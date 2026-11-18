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
import com.facebook.react.common.LifecycleState
import local.storage.transfer.*
import local.storage.security.ServerPolicy
import local.storage.security.SecureNetwork
import local.storage.media.DeviceMediaCatalog
import com.facebook.drawee.backends.pipeline.Fresco
import java.io.File
import org.json.JSONArray
import org.json.JSONObject
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger

class StorageBridge(private val context:ReactApplicationContext):ReactContextBaseJavaModule(context),LifecycleEventListener {
    companion object {
        @Volatile var instance:StorageBridge?=null
        private val deletionCodes=AtomicInteger(6200)
    }
    private val executor=Executors.newSingleThreadExecutor()
    private val preferences=context.getSharedPreferences("preferences",0)
    private val secure=SecureStore(context)
    private val db=TransferDatabase(context)
    private var picker:Promise?=null
    private var managementPromise:Promise?=null
    private var managementSession:String?=null
    @Volatile private var deleting:String?=null
    private var deletingSession:String?=null
    private var deletingRequest:Int?=null
    private var pickerSession:String?=null
    private val selected=mutableMapOf<String,JSONObject>()
    private fun sameSession(id:String?)=id!=null && secure.read("session")?.optString("localId")==id
    init {
        instance=this;context.addLifecycleEventListener(this)
        executor.execute {
            val current=secure.read("session")
            val active=if(current==null)emptySet() else db.rows(current.getString("userId"),current.getString("baseUrl"))
                .filter { it.optString("purpose")=="share" && it.optString("state") !in setOf("done","cancelled","kept_local") }.map { it.optString("share_batch") }.toSet()
            FileSharing.cleanup(context,active)
        }
        context.addActivityEventListener(object:BaseActivityEventListener() {
            override fun onActivityResult(activity:Activity,request:Int,result:Int,data:Intent?) {
                if(request==6101) {
                    val promise=picker;picker=null
                    val selectionSession=pickerSession;pickerSession=null
                    if(!sameSession(selectionSession) || result!=Activity.RESULT_OK || data==null) { promise?.resolve("[]");return }
                    executor.execute {
                        try {
                            val output=JSONArray()
                            val uris=if(data.clipData!=null)(0 until data.clipData!!.itemCount).map { data.clipData!!.getItemAt(it).uri } else listOfNotNull(data.data)
                            require(uris.size<=1000) { "Выберите не больше 1000 файлов за раз" }
                            for(uri in uris.distinct()) {
                                require(sameSession(selectionSession)) { "Сессия изменилась" }
                                require(uri.scheme=="content" && !uri.authority.isNullOrBlank()) { "Выберите файл через системное окно" }
                                try { context.contentResolver.takePersistableUriPermission(uri,data.flags and (Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)) } catch (_:SecurityException) { }
                                val mime=context.contentResolver.getType(uri)?:"application/octet-stream"
                                var name=uri.lastPathSegment?:"file";var size=0L
                                context.contentResolver.query(uri,arrayOf(OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE),null,null,null)?.use {
                                    if(it.moveToFirst()) { name=it.getString(0);if(!it.isNull(1))size=it.getLong(1) }
                                }
                                val picked=JSONObject().put("uri",uri.toString()).put("name",name.take(255)).put("size",size).put("mime",mime)
                                require(sameSession(selectionSession)) { "Сессия изменилась" }
                                selected[uri.toString()]=picked
                                output.put(picked)
                            }
                            promise?.resolve(output.toString())
                        } catch(error:Exception) { promise?.reject("PICK_FAILED","Не удалось прочитать выбранные файлы",error) }
                    }
                } else if(request==6102) {
                    val promise=managementPromise;managementPromise=null
                    val session=managementSession;managementSession=null
                    if(sameSession(session))promise?.resolve("null")
                    else promise?.reject("SESSION_CHANGED","Сессия изменилась")
                } else if(request==deletingRequest) {
                    if(sameSession(deletingSession))deleting?.let {
                        db.patch(it,JSONObject().put("state",if(result==Activity.RESULT_OK)"done" else "kept_local"),setOf("deleting"))
                    }
                    deleting=null;deletingSession=null;deletingRequest=null;TransferScheduler.kick(context)
                }
            }
        })
    }
    override fun getName()="StorageBridge"
    private fun async(promise:Promise,block:()->Any?) { executor.execute { try { promise.resolve(block()?.toString()?:"null") } catch(error:Exception) {
        val message=if(error is ApiException || error is IllegalArgumentException)error.message else "Не удалось выполнить действие"
        promise.reject(if(error is ApiException)error.code else "STORAGE_ERROR",message)
    } } }
    private fun credentials()=secure.read("session")?:throw IllegalStateException("Войдите через Telegram")
    private fun api():Api { val s=credentials();return Api(s.getString("baseUrl"),s.getString("token")) }
    private fun publicSession(session:JSONObject)=JSONObject().put("baseUrl",session.getString("baseUrl"))
        .put("userId",session.getString("userId")).put("localId",session.getString("localId"))
    @ReactMethod fun getSession(promise:Promise)=async(promise) { secure.read("session")?.let { publicSession(it) } }
    @ReactMethod fun request(path:String,method:String,body:String?,headers:ReadableMap,sessionId:String,promise:Promise)=async(promise) {
        if(!sameSession(sessionId))throw ApiException("SESSION_CHANGED","Сессия изменилась",401)
        val route=java.net.URI(path).rawPath
        require(route=="/me" || route=="/files" || route.startsWith("/files/") || route=="/sessions" || route.startsWith("/sessions/"))
        require(method in setOf("GET","POST","DELETE"))
        val safeHeaders=headers.toHashMap().mapValues { require(it.value is String);it.value.toString() }
        require(safeHeaders.keys.all { it=="Idempotency-Key" })
        require(body==null || body.length<=64*1024)
        api().request(path,method,body?.let { JSONObject(it) },safeHeaders)
    }
    @ReactMethod fun preferences(promise:Promise)=async(promise) { JSONObject().put("theme",preferences.getString("theme","system")).put("columns",preferences.getString("columns","3")!!.toInt()).put("baseUrl",preferences.getString("baseUrl",BuildConfig.SERVER_URL)) }
    @ReactMethod fun preference(key:String,value:String) { if(key in setOf("theme","columns"))preferences.edit().putString(key,value).apply() }
    @ReactMethod fun beginLogin(baseUrl:String,promise:Promise)=async(promise) {
        require(secure.read("session")==null) { "Сначала выйдите из текущего аккаунта" }
        val server=ServerPolicy.base(baseUrl)
        secure.write("attempt",null)
        val random=ByteArray(32).also { SecureRandom().nextBytes(it) }
        val verifier=Base64.encodeToString(random,Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        val challenge=Base64.encodeToString(MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray()),Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
        var installation=preferences.getString("installation",null)
        if(installation==null) { installation=UUID.randomUUID().toString();preferences.edit().putString("installation",installation).commit() }
        val response=Api(server).request("/auth/telegram/attempts","POST",JSONObject().put("code_challenge",challenge).put("installation_id",installation).put("device_name","Android"))
        val link=ServerPolicy.loginLink(response.getString("attempt_id"),response.getString("authorization_url"))
        require(Regex("[0-9]{6}").matches(response.getString("login_code"))) { "Неверный код входа" }
        response.put("authorization_url",link)
        secure.write("attempt",JSONObject().put("attempt_id",response.getString("attempt_id")).put("code_verifier",verifier).put("baseUrl",server))
        preferences.edit().putString("baseUrl",server).apply()
        response
    }
    @ReactMethod fun pollLogin(promise:Promise)=async(promise) {
        val attempt=secure.read("attempt")?:return@async JSONObject().put("state","none")
        try {
            val result=Api(attempt.getString("baseUrl")).request("/auth/telegram/attempts/${attempt.getString("attempt_id")}/exchange","POST",JSONObject().put("code_verifier",attempt.getString("code_verifier")))
            if(!result.has("session_token"))return@async result
            require(Regex("[A-Za-z0-9_-]{32,256}").matches(result.getString("session_token"))) { "Неверная сессия" }
            val session=JSONObject().put("localId",UUID.randomUUID().toString()).put("baseUrl",ServerPolicy.base(attempt.getString("baseUrl"))).put("token",result.getString("session_token")).put("userId",result.getJSONObject("user").getString("id"))
            secure.write("session",session);secure.write("attempt",null)
            for(row in db.rows(session.getString("userId"),session.getString("baseUrl")))if(row.getString("state")=="waiting_auth")db.patch(row.getString("id"),"queued")
            Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) }
            JSONObject().put("state","authenticated").put("session",publicSession(session))
        } catch(error:ApiException) {
            if(error.code=="NOT_WHITELISTED")JSONObject().put("state","denied").put("access_request_status",error.details.optString("access_request_status","not_requested")) else throw error
        }
    }
    @ReactMethod fun requestAccess(promise:Promise)=async(promise) {
        val attempt=secure.read("attempt")?:throw IllegalStateException("Войдите через Telegram ещё раз")
        Api(attempt.getString("baseUrl")).request("/access-requests","POST",JSONObject().put("attempt_id",attempt.getString("attempt_id")).put("code_verifier",attempt.getString("code_verifier")))
    }
    @ReactMethod fun logout(promise:Promise)=async(promise) {
        val previous=secure.withSession { session ->
            session?.let {
                db.rows(it.getString("userId"),it.getString("baseUrl")).filter { row ->
                    row.getString("state") !in setOf("done","kept_local","cancelled")
                }.forEach { row -> db.patch(row.getString("id"),"cancelled");TransferEngine.discardPendingDownload(context,row) }
            }
            secure.write("session",null);secure.write("attempt",null)
            session
        }
        Api.cancelAll()
        SecureNetwork.cancel()
        TransferScheduler.cancel(context)
        if(Fresco.hasBeenInitialized())Fresco.getImagePipeline().clearCaches()
        File(context.filesDir,"downloads").deleteRecursively()
        File(context.filesDir,"shares").deleteRecursively()
        selected.clear();deleting=null;deletingSession=null;deletingRequest=null
        context.contentResolver.persistedUriPermissions.forEach {
            val flags=(if(it.isReadPermission)Intent.FLAG_GRANT_READ_URI_PERMISSION else 0) or
                (if(it.isWritePermission)Intent.FLAG_GRANT_WRITE_URI_PERMISSION else 0)
            try { context.contentResolver.releasePersistableUriPermission(it.uri,flags) } catch (_:SecurityException) { }
        }
        // Local logout happens even offline. Server revocation is best effort.
        previous?.let { try { Api(it.getString("baseUrl"),it.getString("token")).request("/auth/logout","POST") } catch (_:Exception) { } }
        null
    }
    @ReactMethod fun pickFiles(promise:Promise) {
        val activity=context.currentActivity
        if(activity==null || picker!=null) { promise.reject("PICK_BUSY","Выбор файлов сейчас недоступен");return }
        val session=secure.read("session")
        if(session==null) { promise.reject("AUTH_REQUIRED","Войдите через Telegram");return }
        picker=promise;pickerSession=session.getString("localId")
        val intent=Intent(Intent.ACTION_OPEN_DOCUMENT).setType("*/*").addCategory(Intent.CATEGORY_OPENABLE)
            .putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
        activity.startActivityForResult(intent,6101)
    }
    @ReactMethod fun deviceAlbums(sessionId:String,promise:Promise)=async(promise) {
        require(sameSession(sessionId)) { "Сессия изменилась" }
        DeviceMediaCatalog(context).albums().also { require(sameSession(sessionId)) }
    }
    @ReactMethod fun deviceMedia(album:String,before:String,sessionId:String,promise:Promise)=async(promise) {
        require(sameSession(sessionId)) { "Сессия изменилась" }
        DeviceMediaCatalog(context).page(album,before).also { require(sameSession(sessionId)) }
    }
    @ReactMethod fun selectDeviceMedia(uris:ReadableArray,sessionId:String,promise:Promise)=async(promise) {
        require(sameSession(sessionId)) { "Сессия изменилась" }
        require(uris.size() in 1..1000)
        val catalog=DeviceMediaCatalog(context)
        val files=uris.toArrayList().map { catalog.resolve(it as String) }.distinctBy { it.getString("uri") }
        require(sameSession(sessionId)) { "Сессия изменилась" }
        selected.clear()
        files.forEach { selected[it.getString("uri")]=it }
        JSONArray(files)
    }
    @ReactMethod fun enqueue(files:ReadableArray,mode:String,promise:Promise)=async(promise) {
        require(mode in setOf("copy","move"))
        val current=credentials();val owner=current.getString("userId")
        require(files.size() in 1..1000)
        val list=files.toArrayList().map {
            val requested=JSONObject(it as Map<*,*>)
            JSONObject(requireNotNull(selected[requested.getString("uri")]) { "Файл не выбран на устройстве" }.toString())
        }.distinctBy { it.getString("uri") }
        for(file in list)db.add(file.put("id",UUID.randomUUID().toString()).put("owner_id",owner).put("base_url",current.getString("baseUrl").trimEnd('/')).put("state","queued").put("mode",mode).put("direction","upload").put("progress",0).put("error","").put("file_id",""))
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) };null
    }
    private fun queueDownloads(sources:List<JSONObject>,mode:String,sharing:Boolean,sessionId:String):String? {
        require(mode in setOf("copy","move") && (!sharing || mode=="copy"))
        require(sameSession(sessionId)) { "Сессия изменилась" }
        require(sources.size in 1..(if(sharing)100 else 1000)) { "Слишком много файлов для одной операции" }
        val current=credentials()
        val batch=if(sharing)UUID.randomUUID().toString() else null
        val rows=sources.distinctBy { it.getString("id") }.map { source ->
            val fileId=ServerPolicy.uuid(source.getString("id"))
            val size=source.getLong("size_bytes");val sha=source.getString("sha256")
            require(size>=0 && Regex("[0-9a-f]{64}").matches(sha))
            val name=source.getString("original_name")
            require(name.length in 1..255 && name.none { it<' ' || it=='/' || it=='\\' }) { "Неверное имя файла" }
            val mime=source.getString("mime_type")
            require(Regex("[a-zA-Z0-9.+_-]+/[a-zA-Z0-9.+_-]+").matches(mime))
            JSONObject().put("id",UUID.randomUUID().toString()).put("owner_id",current.getString("userId"))
                .put("base_url",current.getString("baseUrl").trimEnd('/')).put("name",name).put("size",size)
                .put("sha256",sha).put("mime",mime).put("file_id",fileId).put("state","queued")
                .put("mode",mode).put("direction","download").put("progress",0).put("error","")
                .put("purpose",if(sharing)"share" else "save").apply {
                    if(batch!=null)put("share_batch",batch).put("share_opened",false).put("share_expires_at",System.currentTimeMillis()+FileSharing.TTL)
                }
        }
        secure.withSession { require(sameSession(sessionId));db.addAll(rows) }
        val activeBatches=db.rows(current.getString("userId"),current.getString("baseUrl"))
            .filter { it.optString("purpose")=="share" && it.optString("state") !in setOf("done","cancelled","kept_local") }
            .map { it.optString("share_batch") }.toSet()
        FileSharing.cleanup(context,activeBatches)
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) }
        return batch
    }
    @ReactMethod fun download(file:ReadableMap,promise:Promise)=async(promise) {
        queueDownloads(listOf(JSONObject(file.toHashMap())),"copy",false,credentials().getString("localId"));null
    }
    @ReactMethod fun downloadFiles(files:ReadableArray,mode:String,sessionId:String,promise:Promise)=async(promise) {
        require(files.size() in 1..1000)
        queueDownloads(files.toArrayList().map { JSONObject(it as Map<*,*>) },mode,false,sessionId);null
    }
    @ReactMethod fun shareFiles(files:ReadableArray,sessionId:String,promise:Promise)=async(promise) {
        require(files.size() in 1..100) { "Для одной отправки выберите не больше 100 файлов" }
        JSONObject().put("batch_id",queueDownloads(files.toArrayList().map { JSONObject(it as Map<*,*>) },"copy",true,sessionId))
    }
    @ReactMethod fun openShareBatch(batchId:String,sessionId:String,promise:Promise) {
        executor.execute {
            try {
                ServerPolicy.uuid(batchId);require(sameSession(sessionId)) { "Сессия изменилась" }
                val current=credentials();api().request("/me")
                val rows=db.rows(current.getString("userId"),current.getString("baseUrl"))
                    .filter { it.optString("share_batch")==batchId && it.optString("purpose")=="share" }
                require(rows.isNotEmpty() && rows.all { it.optString("state")=="done" }) { "Дождитесь подготовки всех файлов" }
                require(rows.maxOf { it.optLong("share_expires_at") }>System.currentTimeMillis()) { "Подготовьте файлы заново" }
                val intent=FileSharing.intent(context,rows)
                Handler(Looper.getMainLooper()).post {
                    val activity=context.currentActivity
                    if(!sameSession(sessionId) || activity==null || context.lifecycleState!=LifecycleState.RESUMED) {
                        promise.reject("OPEN_APP","Откройте приложение, чтобы поделиться файлами");return@post
                    }
                    try {
                        activity.startActivity(intent)
                        rows.forEach { db.patch(it.getString("id"),JSONObject().put("share_opened",true),setOf("done")) }
                        promise.resolve("null")
                    } catch (_:Exception) { promise.reject("SHARE_FAILED","Не удалось открыть меню отправки") }
                }
            } catch(error:Exception) { promise.reject("SHARE_FAILED",if(error is IllegalArgumentException)error.message else "Не удалось подготовить отправку") }
        }
    }
    @ReactMethod fun transfers(promise:Promise)=async(promise) { credentials().let { JSONArray(db.rows(it.getString("userId"),it.getString("baseUrl"))) } }
    @ReactMethod fun action(id:String,action:String,promise:Promise)=async(promise) {
        val row=db.get(id)?:return@async null
        require(belongsToSession(row))
        val state=row.getString("state")
        require(state !in setOf("deleting","done","kept_local","cancelled")) { "Действие для этой передачи недоступно" }
        require(action in setOf("pause","resume","cancel"))
        when(action) {
            "pause"->db.patch(id,"paused")
            "resume"->db.patch(id,"queued")
            "cancel"->{db.patch(id,"cancelled");TransferEngine.discardPendingDownload(context,row);if(row.optString("upload_id").isNotBlank())try { api().request("/uploads/${row.getString("upload_id")}","DELETE") } catch (_:Exception) { }}
        }
        Handler(Looper.getMainLooper()).post { TransferScheduler.kick(context) };null
    }
    @ReactMethod fun cancelAllTransfers(sessionId:String,promise:Promise)=async(promise) {
        val cancelled=secure.withSession {
            require(sameSession(sessionId)) { "Сессия изменилась" }
            val current=credentials()
            val rows=db.rows(current.getString("userId"),current.getString("baseUrl"))
                .filter { it.getString("state") !in setOf("done","kept_local","cancelled") }
            rows.forEach { db.patch(it.getString("id"),"cancelled") }
            rows
        }
        Api.cancelTransfers()
        TransferScheduler.cancel(context)
        cancelled.filter { it.optString("direction")=="download" }.forEach {
            File(context.filesDir,"downloads/${ServerPolicy.uuid(it.getString("id"))}.part").delete()
            TransferEngine.discardPendingDownload(context,it)
            if(it.optString("purpose")=="share")FileSharing.file(context,it).delete()
        }
        Handler(Looper.getMainLooper()).post {
            if(sameSession(sessionId) && cancelled.any { it.getString("id")==deleting }) {
                deletingRequest?.let { code -> try { context.currentActivity?.finishActivity(code) } catch (_:Exception) { } }
                deleting=null;deletingSession=null;deletingRequest=null
            }
        }
        null
    }
    @ReactMethod fun canManageMedia(promise:Promise)=async(promise) { MediaStore.canManageMedia(context) }
    @ReactMethod fun requestManageMedia(promise:Promise) {
        Handler(Looper.getMainLooper()).post {
            val activity=context.currentActivity
            val session=secure.read("session")
            if(activity==null || session==null) { promise.reject("NO_ACTIVITY","Войдите и откройте приложение");return@post }
            if(managementPromise!=null) { promise.reject("REQUEST_BUSY","Запрос разрешения уже открыт");return@post }
            if(MediaStore.canManageMedia(context)) { promise.resolve("null");return@post }
            managementPromise=promise;managementSession=session.getString("localId")
            try {
                activity.startActivityForResult(Intent(Settings.ACTION_REQUEST_MANAGE_MEDIA,Uri.parse("package:${context.packageName}")),6102)
            } catch (_:Exception) {
                // Devices without this settings page can still show per-file delete consent.
                managementPromise=null;managementSession=null;promise.resolve("null")
            }
        }
    }
    @ReactMethod fun immersive(enabled:Boolean) {
        context.currentActivity?.runOnUiThread {
            context.currentActivity?.let { activity ->
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
    fun deleteVerified(row:JSONObject,sessionId:String,continuing:()->Boolean):Boolean {
        if(!continuing() || !sameSession(sessionId) || !belongsToSession(row))return false
        val fresh=db.get(row.getString("id"))?:return false
        if(fresh.optString("mode")!="move" || fresh.optString("direction")!="upload" ||
            fresh.optString("file_id").isBlank() || fresh.optString("state")!="verifying" ||
            fresh.optString("sha256")!=row.optString("sha256") || fresh.optString("uri")!=row.optString("uri"))return false
        if(context.currentActivity==null || context.lifecycleState!=LifecycleState.RESUMED)return false
        val id=row.getString("id")
        if(deleting!=null)return false
        val source=Uri.parse(row.getString("uri"))
        val media=if(source.authority=="media")source else try { MediaStore.getMediaUri(context,source) } catch (_:Exception) { null }
        if(!db.patch(id,JSONObject().put("state","deleting"),TransferEngine.RUNNABLE))return false
        deleting=id;deletingSession=sessionId
        Handler(Looper.getMainLooper()).post {
            if(!continuing() || !sameSession(sessionId) || !belongsToSession(row) || db.get(id)?.optString("state")!="deleting") {
                db.patch(id,JSONObject().put("state","awaiting_foreground"),setOf("deleting"))
                deleting=null;deletingSession=null;return@post
            }
            val activity=context.currentActivity
            if(activity==null) { deleting=null;deletingSession=null;db.patch(id,"awaiting_foreground");return@post }
            try {
                if(media!=null) {
                    deleting=id
                    val request=MediaStore.createDeleteRequest(context.contentResolver,listOf(media))
                    val code=deletionCodes.getAndIncrement()
                    require(code<=65535) { "Перезапустите приложение перед следующим удалением" }
                    deletingRequest=code
                    activity.startIntentSenderForResult(request.intentSender,code,null,0,0,0)
                } else if(DocumentsContract.isDocumentUri(context,source)) {
                    val removed=DocumentsContract.deleteDocument(context.contentResolver,source)
                    db.patch(id,if(removed)"done" else "kept_local");deleting=null;deletingSession=null
                } else { deleting=null;deletingSession=null;db.patch(id,"awaiting_permission") }
            } catch (_:SecurityException) { deleting=null;deletingSession=null;db.patch(id,"awaiting_permission")
            } catch (_:Exception) { deleting=null;deletingSession=null;db.patch(id,"kept_local") }
        }
        return true
    }
    override fun onHostResume() {
        TransferScheduler.kick(context)
    }
    override fun onHostPause() = Unit
    override fun onHostDestroy() = Unit
    override fun invalidate() { if(instance===this)instance=null;super.invalidate() }
}
