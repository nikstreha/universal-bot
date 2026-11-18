package local.storage.transfer

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Environment
import android.os.StatFs
import local.storage.security.ServerPolicy
import android.provider.MediaStore
import local.storage.StorageBridge
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileNotFoundException
import java.io.InputStream
import java.io.RandomAccessFile
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean

private class TransferStoppedException : Exception("Transfer stopped")

class TransferEngine(private val context:Context, private val stopped:()->Boolean = {false}) {
    companion object {
        val RUNNABLE=setOf("queued","preparing","uploading","verifying","waiting_network","awaiting_foreground","removing_server")
        private val running=AtomicBoolean(false)
        fun hash(stream:InputStream, active:()->Boolean = {true}):Pair<String,Long> {
            val digest=MessageDigest.getInstance("SHA-256");var size=0L
            val buffer=ByteArray(1024*1024)
            stream.use { while(true) { if(!active())throw TransferStoppedException();val count=it.read(buffer);if(count<0)break;digest.update(buffer,0,count);size+=count } }
            return digest.digest().joinToString("") { "%02x".format(it) } to size
        }
        fun hash(bytes:ByteArray)=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        fun discardPendingDownload(context:Context,row:JSONObject) {
            val raw=row.optString("pending_uri");if(raw.isBlank())return
            val uri=Uri.parse(raw);if(uri.scheme!="content" || uri.authority!="media")return
            try {
                val removable=context.contentResolver.query(uri,arrayOf(MediaStore.MediaColumns.OWNER_PACKAGE_NAME,MediaStore.MediaColumns.IS_PENDING),null,null,null)?.use {
                    it.moveToFirst() && it.getString(0)==context.packageName && it.getInt(1)==1
                }==true
                if(removable)context.contentResolver.delete(uri,null,null)
            }catch (_:Exception) { }
        }
    }
    private val db=TransferDatabase(context)
    private val secure=SecureStore(context)
    private var executionSession:String?=null
    private fun active(id:String):Boolean {
        if(stopped())return false
        val current=secure.read("session")?:return false
        if(current.optString("localId")!=executionSession)return false
        val row=db.get(id)?:return false
        return row.getString("state") in RUNNABLE && row.getString("owner_id")==current.getString("userId") && row.optString("base_url")==current.getString("baseUrl").trimEnd('/')
    }
    private fun update(id:String,vararg values:Pair<String,Any>):Boolean = secure.withSession {
        if(!active(id))false else db.patch(id,JSONObject().apply { values.forEach { put(it.first,it.second) } },RUNNABLE)
    }
    private fun source(row:JSONObject):InputStream {
        val uri=Uri.parse(row.getString("uri"))
        require(uri.scheme=="content") { "Неверный источник файла" }
        return context.contentResolver.openInputStream(uri)?:throw FileNotFoundException()
    }
    private fun session()=SecureStore(context).read("session")?:throw ApiException("AUTH_REQUIRED","Войдите через Telegram",401)
    fun run():Boolean {
        if(!running.compareAndSet(false,true))return false
        var retry=false
        try {
            val credentials=session()
            executionSession=credentials.getString("localId")
            val api=Api(credentials.getString("baseUrl"),credentials.getString("token"),transfer=true)
            for(row in db.rows(credentials.getString("userId"), credentials.getString("baseUrl"))) {
                val id=row.getString("id")
                if(!active(id))continue
                try {
                    if(row.optString("direction")=="download") download(row,api) else upload(row,api)
                    if(db.get(id)?.optString("state")=="deleting")break
                } catch (_:TransferStoppedException) { continue
                } catch (error:ApiException) {
                    val state=when {
                        error.status==401 -> "waiting_auth"
                        error.status==403 -> "access_revoked"
                        error.status==429 || error.status>=500 -> "waiting_network"
                        else -> "failed"
                    }
                    update(id,"state" to state,"error" to error.message)
                    if(state=="waiting_network")retry=true
                } catch (_:SecurityException) { update(id,"state" to "needs_source","error" to "Нет доступа к исходному файлу")
                } catch (_:FileNotFoundException) { update(id,"state" to "needs_source","error" to "Исходный файл недоступен")
                } catch (_:java.io.IOException) { update(id,"state" to "waiting_network","error" to "Нет соединения или сервер недоступен"); retry=true
                } catch (error:Exception) { update(id,"state" to "failed","error" to (error.message?:"Ошибка передачи")) }
            }
        } catch (_:Exception) { return false }
        finally { running.set(false) }
        return retry
    }
    private fun upload(row:JSONObject,api:Api) {
        val id=row.getString("id")
        if(!active(id))return
        if(row.optString("sha256").isBlank()) {
            if(!update(id,"state" to "preparing"))return
            val (sha,size)=hash(source(row)) { active(id) }
            if(!update(id,"sha256" to sha,"size" to size,"state" to "uploading"))return
            row.put("sha256",sha).put("size",size)
        }
        var uploadId=row.optString("upload_id")
        if(uploadId.isBlank()) {
            val created=api.request("/uploads","POST",JSONObject().put("original_name",row.getString("name")).put("size_bytes",row.getLong("size")).put("sha256",row.getString("sha256")).put("declared_mime",row.optString("mime","application/octet-stream")),mapOf("Idempotency-Key" to id))
            uploadId=ServerPolicy.uuid(created.getString("upload_id"))
            if(!update(id,"upload_id" to uploadId,"archive_path" to created.getString("archive_path")))return
        }
        ServerPolicy.uuid(uploadId)
        if(!active(id))return
        var status=api.request("/uploads/$uploadId")
        if(status.getString("state")=="receiving") {
            val partSize=status.getInt("part_size_bytes")
            require(partSize in 1..(32*1024*1024)) { "Неверный размер части файла" }
            val received=mutableSetOf<Int>();status.getJSONArray("received_parts").let { for(i in 0 until it.length())received.add(it.getInt(i)) }
            source(row).use { stream ->
                var index=0;var total=0L
                while(total<row.getLong("size")) {
                    if(!active(id))return
                    val expected=minOf(partSize.toLong(),row.getLong("size")-total).toInt()
                    val part=ByteArray(expected);var count=0
                    while(count<expected) { val read=stream.read(part,count,expected-count);if(read<0)throw IllegalStateException("Исходный файл изменился");count+=read }
                    if(index !in received) api.request("/uploads/$uploadId/parts/$index","PUT",headers=mapOf("X-Content-SHA256" to hash(part)),bytes=part)
                    total+=count;index++
                    if(!update(id,"progress" to total,"state" to "uploading"))return
                }
            }
            if(!active(id))return
            status=api.request("/uploads/$uploadId/complete","POST",JSONObject())
        }
        if(!update(id,"state" to "verifying"))return
        while(active(id) && status.getString("state")=="verifying") { Thread.sleep(1500);status=api.request("/uploads/$uploadId") }
        if(!active(id))return
        if(status.getString("state")!="completed")throw IllegalStateException("Сохранение не завершено: "+status.optString("error",status.getString("state")))
        val fileId=ServerPolicy.uuid(status.getString("file_id"))
        if(!update(id,"file_id" to fileId,"progress" to row.getLong("size")))return
        row.put("file_id",fileId)
        if(row.getString("mode")=="copy") { update(id,"state" to "done");return }
        // A resumed deletion always obtains a new server-side integrity check.
        val check=api.request("/files/$fileId/verifications","POST",JSONObject(),mapOf("Idempotency-Key" to UUID.randomUUID().toString()))
        var result=check
        while(active(id) && result.getString("state") in setOf("queued","running")) { Thread.sleep(1500);result=api.request("/files/$fileId/verifications/"+check.getString("id")) }
        if(!active(id))return
        if(result.getString("state")!="succeeded" || result.optString("integrity")!="verified" || result.optString("file_id")!=fileId || result.optString("observed_sha256")!=row.getString("sha256") || result.optLong("observed_size",-1)!=row.getLong("size"))throw IllegalStateException("Серверная копия не прошла проверку")
        val (actual,size)=hash(source(row)) { active(id) }
        if(actual!=row.getString("sha256") || size!=row.getLong("size"))throw IllegalStateException("Оригинал изменился. Удаление остановлено")
        if(!active(id))return
        val bridge=StorageBridge.instance
        if(bridge==null || !bridge.deleteVerified(row,requireNotNull(executionSession)) { !stopped() }) update(id,"state" to "awaiting_foreground")
    }
    private fun download(row:JSONObject,api:Api) {
        val id=ServerPolicy.uuid(row.getString("id"))
        val fileId=ServerPolicy.uuid(row.getString("file_id"))
        val expectedSize=row.getLong("size")
        require(expectedSize>=0 && Regex("[0-9a-f]{64}").matches(row.getString("sha256")))
        if(!active(id))return
        val pending=row.optString("pending_uri")
        if(pending.isNotBlank() && !row.optBoolean("local_verified")) {
            val uri=Uri.parse(pending)
            require(uri.scheme=="content" && uri.authority=="media")
            val state=context.contentResolver.query(uri,arrayOf(MediaStore.MediaColumns.OWNER_PACKAGE_NAME,MediaStore.MediaColumns.IS_PENDING),null,null,null)?.use {
                if(!it.moveToFirst())null else { require(it.getString(0)==context.packageName);it.getInt(1) }
            }
            if(state==0) {
                val (sha,size)=hash(requireNotNull(context.contentResolver.openInputStream(uri))) { active(id) }
                require(sha==row.getString("sha256") && size==expectedSize) { "Копия на устройстве изменилась. Серверный файл сохранён." }
                if(!update(id,"local_verified" to true,"local_uri" to pending,"pending_uri" to ""))return
                row.put("local_verified",true).put("local_uri",pending)
            }else {
                discardPendingDownload(context,row)
                if(!update(id,"pending_uri" to ""))return
            }
        }
        if(row.optBoolean("local_verified") && row.optString("local_uri").isNotBlank()) {
            finishLocalDownload(row,api);return
        }
        val metadata=api.request("/files/$fileId")
        require(metadata.getString("sha256")==row.getString("sha256") && metadata.getLong("size_bytes")==expectedSize) { "Метаданные файла на сервере изменились" }
        val dir=File(context.filesDir,"downloads").apply { mkdirs() }
        val temporary=File(dir,"$id.part")
        if(temporary.length()>expectedSize)check(temporary.delete())
        var offset=temporary.length()
        val remaining=expectedSize-offset
        require(remaining <= StatFs(dir.path).availableBytes - 64L*1024*1024) { "Недостаточно места на устройстве" }
        if(!temporary.exists() || offset<expectedSize) {
            val connection=api.connection("/files/$fileId/content")
            connection.setRequestProperty("Accept-Encoding","identity")
            if(offset>0) { connection.setRequestProperty("Range","bytes=$offset-");connection.setRequestProperty("If-Range","\"${row.getString("sha256")}\"") }
            try {
                val code=connection.responseCode
                if(code !in setOf(200,206))throw ApiException("DOWNLOAD_FAILED","Не удалось скачать файл",code)
                if(code==200)offset=0
                else require(connection.getHeaderField("Content-Range")=="bytes $offset-${expectedSize-1}/$expectedSize") { "Неверный диапазон скачивания" }
                val length=connection.getHeaderFieldLong("Content-Length",-1)
                require(length<0 || length==expectedSize-offset) { "Размер скачивания не совпадает" }
                if(!update(id,"state" to "uploading"))return
                RandomAccessFile(temporary,"rw").use { output ->
                    if(offset==0L)output.setLength(0)
                    output.seek(offset)
                    connection.inputStream.use { input ->
                        var lastProgress=0L
                        val buffer=ByteArray(256*1024)
                        while(true) {
                            if(!active(id))throw TransferStoppedException()
                            val count=input.read(buffer)
                            if(count<0)break
                            require(count.toLong()<=expectedSize-offset) { "Сервер прислал лишние данные" }
                            output.write(buffer,0,count);offset+=count
                            val now=android.os.SystemClock.elapsedRealtime()
                            if(now-lastProgress>=250 || offset==expectedSize){update(id,"progress" to offset);lastProgress=now}
                        }
                    }
                }
            } finally { api.close(connection) }
        }
        if(!update(id,"state" to "verifying"))return
        val (sha,size)=hash(temporary.inputStream()) { active(id) }
        if(sha!=row.getString("sha256") || size!=expectedSize) { temporary.delete();throw IllegalStateException("Скачанная копия не прошла проверку") }
        if(!active(id))return
        if(row.optString("purpose")=="share") {
            val target=FileSharing.file(context,row)
            secure.withSession {
                if(!active(id))throw TransferStoppedException()
                target.parentFile!!.mkdirs()
                if(target.exists())check(target.delete())
                check(temporary.renameTo(target)) { "Не удалось сохранить файл отправки" }
                target.parentFile!!.setLastModified(System.currentTimeMillis())
                update(id,"state" to "done","share_expires_at" to (System.currentTimeMillis()+FileSharing.TTL))
            }
            return
        }
        val mime=row.optString("mime","application/octet-stream")
        val collection=when { mime.startsWith("image/")->MediaStore.Images.Media.EXTERNAL_CONTENT_URI;mime.startsWith("video/")->MediaStore.Video.Media.EXTERNAL_CONTENT_URI;else->MediaStore.Downloads.EXTERNAL_CONTENT_URI }
        val directory=when { mime.startsWith("image/")->Environment.DIRECTORY_PICTURES;mime.startsWith("video/")->Environment.DIRECTORY_MOVIES;else->Environment.DIRECTORY_DOWNLOADS }
        val values=ContentValues().apply { put(MediaStore.MediaColumns.DISPLAY_NAME,row.getString("name"));put(MediaStore.MediaColumns.MIME_TYPE,mime);put(MediaStore.MediaColumns.RELATIVE_PATH,"$directory/storage");put(MediaStore.MediaColumns.IS_PENDING,1) }
        val uri=secure.withSession {
            if(!active(id))throw TransferStoppedException()
            context.contentResolver.insert(collection,values)?:throw IllegalStateException("Не удалось создать файл на устройстве")
        }
        if(!update(id,"pending_uri" to uri.toString())) {
            context.contentResolver.delete(uri,null,null);return
        }
        var published=false
        try {
            requireNotNull(context.contentResolver.openOutputStream(uri)).use { output ->
                temporary.inputStream().use { input ->
                    val buffer=ByteArray(256*1024)
                    while(true) {
                        if(!active(id))throw TransferStoppedException()
                        val count=input.read(buffer);if(count<0)break
                        output.write(buffer,0,count)
                    }
                }
            }
            val (localHash,localSize)=hash(requireNotNull(context.contentResolver.openInputStream(uri))) { active(id) }
            require(localHash==sha && localSize==expectedSize) { "Копия на устройстве не прошла проверку" }
            secure.withSession {
                if(!active(id))throw TransferStoppedException()
                require(context.contentResolver.update(uri,ContentValues().apply { put(MediaStore.MediaColumns.IS_PENDING,0) },null,null)==1)
                published=true
                require(update(id,"local_verified" to true,"local_uri" to uri.toString(),"uri" to uri.toString(),"pending_uri" to ""))
                row.put("local_verified",true).put("local_uri",uri.toString())
            }
            temporary.delete()
        } catch(error:Exception) { if(!published)context.contentResolver.delete(uri,null,null);throw error }
        finishLocalDownload(row,api)
    }
    private fun finishLocalDownload(row:JSONObject,api:Api) {
        val id=row.getString("id")
        if(!active(id))return
        if(row.getString("mode")=="move") {
            if(!update(id,"state" to "removing_server"))return
            val uri=Uri.parse(row.getString("local_uri"))
            require(uri.scheme=="content" && uri.authority=="media")
            val (sha,size)=hash(requireNotNull(context.contentResolver.openInputStream(uri))) { active(id) }
            require(sha==row.getString("sha256") && size==row.getLong("size")) { "Копия на устройстве изменилась. Серверный файл сохранён." }
            if(!active(id))return
            val fileId=ServerPolicy.uuid(row.getString("file_id"))
            val metadata=api.request("/files/$fileId")
            require(metadata.getString("sha256")==sha && metadata.getLong("size_bytes")==size)
            if(!active(id))return
            api.request("/files/$fileId/trash","POST",JSONObject())
            if(!active(id))return
            update(id,"state" to "done","server_removed" to true,"error" to "")
        }else update(id,"state" to "done","error" to "")
    }
}
