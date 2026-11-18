package local.storage.media

import android.graphics.Color
import android.graphics.RectF
import android.graphics.Typeface
import android.graphics.drawable.Animatable
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.Log
import android.view.GestureDetector
import android.view.Gravity
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.View
import android.view.ViewGroup
import android.view.animation.DecelerateInterpolator
import android.widget.FrameLayout
import android.widget.TextView
import androidx.core.view.doOnPreDraw
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.facebook.drawee.backends.pipeline.Fresco
import com.facebook.drawee.controller.BaseControllerListener
import com.facebook.drawee.drawable.ScalingUtils
import com.facebook.drawee.view.SimpleDraweeView
import com.facebook.imagepipeline.common.ResizeOptions
import com.facebook.imagepipeline.image.ImageInfo
import com.facebook.imagepipeline.request.ImageRequestBuilder
import com.facebook.react.bridge.Arguments
import com.facebook.react.bridge.ReadableArray
import com.facebook.react.bridge.ReadableMap
import com.facebook.react.bridge.WritableMap
import com.facebook.react.uimanager.SimpleViewManager
import com.facebook.react.uimanager.ThemedReactContext
import com.facebook.react.uimanager.UIManagerHelper
import com.facebook.react.uimanager.annotations.ReactProp
import com.facebook.react.uimanager.events.Event
import local.storage.security.SecureNetwork
import local.storage.security.ServerPolicy
import local.storage.transfer.SecureStore
import local.storage.BuildConfig
import kotlin.math.roundToInt
import java.util.concurrent.Executors

private data class GridItem(val id:String,val label:String,val uri:String?,val video:Boolean,val heading:Boolean)
private class GridEvent(surface:Int,tag:Int,private val name:String,private val payload:WritableMap):Event<GridEvent>(surface,tag) {
    override fun getEventName()=name
    override fun getEventData()=payload
    override fun canCoalesce()=false
}

/** One UI-thread implementation for the server gallery and local media selection. */
class MediaGridView(private val react:ThemedReactContext):FrameLayout(react) {
    private val main=Handler(Looper.getMainLooper())
    private val recycler=RecyclerView(react)
    private val swipe=SwipeRefreshLayout(react)
    private val layout=GridLayoutManager(react,3)
    private val adapter=GridAdapter()
    private var items=emptyList<GridItem>()
    private var selected=linkedSetOf<String>()
    private var selectable=false
    private var selectionAvailable=false
    private var selectionLocked=false
    private var hasMore=false
    private var requestedCount=-1
    private var pendingAnchor:Pair<String,Int>?=null
    private var anchorApplied=false
    private var catalogKey:String?=null
    private var ink=Color.WHITE
    private var surface=Color.DKGRAY
    private var accent=Color.rgb(255,145,56)
    private var buttonInk=Color.BLACK
    private var intercepting=false
    private var pinching=false
    private var cancelled=false
    private var preview=1f
    private var startingColumns=3
    private var focusX=0f
    private var focusY=0f
    private var dragging=false
    private var dragStart=-1
    private var dragLast=-1
    private var dragAdding=true
    private var dragBase=linkedSetOf<String>()
    private var dragX=0f
    private var dragY=0f
    private var lastEmission=0L
    private var decodedImages=0
    private var relayoutQueued=false
    private val dataExecutor=Executors.newSingleThreadExecutor()
    @Volatile private var dataGeneration=0L
    @Volatile private var disposed=false

    // React Native positions this outer view itself. Requests from RecyclerView
    // still need a native measure/layout pass for its own descendants.
    private fun scheduleNativeLayout() {
        if(relayoutQueued)return
        relayoutQueued=true
        postOnAnimation {
            relayoutQueued=false
            if(disposed)return@postOnAnimation
            if(width>0 && height>0) {
                measure(MeasureSpec.makeMeasureSpec(width,MeasureSpec.EXACTLY),MeasureSpec.makeMeasureSpec(height,MeasureSpec.EXACTLY))
                layout(left,top,right,bottom)
            }
        }
    }

    private fun dp(value:Int)=(value*resources.displayMetrics.density).roundToInt()
    private fun emit(name:String,data:WritableMap=Arguments.createMap()) {
        if(id==View.NO_ID || !isAttachedToWindow)return
        UIManagerHelper.getEventDispatcherForReactTag(react,id)?.dispatchEvent(GridEvent(UIManagerHelper.getSurfaceId(this),id,name,data))
    }
    private fun emitSelection(force:Boolean=false) {
        if(!force && SystemClock.uptimeMillis()-lastEmission<100)return
        lastEmission=SystemClock.uptimeMillis()
        emit("topSelectionChange",Arguments.createMap().apply {
            putArray("ids",Arguments.createArray().apply { selected.forEach { pushString(it) } })
        })
    }
    private fun childPosition(x:Float,y:Float):Int = recycler.findChildViewUnder(x,y)?.let { recycler.getChildAdapterPosition(it) } ?: RecyclerView.NO_POSITION
    private fun savePosition() {
        val position=layout.findFirstVisibleItemPosition()
        val item=items.getOrNull(position)?:return
        val top=layout.findViewByPosition(position)?.top?:0
        emit("topPositionChange",Arguments.createMap().apply { putString("id",item.id);putDouble("offset",top/resources.displayMetrics.density.toDouble()) })
    }
    private fun restorePosition() {
        if(anchorApplied)return
        val anchor=pendingAnchor?:return
        val position=items.indexOfFirst { it.id==anchor.first }
        if(position>=0){layout.scrollToPositionWithOffset(position,anchor.second);anchorApplied=true}
    }
    private fun claim(event:MotionEvent) {
        if(intercepting)return
        intercepting=true;recycler.stopScroll();swipe.isEnabled=false
        parent?.requestDisallowInterceptTouchEvent(true)
        val cancel=MotionEvent.obtain(event);cancel.action=MotionEvent.ACTION_CANCEL
        super.dispatchTouchEvent(cancel);cancel.recycle()
    }
    private val scale=ScaleGestureDetector(react,object:ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScaleBegin(detector:ScaleGestureDetector):Boolean {
            if(width==0)return false
            if(dragging){dragging=false;emitSelection(true)}
            pinching=true;startingColumns=layout.spanCount;preview=1f
            focusX=detector.focusX;focusY=detector.focusY
            return true
        }
        override fun onScale(detector:ScaleGestureDetector):Boolean {
            preview=(preview*detector.scaleFactor).coerceIn(startingColumns/6f,startingColumns/2f)
            recycler.pivotX=focusX;recycler.pivotY=focusY
            recycler.scaleX=preview;recycler.scaleY=preview
            return true
        }
        override fun onScaleEnd(detector:ScaleGestureDetector) {
            val target=if(cancelled)startingColumns else (startingColumns/preview).roundToInt().coerceIn(2,6)
            pinching=false;changeColumns(target,focusX,focusY)
        }
    })
    private val detector=GestureDetector(react,object:GestureDetector.SimpleOnGestureListener() {
        override fun onDown(event:MotionEvent)=true
        override fun onLongPress(event:MotionEvent) {
            if(selectionLocked || (!selectable && !selectionAvailable) || pinching)return
            val position=childPosition(event.x,event.y)
            if(position !in items.indices || items[position].heading)return
            selectable=true
            claim(event);dragging=true;dragStart=position;dragLast=-1
            dragX=event.x;dragY=event.y;dragBase=LinkedHashSet(selected)
            dragAdding=items[position].id !in selected
            selectRange(position);main.post(autoScroll)
        }
    })
    private fun selectRange(position:Int) {
        if(position !in items.indices || position==dragLast)return
        dragLast=position
        val next=LinkedHashSet(dragBase)
        for(index in minOf(dragStart,position)..maxOf(dragStart,position)) {
            val item=items[index];if(item.heading)continue
            if(!dragAdding)next.remove(item.id) else if(next.size<1000)next.add(item.id)
        }
        selected=next;updateVisibleSelection();emitSelection()
    }
    private val autoScroll=object:Runnable {
        override fun run() {
            if(!dragging)return
            val edge=dp(56)
            val speed=when { dragY<edge -> -dp(10);dragY>height-edge -> dp(10);else -> 0 }
            if(speed!=0) {
                recycler.scrollBy(0,speed)
                val y=dragY.coerceIn(1f,(height-1).toFloat())
                val position=childPosition(dragX.coerceIn(1f,(width-1).toFloat()),y)
                if(position!=RecyclerView.NO_POSITION)selectRange(position)
            }
            main.postDelayed(this,16)
        }
    }
    init {
        if(!Fresco.hasBeenInitialized())Fresco.initialize(react.applicationContext,SecureNetwork.images(react))
        recycler.layoutManager=layout;recycler.adapter=adapter
        recycler.itemAnimator=null;recycler.setHasFixedSize(true)
        recycler.setItemViewCacheSize(24)
        recycler.recycledViewPool.setMaxRecycledViews(0,36)
        recycler.overScrollMode=View.OVER_SCROLL_NEVER
        layout.spanSizeLookup=object:GridLayoutManager.SpanSizeLookup() {
            override fun getSpanSize(position:Int)=if(items.getOrNull(position)?.heading==true)layout.spanCount else 1
        }
        recycler.addOnScrollListener(object:RecyclerView.OnScrollListener() {
            override fun onScrollStateChanged(view:RecyclerView,state:Int) {
                if(state==RecyclerView.SCROLL_STATE_IDLE) {
                    savePosition()
                    for(i in 0 until recycler.childCount) {
                        val holder=recycler.getChildViewHolder(recycler.getChildAt(i))
                        if(holder is TileHolder)loadTile(holder)
                    }
                }
            }
            override fun onScrolled(view:RecyclerView,dx:Int,dy:Int) {
                if(hasMore && layout.findLastVisibleItemPosition()>=items.size-24 && requestedCount!=items.size) {
                    requestedCount=items.size;emit("topLoadMore")
                }
            }
        })
        swipe.addView(recycler,ViewGroup.LayoutParams(-1,-1))
        swipe.setOnRefreshListener { emit("topRefresh") }
        addView(swipe,LayoutParams(-1,-1))
    }
    override fun dispatchTouchEvent(event:MotionEvent):Boolean {
        if(event.actionMasked==MotionEvent.ACTION_DOWN)anchorApplied=true
        cancelled=event.actionMasked==MotionEvent.ACTION_CANCEL
        scale.onTouchEvent(event);detector.onTouchEvent(event)
        if(pinching)claim(event)
        if(!intercepting)return super.dispatchTouchEvent(event)
        if(dragging && event.actionMasked==MotionEvent.ACTION_MOVE) {
            dragX=event.x;dragY=event.y
            selectRange(childPosition(dragX,dragY))
        }
        if(event.actionMasked==MotionEvent.ACTION_UP || cancelled) {
            if(dragging)emitSelection(true)
            dragging=false;main.removeCallbacks(autoScroll);intercepting=false;swipe.isEnabled=true
            savePosition()
            parent?.requestDisallowInterceptTouchEvent(false)
        }
        return true
    }
    fun setColumns(value:Int) {
        val next=value.coerceIn(2,6)
        if(next!=layout.spanCount && !pinching)changeColumns(next,width/2f,height/2f)
    }
    private fun changeColumns(next:Int,x:Float,y:Float) {
        val previous=layout.spanCount
        val old=mutableMapOf<String,RectF>()
        for(i in 0 until recycler.childCount) {
            val child=recycler.getChildAt(i)
            val item=items.getOrNull(recycler.getChildAdapterPosition(child))?:continue
            child.animate().cancel()
            old[item.id]=RectF(
                recycler.pivotX+(child.x-recycler.pivotX)*recycler.scaleX,
                recycler.pivotY+(child.y-recycler.pivotY)*recycler.scaleY,
                recycler.pivotX+(child.x+child.width*child.scaleX-recycler.pivotX)*recycler.scaleX,
                recycler.pivotY+(child.y+child.height*child.scaleY-recycler.pivotY)*recycler.scaleY,
            )
        }
        val anchor=childPosition(x,y).takeIf { it!=RecyclerView.NO_POSITION } ?: layout.findFirstVisibleItemPosition()
        val anchorChild=recycler.findViewHolderForAdapterPosition(anchor)?.itemView
        val fraction=anchorChild?.let { ((y-it.top)/it.height.coerceAtLeast(1)).coerceIn(0f,1f) } ?: 0f
        recycler.scaleX=1f;recycler.scaleY=1f;preview=1f
        if(next!=previous) {
            layout.spanCount=next
            adapter.notifyItemRangeChanged(0,items.size,"size")
            if(anchor>=0)layout.scrollToPositionWithOffset(anchor,(y-width/next*fraction).roundToInt())
            emit("topColumnsChange",Arguments.createMap().apply { putInt("columns",next) })
        }
        recycler.doOnPreDraw {
            for(i in 0 until recycler.childCount) {
                val child=recycler.getChildAt(i)
                val item=items.getOrNull(recycler.getChildAdapterPosition(child))?:continue
                val bounds=old[item.id]
                child.pivotX=0f;child.pivotY=0f
                if(bounds!=null && child.width>0 && child.height>0) {
                    child.translationX=bounds.left-child.left;child.translationY=bounds.top-child.top
                    child.scaleX=bounds.width()/child.width;child.scaleY=bounds.height()/child.height
                } else child.alpha=0f
                child.animate().translationX(0f).translationY(0f).scaleX(1f).scaleY(1f).alpha(1f)
                    .setDuration(200).setInterpolator(DecelerateInterpolator()).start()
            }
            savePosition()
        }
        recycler.requestLayout();scheduleNativeLayout()
    }
    fun setItems(values:ReadableArray?) {
        if(disposed)return
        val generation=++dataGeneration
        val before=items
        dataExecutor.execute {
        if(disposed || generation!=dataGeneration)return@execute
        val session=SecureStore(react).read("session")
        val next=buildList {
            if(session==null || values==null)return@buildList
            for(index in 0 until values.size()) {
                val value=values.getMap(index)?:continue
                val key=value.getString("id")?:continue
                val heading=value.hasKey("heading") && value.getBoolean("heading")
                val uri=if(value.hasKey("uri"))value.getString("uri") else null
                if(!heading) {
                    if(uri==null)continue
                    val parsed=Uri.parse(uri)
                    if(parsed.scheme=="content") {
                        if(parsed.authority!="media" || parsed.query!=null || parsed.fragment!=null)continue
                    } else try { ServerPolicy.media(uri,session.getString("baseUrl")) } catch (_:Exception) { continue }
                }
                add(GridItem(key,value.getString("label")?:"",uri,value.hasKey("video") && value.getBoolean("video"),heading))
            }
        }
        if(before==next)return@execute
        val result=DiffUtil.calculateDiff(object:DiffUtil.Callback() {
            override fun getOldListSize()=before.size
            override fun getNewListSize()=next.size
            override fun areItemsTheSame(old:Int,new:Int)=before[old].id==next[new].id
            override fun areContentsTheSame(old:Int,new:Int)=before[old]==next[new]
        })
        main.post {
            if(disposed || generation!=dataGeneration)return@post
            items=next;result.dispatchUpdatesTo(adapter);restorePosition();scheduleNativeLayout()
        }
        }
    }
    fun dispose() { disposed=true;dataGeneration++;dataExecutor.shutdownNow();main.removeCallbacks(autoScroll) }

    fun setSelected(values:ReadableArray?) {
        if(dragging)return
        selected=linkedSetOf<String>().apply { if(values!=null)for(i in 0 until minOf(values.size(),1000))values.getString(i)?.let { add(it) } }
        updateVisibleSelection()
    }
    fun setSelectable(value:Boolean) { selectable=value;updateVisibleSelection() }
    fun setSelectionAvailable(value:Boolean) { selectionAvailable=value }
    fun setSelectionLocked(value:Boolean) { selectionLocked=value }
    fun setMore(value:Boolean) { hasMore=value }
    fun setAnchor(value:ReadableMap?) {
        if(value==null)return
        pendingAnchor=value.getString("id")?.let { it to (value.getDouble("offset")*resources.displayMetrics.density).roundToInt() }
        restorePosition()
    }
    fun setCatalog(value:String?) {
        if(catalogKey==value)return
        val previous=catalogKey;catalogKey=value
        if(previous!=null){anchorApplied=true;pendingAnchor=null;layout.scrollToPositionWithOffset(0,0);requestedCount=-1}
    }
    fun setRefreshing(value:Boolean) { swipe.isRefreshing=value;if(!value)requestedCount=-1 }
    fun setPalette(value:ReadableMap?) {
        if(value==null)return
        ink=Color.parseColor(value.getString("ink"));surface=Color.parseColor(value.getString("surface"))
        accent=Color.parseColor(value.getString("accent"));buttonInk=Color.parseColor(value.getString("buttonInk"))
        swipe.setColorSchemeColors(accent);swipe.setProgressBackgroundColorSchemeColor(surface)
        adapter.notifyItemRangeChanged(0,items.size,"palette")
    }
    private fun updateVisibleSelection() {
        for(i in 0 until recycler.childCount) {
            val child=recycler.getChildAt(i)
            val holder=recycler.getChildViewHolder(child)
            if(holder is TileHolder)holder.mark()
        }
    }
    private inner class TileHolder(val tile:FrameLayout):RecyclerView.ViewHolder(tile) {
        val image=SimpleDraweeView(react)
        val check=TextView(react)
        val video=TextView(react)
        val failure=TextView(react)
        var boundId:String?=null
        var requestedUri:String?=null
        var requestedSize=0
        var loaded=false
        private val marker=GradientDrawable().apply { shape=GradientDrawable.OVAL }
        private val outline=GradientDrawable().apply { setColor(Color.TRANSPARENT) }
        init {
            image.hierarchy.setActualImageScaleType(ScalingUtils.ScaleType.CENTER_CROP)
            tile.addView(image,FrameLayout.LayoutParams(-1,-1))
            failure.text="!";failure.textSize=24f;failure.gravity=Gravity.CENTER;failure.setTextColor(Color.WHITE);failure.visibility=View.GONE
            tile.addView(failure,FrameLayout.LayoutParams(-1,-1))
            check.gravity=Gravity.CENTER;check.textSize=14f;check.text="✓";check.background=marker
            tile.addView(check,FrameLayout.LayoutParams(dp(24),dp(24),Gravity.TOP or Gravity.END).apply { setMargins(dp(6),dp(6),dp(6),dp(6)) })
            video.text="▷";video.textSize=18f;video.setTextColor(Color.WHITE)
            tile.addView(video,FrameLayout.LayoutParams(dp(28),dp(28),Gravity.BOTTOM or Gravity.START).apply { leftMargin=dp(6) })
            tile.setOnClickListener {
                if(selectionLocked)return@setOnClickListener
                val item=items.getOrNull(bindingAdapterPosition)?:return@setOnClickListener
                if(selectable) {
                    if(item.id in selected)selected.remove(item.id) else if(selected.size<1000)selected.add(item.id)
                    mark();emitSelection(true)
                } else { savePosition();emit("topOpen",Arguments.createMap().apply { putString("id",item.id) }) }
            }
        }
        fun mark() {
            val item=items.getOrNull(bindingAdapterPosition)?:return
            val checked=item.id in selected
            check.visibility=if(selectable)View.VISIBLE else View.INVISIBLE
            check.setTextColor(if(checked)buttonInk else Color.TRANSPARENT)
            marker.setColor(if(checked)accent else 0x66000000);marker.setStroke(dp(1),if(checked)accent else Color.WHITE)
            outline.setStroke(dp(3),accent);tile.foreground=if(checked)outline else null
            tile.isSelected=checked
        }
    }
    private fun loadTile(holder:TileHolder) {
        val item=items.getOrNull(holder.bindingAdapterPosition)?:return
        val side=((recycler.width.takeIf { it>0 }?:resources.displayMetrics.widthPixels)/layout.spanCount).coerceAtLeast(1)
        if(holder.requestedUri==item.uri && holder.requestedSize==side)return
        holder.requestedUri=item.uri;holder.requestedSize=side;holder.loaded=false
        holder.failure.visibility=View.GONE;holder.tile.contentDescription="Загрузка миниатюры. ${item.label}"
        val request=ImageRequestBuilder.newBuilderWithSource(Uri.parse(item.uri)).setResizeOptions(ResizeOptions(side,side)).build()
                holder.image.controller=Fresco.newDraweeControllerBuilder().setOldController(holder.image.controller).setImageRequest(request)
                    .setControllerListener(object:BaseControllerListener<ImageInfo>() {
                        override fun onFailure(id:String?,error:Throwable) {
                            if(holder.boundId!=item.id)return
                            holder.failure.visibility=View.VISIBLE
                            holder.tile.contentDescription="Миниатюра недоступна. ${item.label}"
                            Log.w("StorageMediaGrid","Thumbnail load failed: ${error.javaClass.simpleName}")
                        }
                        override fun onFinalImageSet(id:String?,info:ImageInfo?,animatable:Animatable?) {
                            if(holder.boundId!=item.id)return
                            holder.loaded=true;holder.failure.visibility=View.GONE;holder.tile.contentDescription=item.label
                            if(BuildConfig.DEBUG && decodedImages++<8)Log.d("StorageMediaGrid","Thumbnail decoded: ${info?.width}x${info?.height}")
                        }
                    }).build()
    }
    private inner class GridAdapter:RecyclerView.Adapter<RecyclerView.ViewHolder>() {
        private val ids=mutableMapOf<String,Long>()
        private var nextId=0L
        init { setHasStableIds(true) }
        override fun getItemId(position:Int)=ids.getOrPut(items[position].id) { ++nextId }
        override fun getItemCount()=items.size
        override fun getItemViewType(position:Int)=if(items[position].heading)1 else 0
        override fun onCreateViewHolder(parent:ViewGroup,type:Int):RecyclerView.ViewHolder =
            if(type==1)object:RecyclerView.ViewHolder(TextView(react).apply { gravity=Gravity.CENTER_VERTICAL;textSize=15f;setTypeface(null,Typeface.BOLD);setPadding(dp(16),0,dp(16),0) }){} else TileHolder(FrameLayout(react))
        override fun onBindViewHolder(holder:RecyclerView.ViewHolder,position:Int) {
            val item=items[position]
            if(holder is TileHolder) {
                val side=((recycler.width.takeIf { it>0 }?:resources.displayMetrics.widthPixels)/layout.spanCount).coerceAtLeast(1)
                val height=(side-dp(2)).coerceAtLeast(1)
                if(holder.tile.layoutParams?.height!=height)holder.tile.layoutParams=RecyclerView.LayoutParams(-1,height).apply { setMargins(dp(1),dp(1),dp(1),dp(1)) }
                holder.boundId=item.id
                holder.tile.setBackgroundColor(surface)
                holder.tile.contentDescription=if(holder.loaded&&holder.requestedUri==item.uri)item.label else "Загрузка миниатюры. ${item.label}"
                holder.video.visibility=if(item.video)View.VISIBLE else View.GONE
                if(recycler.scrollState!=RecyclerView.SCROLL_STATE_SETTLING)loadTile(holder)
                else if(holder.requestedUri!=item.uri) {
                    holder.image.controller=null;holder.requestedUri=null;holder.loaded=false
                }
                holder.mark()
            } else {
                (holder.itemView as TextView).apply { text=item.label;setTextColor(ink);layoutParams=RecyclerView.LayoutParams(-1,dp(40)) }
            }
        }
    }
    override fun onDetachedFromWindow() { main.removeCallbacks(autoScroll);super.onDetachedFromWindow() }
}

class MediaGridManager:SimpleViewManager<MediaGridView>() {
    override fun getName()="StorageMediaGrid"
    override fun createViewInstance(context:ThemedReactContext)=MediaGridView(context)
    override fun onDropViewInstance(view:MediaGridView) { view.dispose();super.onDropViewInstance(view) }
    @ReactProp(name="items") fun items(view:MediaGridView,value:ReadableArray?)=view.setItems(value)
    @ReactProp(name="selectedIds") fun selected(view:MediaGridView,value:ReadableArray?)=view.setSelected(value)
    @ReactProp(name="columns",defaultInt=3) fun columns(view:MediaGridView,value:Int)=view.setColumns(value)
    @ReactProp(name="selectionAvailable") fun selectionAvailable(view:MediaGridView,value:Boolean)=view.setSelectionAvailable(value)
    @ReactProp(name="selectionLocked") fun selectionLocked(view:MediaGridView,value:Boolean)=view.setSelectionLocked(value)
    @ReactProp(name="selectable") fun selectable(view:MediaGridView,value:Boolean)=view.setSelectable(value)
    @ReactProp(name="hasMore") fun more(view:MediaGridView,value:Boolean)=view.setMore(value)
    @ReactProp(name="refreshing") fun refreshing(view:MediaGridView,value:Boolean)=view.setRefreshing(value)
    @ReactProp(name="palette") fun palette(view:MediaGridView,value:ReadableMap?)=view.setPalette(value)
    @ReactProp(name="anchor") fun anchor(view:MediaGridView,value:ReadableMap?)=view.setAnchor(value)
    @ReactProp(name="catalogKey") fun catalog(view:MediaGridView,value:String?)=view.setCatalog(value)
    override fun getExportedCustomDirectEventTypeConstants():Map<String,Any> = listOf("Open","SelectionChange","ColumnsChange","LoadMore","Refresh","PositionChange").associate { "top$it" to mapOf("registrationName" to "on$it") }
}
