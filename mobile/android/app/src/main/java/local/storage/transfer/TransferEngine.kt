package local.storage.transfer

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Environment
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

class TransferEngine(private val context:Context) {
    companion object {
        val RUNNABLE=setOf("queued","preparing","uploading","verifying","waiting_network","awaiting_foreground")
        private val running=AtomicBoolean(false)
        fun hash(stream:InputStream):Pair<String,Long> {
            val digest=MessageDigest.getInstance("SHA-256");var size=0L
            val buffer=ByteArray(1024*1024)
            stream.use { while(true) { val count=it.read(buffer);if(count<0)break;digest.update(buffer,0,count);size+=count } }
            return digest.digest().joinToString("") { "%02x".format(it) } to size
        }
        fun hash(bytes:ByteArray)=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
    }
    private val db=TransferDatabase(context)
    private fun active(id:String):Boolean {
        val current=SecureStore(context).read("session")?:return false
        val row=db.get(id)?:return false
        return row.getString("state") in RUNNABLE && row.getString("owner_id")==current.getString("userId") && row.optString("base_url")==current.getString("baseUrl").trimEnd('/')
    }
    private fun update(id:String,vararg values:Pair<String,Any>):Boolean = db.patch(id,JSONObject().apply { values.forEach { put(it.first,it.second) } },RUNNABLE)
    private fun source(row:JSONObject):InputStream = context.contentResolver.openInputStream(Uri.parse(row.getString("uri")))?:throw FileNotFoundException()
    private fun session()=SecureStore(context).read("session")?:throw ApiException("AUTH_REQUIRED","Войдите через Telegram",401)
    fun run():Boolean {
        if(!running.compareAndSet(false,true))return false
        var retry=false
        try {
            val credentials=session()
            val api=Api(credentials.getString("baseUrl"),credentials.getString("token"))
            for(row in db.rows(credentials.getString("userId"), credentials.getString("baseUrl"))) {
                val id=row.getString("id")
                if(!active(id))continue
                try {
                    if(row.optString("direction")=="download") download(row,api) else upload(row,api)
                    if(db.get(id)?.optString("state")=="deleting")break
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
        if(row.optString("sha256").isBlank()) {
            if(!update(id,"state" to "preparing"))return
            val (sha,size)=hash(source(row))
            if(!update(id,"sha256" to sha,"size" to size,"state" to "uploading"))return
            row.put("sha256",sha).put("size",size)
        }
        var uploadId=row.optString("upload_id")
        if(uploadId.isBlank()) {
            val created=api.request("/uploads","POST",JSONObject().put("original_name",row.getString("name")).put("size_bytes",row.getLong("size")).put("sha256",row.getString("sha256")).put("declared_mime",row.optString("mime","application/octet-stream")),mapOf("Idempotency-Key" to id))
            uploadId=created.getString("upload_id")
            if(!update(id,"upload_id" to uploadId,"archive_path" to created.getString("archive_path")))return
        }
        var status=api.request("/uploads/$uploadId")
        if(status.getString("state")=="receiving") {
            val partSize=status.getInt("part_size_bytes")
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
        update(id,"state" to "verifying")
        while(active(id) && status.getString("state")=="verifying") { Thread.sleep(1500);status=api.request("/uploads/$uploadId") }
        if(!active(id))return
        if(status.getString("state")!="completed")throw IllegalStateException("Сохранение не завершено: "+status.optString("error",status.getString("state")))
        val fileId=status.getString("file_id")
        if(!update(id,"file_id" to fileId,"progress" to row.getLong("size")))return
        row.put("file_id",fileId)
        if(row.getString("mode")=="copy") { update(id,"state" to "done");return }
        // A resumed deletion always obtains a new server-side integrity check.
        val check=api.request("/files/$fileId/verifications","POST",JSONObject(),mapOf("Idempotency-Key" to UUID.randomUUID().toString()))
        var result=check
        while(active(id) && result.getString("state") in setOf("queued","running")) { Thread.sleep(1500);result=api.request("/files/$fileId/verifications/"+check.getString("id")) }
        if(!active(id))return
        if(result.getString("state")!="succeeded" || result.optString("integrity")!="verified" || result.optString("file_id")!=fileId || result.optString("observed_sha256")!=row.getString("sha256") || result.optLong("observed_size",-1)!=row.getLong("size"))throw IllegalStateException("Серверная копия не прошла проверку")
        val (actual,size)=hash(source(row))
        if(actual!=row.getString("sha256") || size!=row.getLong("size"))throw IllegalStateException("Оригинал изменился. Удаление остановлено")
        val bridge=StorageBridge.instance
        if(bridge==null || !bridge.deleteVerified(row)) update(id,"state" to "awaiting_foreground")
    }
    private fun download(row:JSONObject,api:Api) {
        val id=row.getString("id")
        val dir=File(context.filesDir,"downloads").apply { mkdirs() }
        val temporary=File(dir,"$id.part")
        val connection=api.connection("/files/${row.getString("file_id")}/content")
        var offset=temporary.length()
        if(offset>0) { connection.setRequestProperty("Range","bytes=$offset-");connection.setRequestProperty("If-Range","\"${row.getString("sha256")}\"") }
        try {
            val code=connection.responseCode
            if(code !in setOf(200,206))throw ApiException("DOWNLOAD_FAILED","Не удалось скачать файл",code)
            if(code==200)offset=0
            if(!update(id,"state" to "uploading"))return
            RandomAccessFile(temporary,"rw").use { output ->
                if(offset==0L)output.setLength(0)
                output.seek(offset)
                connection.inputStream.use { input ->
                    val buffer=ByteArray(256*1024)
                    while(true) { if(!active(id))return;val count=input.read(buffer);if(count<0)break;output.write(buffer,0,count);offset+=count;update(id,"progress" to offset) }
                }
            }
        } finally { connection.disconnect() }
        update(id,"state" to "verifying")
        val (sha,size)=hash(temporary.inputStream())
        if(sha!=row.getString("sha256") || size!=row.getLong("size")) { temporary.delete();throw IllegalStateException("Скачанная копия не прошла проверку") }
        if(!active(id))return
        val mime=row.optString("mime","application/octet-stream")
        val collection=when { mime.startsWith("image/")->MediaStore.Images.Media.EXTERNAL_CONTENT_URI;mime.startsWith("video/")->MediaStore.Video.Media.EXTERNAL_CONTENT_URI;else->MediaStore.Downloads.EXTERNAL_CONTENT_URI }
        val directory=when { mime.startsWith("image/")->Environment.DIRECTORY_PICTURES;mime.startsWith("video/")->Environment.DIRECTORY_MOVIES;else->Environment.DIRECTORY_DOWNLOADS }
        val values=ContentValues().apply { put(MediaStore.MediaColumns.DISPLAY_NAME,row.getString("name"));put(MediaStore.MediaColumns.MIME_TYPE,mime);put(MediaStore.MediaColumns.RELATIVE_PATH,"$directory/storage");put(MediaStore.MediaColumns.IS_PENDING,1) }
        val uri=context.contentResolver.insert(collection,values)?:throw IllegalStateException("Не удалось создать файл на устройстве")
        try {
            context.contentResolver.openOutputStream(uri)!!.use { output -> temporary.inputStream().use { it.copyTo(output) } }
            context.contentResolver.update(uri,ContentValues().apply { put(MediaStore.MediaColumns.IS_PENDING,0) },null,null)
            temporary.delete();update(id,"state" to "done","uri" to uri.toString())
        } catch(error:Exception) { context.contentResolver.delete(uri,null,null);throw error }
    }
}
