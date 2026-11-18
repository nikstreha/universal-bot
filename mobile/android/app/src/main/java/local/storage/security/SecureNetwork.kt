package local.storage.security

import android.content.Context
import com.facebook.imagepipeline.backends.okhttp3.OkHttpImagePipelineConfigFactory
import com.facebook.imagepipeline.core.ImagePipelineConfig
import com.facebook.react.modules.network.OkHttpClientProvider
import local.storage.transfer.SecureStore
import okhttp3.OkHttpClient
import java.io.IOException
import java.net.URI

/** Shared by JS API calls, Fresco and video. Redirects never forward credentials. */
object SecureNetwork {
    @Volatile private var instance: OkHttpClient? = null

    @Synchronized fun client(context: Context): OkHttpClient {
        instance?.let { return it }
        val store = SecureStore(context.applicationContext)
        return OkHttpClientProvider.createClientBuilder()
            .followRedirects(false)
            .followSslRedirects(false)
            .cache(null)
            .addInterceptor { chain ->
                var request = chain.request()
                val url = request.url
                try {
                    val origin = ServerPolicy.base(URI(url.scheme, null, url.host, url.port, null, null, null).toASCIIString())
                    require(request.header("Authorization") == null)
                    if (url.encodedPath.startsWith("/api/v1/files/")) {
                        val session = store.read("session") ?: throw IOException("Session is no longer active")
                        require(origin == ServerPolicy.base(session.getString("baseUrl")))
                        ServerPolicy.media(url.toString(),session.getString("baseUrl"))
                        request = request.newBuilder().header("Authorization","Bearer ${session.getString("token")}")
                            .removeHeader("Cookie").build()
                    }
                } catch (_: Exception) {
                    throw IOException("Untrusted server origin or credentials")
                }
                val response = chain.proceed(request)
                if (response.code in 300..399) {
                    response.close()
                    throw IOException("Server redirects are forbidden")
                }
                response
            }
            .build().also { instance = it }
    }

    fun images(context: Context): ImagePipelineConfig =
        OkHttpImagePipelineConfigFactory.newBuilder(context, client(context))
            .setDiskCacheEnabled(false)
            .build()

    fun cancel() { instance?.dispatcher?.cancelAll() }
}
