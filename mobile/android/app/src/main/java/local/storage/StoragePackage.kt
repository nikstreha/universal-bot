package local.storage

import android.net.Uri
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.okhttp.OkHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.ui.PlayerView
import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReadableMap
import com.facebook.react.uimanager.SimpleViewManager
import com.facebook.react.uimanager.ThemedReactContext
import com.facebook.react.uimanager.ViewManager
import com.facebook.react.uimanager.annotations.ReactProp
import local.storage.security.SecureNetwork
import local.storage.security.ServerPolicy
import local.storage.transfer.SecureStore
import local.storage.media.MediaGridManager

class StoragePackage:ReactPackage {
    override fun createNativeModules(context:ReactApplicationContext):List<NativeModule> = listOf(StorageBridge(context))
    override fun createViewManagers(context:ReactApplicationContext):List<ViewManager<*,*>> = listOf(StorageVideoManager(),MediaGridManager())
}

@UnstableApi
class StorageVideoManager:SimpleViewManager<PlayerView>() {
    override fun getName()="StorageVideo"
    override fun createViewInstance(context:ThemedReactContext)=PlayerView(context)
    @ReactProp(name="source") fun source(view:PlayerView,source:ReadableMap?) {
        view.player?.release(); view.player=null
        if(source==null)return
        val session=SecureStore(view.context).read("session")?:return
        val uri=ServerPolicy.media(requireNotNull(source.getString("uri")),session.getString("baseUrl"))
        // The shared native interceptor adds Authorization after checking the origin.
        val data=OkHttpDataSource.Factory(SecureNetwork.client(view.context))
        view.player=ExoPlayer.Builder(view.context)
            .setMediaSourceFactory(DefaultMediaSourceFactory(data)).build().apply {
                setMediaItem(MediaItem.fromUri(Uri.parse(uri)))
                prepare()
            }
    }
    override fun onDropViewInstance(view:PlayerView) { view.player?.release();view.player=null;super.onDropViewInstance(view) }
}
