package local.storage

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.provider.DocumentsContract
import android.provider.MediaStore
import android.provider.OpenableColumns
import android.provider.Settings
import android.util.Base64
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.facebook.react.bridge.*
import local.storage.transfer.*
import org.json.JSONArray
import org.json.JSONObject
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.UUID
import java.util.concurrent.Executors

class StorageBridge(private val context:ReactApplicationContext):ReactContextBaseJavaModule(context),LifecycleEventListener {
    companion object { @Volatile var instance:StorageBridge?=null }
    private val executor=Executors.newSingleThreadExecutor()
    private val preferences=context.getSharedPreferences("preferences",0)
    private val secure=SecureStore(context)
    private val db=TransferDatabase(context)
    private var picker:Promise?=null
    private var deleting:String?=null
    init {
        instance=this;context.addLifecycleEventListener(this)
        context.addActivityEventListener(object:BaseActivityEventListener() {
            override fun onActivityResult(activity:Activity,request:Int,result:Int,data:Intent?) {
                if(request==6101) {
                    val promise=picker;picker=null
                    if(result!=Activity.RESULT_OK || data==null) { promise?.resolve("[]");return }
                    executor.execute {
                        try {
                            val output=JSONArray()
                            val uris=if(data.clipData!=null)(0 until data.clipData!!.itemCount).map { data.clipData!!.getItemAt(it).uri } else listOfNotNull(data.data)
                            for(uri in uris) {
                                try { context.contentResolver.takePersistableUriPermission(uri,data.flags and (Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)) } catch (_:SecurityException) { }
                                val mime=context.contentResolver.getType(uri)?:"application/octet-stream"
                                var name=uri.lastPathSegment?:"file";var size=0L
                                context.contentResolver.query(uri,arrayOf(OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE),null,null,null)?.use {
                                    if(it.moveToFirst()) { name=it.getString(0);if(!it.isNull(1))size=it.getLong(1) }
                                }
                                output.put(JSONObject().put("uri",uri.toString()).put("name",name).put("size",size).put("mime",mime))
                            }
                            promise?.resolve(output.toString())
                        } catch(error:Exception) { promise?.reject("PICK_FAILED","Не удалось прочитать выбранные файлы",error) }
                    }
                } else if(request==6102) {
                    deleting?.let { db.patch(it,if(result==Activity.RESULT_OK)"done" else "kept_local") }
                    deleting=null;TransferScheduler.kick(context)
                }
            }
        })
    }
    override fun getName()="StorageBridge"
    private fun async(promise:Promise,block:()->Any?) { executor.execute { try { promise.resolve(block()?.toString()?:"null") } catch(error:Exception) { promise.reject(if(error is ApiException)error.code else "STORAGE_ERROR",error.message,error) } } }
    private fun credentials()=secure.read("session")?:throw IllegalStateException("Войдите через Telegram")
    private fun api():Api { val s=credentials();return Api(s.getString("baseUrl"),s.getString("token")) }
    @ReactMethod fun getSession(promise:Promise)=async(promise) { secure.read("session") }
    @ReactMethod fun preferences(promise:Promise)=async(promise) { JSONObject().put("theme",preferences.getString("theme","system")).put("columns",preferences.getString("columns","3")!!.toInt()).put("baseUrl",preferences.getString("baseUrl",BuildConfig.SERVER_URL)) }
    @ReactMethod fun preference(key:String,value:String) { if(key in setOf("theme","columns"))preferences.edit().putString(key,value).apply() }
    @ReactMethod fun beginLogin(baseUrl:String,promise:Promise)=async(promise) {
        val uri=Uri.parse(baseUrl.trimEnd('/'))
        require(uri.scheme=="https" || BuildConfig.DEBUG && uri.scheme=="http") { "Используйте HTTPS-адрес сервера" }
        require(!uri.host.isNullOrBlank() && uri.userInfo==null && uri.query==null && uri.fragment==null) { "Неверный адрес сервера" }
        val random=ByteArray(32).also { SecureRandom().nextBytes(it) }
        val verifier=Base64.encodeToString(random,Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val challenge=Base64.encodeToString(MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray()),Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        var installation=preferences.getString("installation",null)
        if(installation==null) { installation=UUID.randomUUID().toString();preferences.edit().putString("installation",installation).commit() }
        val response=Api(baseUrl).request("/auth/telegram/attempts","POST",JSONObject().put("code_challenge",challenge).put("installation_id",installation).put("device_name","Android"))
        secure.write("attempt",JSONObject().put("attempt_id",response.getString("attempt_id")).put("code_verifier",verifier).put("baseUrl",baseUrl.trimEnd('/')))
        preferences.edit().putString("baseUrl",baseUrl.trimEnd('/')).apply()
        response
    }
    @ReactMethod fun pollLogin(promise:Promise)=async(promise) {
        val attempt=secure.read("attempt")?:return@async JSONObject().put("state","none")
        try {
            val result=Api(attempt.getString("baseUrl")).request("/auth/telegram/attempts/${attempt.getString("attempt_id")}/exchange","POST",JSONObject().put("code_verifier",attempt.getString("code_verifier")))
            if(!result.has("session_token"))return@async result
            val session=JSONObject().put("baseUrl",attempt.getString("baseUrl")).put("token",result.getString("session_token")).put("userId",result.getJSONObject("user").getString("id"))
            secure.write("session",session);secure.write("attempt",null)
            for(row in db.rows(session.getString("userId"),session.getString("baseUrl")))if(row.getString("state")=="waiting_auth")db.patch(row.getString("id"),"queued")
            Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) }
            JSONObject().put("state","authenticated").put("session",session)
        } catch(error:ApiException) {
            if(error.code=="NOT_WHITELISTED")JSONObject().put("state","denied").put("access_request_status",error.details.optString("access_request_status","not_requested")) else throw error
        }
    }
    @ReactMethod fun requestAccess(promise:Promise)=async(promise) {
        val attempt=secure.read("attempt")?:throw IllegalStateException("Войдите через Telegram ещё раз")
        Api(attempt.getString("baseUrl")).request("/access-requests","POST",JSONObject().put("attempt_id",attempt.getString("attempt_id")).put("code_verifier",attempt.getString("code_verifier")))
    }
    @ReactMethod fun logout(promise:Promise)=async(promise) {
        secure.read("session")?.let { session -> db.rows(session.getString("userId"),session.getString("baseUrl")).filter { it.getString("state") in TransferEngine.RUNNABLE }.forEach { db.patch(it.getString("id"),"cancelled") } }
        secure.write("session",null);secure.write("attempt",null);null
    }
    @ReactMethod fun pickFiles(promise:Promise) {
        val activity=currentActivity
        if(activity==null || picker!=null) { promise.reject("PICK_BUSY","Выбор файлов сейчас недоступен");return }
        picker=promise
        val intent=Intent(Intent.ACTION_OPEN_DOCUMENT).setType("*/*").addCategory(Intent.CATEGORY_OPENABLE)
            .putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
        activity.startActivityForResult(intent,6101)
    }
    @ReactMethod fun enqueue(files:ReadableArray,mode:String,promise:Promise)=async(promise) {
        require(mode in setOf("copy","move"))
        val current=credentials();val owner=current.getString("userId")
        val list=files.toArrayList().map { JSONObject(it as Map<*,*>) }
        for(file in list)db.add(file.put("id",UUID.randomUUID().toString()).put("owner_id",owner).put("base_url",current.getString("baseUrl").trimEnd('/')).put("state","queued").put("mode",mode).put("direction","upload").put("progress",0).put("error","").put("file_id",""))
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) };null
    }
    @ReactMethod fun download(file:ReadableMap,promise:Promise)=async(promise) {
        val source=JSONObject(file.toHashMap())
        db.add(JSONObject().put("id",UUID.randomUUID().toString()).put("owner_id",credentials().getString("userId")).put("base_url",credentials().getString("baseUrl").trimEnd('/')).put("name",source.getString("original_name")).put("size",source.getLong("size_bytes")).put("sha256",source.getString("sha256")).put("mime",source.getString("mime_type")).put("file_id",source.getString("id")).put("state","queued").put("mode","copy").put("direction","download").put("progress",0).put("error",""))
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) };null
    }
    @ReactMethod fun transfers(promise:Promise)=async(promise) { credentials().let { JSONArray(db.rows(it.getString("userId"),it.getString("baseUrl"))) } }
    @ReactMethod fun action(id:String,action:String,promise:Promise)=async(promise) {
        val row=db.get(id)?:return@async null
        require(belongsToSession(row))
        require(row.getString("state")!="deleting") { "Android уже выполняет удаление" }
        when(action) {
            "pause"->db.patch(id,"paused")
            "resume"->db.patch(id,"queued")
            "cancel"->{db.patch(id,"cancelled");if(row.optString("upload_id").isNotBlank())try { api().request("/uploads/${row.getString("upload_id")}","DELETE") } catch (_:Exception) { }}
        }
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) };null
    }
    @ReactMethod fun canManageMedia(promise:Promise)=async(promise) { MediaStore.canManageMedia(context) }
    @ReactMethod fun requestManageMedia(promise:Promise) {
        val activity=currentActivity
        if(activity==null) { promise.reject("NO_ACTIVITY","Откройте приложение");return }
        activity.startActivity(Intent(Settings.ACTION_REQUEST_MANAGE_MEDIA,Uri.parse("package:${context.packageName}")))
        promise.resolve("null")
    }
    @ReactMethod fun immersive(enabled:Boolean) {
        currentActivity?.runOnUiThread {
            currentActivity?.let { activity ->
                val controller=WindowCompat.getInsetsController(activity.window,activity.window.decorView)
                controller.systemBarsBehavior=WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                if(enabled)controller.hide(WindowInsetsCompat.Type.systemBars()) else controller.show(WindowInsetsCompat.Type.systemBars())
            }
        }
    }
    private fun belongsToSession(row:JSONObject):Boolean {
        val current=secure.read("session")?:return false
        return row.getString("owner_id")==current.getString("userId") && row.optString("base_url")==current.getString("baseUrl").trimEnd('/')
    }
    fun deleteVerified(row:JSONObject):Boolean {
        if(!belongsToSession(row))return false
        if(currentActivity==null)return false
        val id=row.getString("id")
        if(deleting!=null)return false
        val source=Uri.parse(row.getString("uri"))
        val media=try { MediaStore.getMediaUri(context,source) } catch (_:Exception) { null }
        if(media!=null && !MediaStore.canManageMedia(context)) { db.patch(id,"awaiting_permission");return true }
        if(!db.patch(id,JSONObject().put("state","deleting"),TransferEngine.RUNNABLE))return false
        Handler(Looper.getMainLooper()).post {
            if(!belongsToSession(row) || db.get(id)?.optString("state")!="deleting")return@post
            val activity=currentActivity
            if(activity==null) { db.patch(id,"awaiting_foreground");return@post }
            try {
                if(media!=null) {
                    deleting=id
                    val request=MediaStore.createDeleteRequest(context.contentResolver,listOf(media))
                    activity.startIntentSenderForResult(request.intentSender,6102,null,0,0,0)
                } else if(DocumentsContract.isDocumentUri(context,source)) {
                    val removed=DocumentsContract.deleteDocument(context.contentResolver,source)
                    db.patch(id,if(removed)"done" else "kept_local")
                } else { db.patch(id,"awaiting_permission") }
            } catch (_:SecurityException) { deleting=null;db.patch(id,"awaiting_permission")
            } catch (_:Exception) { deleting=null;db.patch(id,"kept_local") }
        }
        return true
    }
    override fun onHostResume() {
        if(MediaStore.canManageMedia(context))secure.read("session")?.let { session ->
            db.rows(session.getString("userId"),session.getString("baseUrl")).filter { it.getString("state")=="awaiting_permission" }.forEach { db.patch(it.getString("id"),"queued") }
        }
        TransferScheduler.kick(context)
    }
    override fun onHostPause() = Unit
    override fun onHostDestroy() = Unit
    override fun invalidate() { if(instance===this)instance=null;super.invalidate() }
}
