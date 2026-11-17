package local.storage

import android.net.Uri
import android.widget.MediaController
import android.widget.VideoView
import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReadableMap
import com.facebook.react.uimanager.SimpleViewManager
import com.facebook.react.uimanager.ThemedReactContext
import com.facebook.react.uimanager.ViewManager
import com.facebook.react.uimanager.annotations.ReactProp

class StoragePackage:ReactPackage {
    override fun createNativeModules(context:ReactApplicationContext):List<NativeModule> = listOf(StorageBridge(context))
    override fun createViewManagers(context:ReactApplicationContext):List<ViewManager<*,*>> = listOf(StorageVideoManager())
}

class StorageVideoManager:SimpleViewManager<VideoView>() {
    override fun getName()="StorageVideo"
    override fun createViewInstance(context:ThemedReactContext)=VideoView(context).apply {
        val controller=MediaController(context);controller.setAnchorView(this);setMediaController(controller)
        setOnPreparedListener { it.isLooping=false;seekTo(1) }
    }
    @ReactProp(name="source") fun source(view:VideoView,source:ReadableMap?) {
        if(source==null)return
        val headers=source.getMap("headers")?.toHashMap()?.mapValues { it.value.toString() }?:emptyMap()
        view.setVideoURI(Uri.parse(source.getString("uri")),headers)
    }
    override fun onDropViewInstance(view:VideoView) { view.stopPlayback();super.onDropViewInstance(view) }
}
