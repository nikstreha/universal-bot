package local.storage

import android.app.Application
import com.facebook.react.PackageList
import com.facebook.react.ReactApplication
import com.facebook.react.ReactHost
import com.facebook.react.ReactNativeApplicationEntryPoint.loadReactNative
import com.facebook.react.defaults.DefaultReactHost.getDefaultReactHost
import com.facebook.react.modules.network.OkHttpClientFactory
import com.facebook.react.modules.network.OkHttpClientProvider
import com.facebook.react.shell.MainPackageConfig
import com.facebook.react.shell.MainReactPackage
import local.storage.security.SecureNetwork

class MainApplication : Application(), ReactApplication {
    override val reactHost: ReactHost by lazy {
        getDefaultReactHost(
            context = applicationContext,
            packageList = PackageList(this).packages.apply {
                removeAll { it is MainReactPackage }
                add(MainReactPackage(MainPackageConfig(SecureNetwork.images(applicationContext))))
                add(StoragePackage())
            },
            useDevSupport = BuildConfig.DEBUG,
        )
    }
    override fun onCreate() {
        super.onCreate()
        OkHttpClientProvider.setOkHttpClientFactory(OkHttpClientFactory { SecureNetwork.client(this) })
        loadReactNative(this)
    }
}
