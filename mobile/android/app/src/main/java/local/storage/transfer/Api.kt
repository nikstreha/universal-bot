package local.storage.transfer

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.io.ByteArrayOutputStream
import java.io.IOException
import local.storage.security.ServerPolicy

class ApiException(val code: String, override val message: String, val status: Int, val details:JSONObject=JSONObject()) : Exception(message)

class Api(private val base: String, private val token: String = "", private val transfer: Boolean = false) {
    companion object {
        private val lock=Any()
        private val connections=mutableMapOf<HttpURLConnection,Boolean>()
        @Volatile private var generation=0L
        @Volatile private var transferGeneration=0L
        fun cancelTransfers() {
            val active=synchronized(lock) {
                transferGeneration++
                connections.filterValues { it }.keys.toList().also { rows -> rows.forEach { connections.remove(it) } }
            }
            active.forEach { it.disconnect() }
        }
        fun cancelAll()=synchronized(lock) {
            generation++
            connections.keys.forEach { it.disconnect() };connections.clear()
        }
    }
    private val born=generation
    private val transferBorn=transferGeneration
    fun connection(path: String): HttpURLConnection = (URL(ServerPolicy.request(base,path)).openConnection() as HttpURLConnection).apply {
        instanceFollowRedirects=false
        useCaches=false
        connectTimeout=20000; readTimeout=60000
        if(token.isNotEmpty()) setRequestProperty("Authorization","Bearer $token")
        synchronized(lock) {
            if(born!=generation || transfer&&transferBorn!=transferGeneration)throw IOException("Request cancelled")
            connections[this]=transfer
        }
    }
    fun close(connection:HttpURLConnection) {
        synchronized(lock) { connections.remove(connection) }
        connection.disconnect()
    }
    fun request(path: String, method: String="GET", body: JSONObject?=null, headers: Map<String,String> = emptyMap(), bytes: ByteArray?=null): JSONObject {
        val connection = connection(path)
        try {
            connection.requestMethod=method
            headers.forEach { (k,v) -> connection.setRequestProperty(k,v) }
            val payload = bytes ?: body?.toString()?.toByteArray(Charsets.UTF_8)
            if(payload != null) {
                connection.doOutput=true
                if(bytes==null) connection.setRequestProperty("Content-Type","application/json")
                connection.setFixedLengthStreamingMode(payload.size)
                connection.outputStream.use { it.write(payload) }
            }
            val status=connection.responseCode
            if(status in 300..399)throw ApiException("REDIRECT_REJECTED","Перенаправление запроса запрещено",status)
            val text=(if(status in 200..299) connection.inputStream else connection.errorStream)?.use {
                val result=ByteArrayOutputStream()
                val buffer=ByteArray(8192)
                while(true) {
                    val count=it.read(buffer)
                    if(count<0)break
                    require(result.size()+count<=2*1024*1024) { "Ответ сервера слишком большой" }
                    result.write(buffer,0,count)
                }
                result.toString("UTF-8")
            }.orEmpty()
            val json=if(text.isBlank()) JSONObject() else JSONObject(text)
            if(status !in 200..299) {
                val error=json.optJSONObject("error")
                throw ApiException(error?.optString("code")?:"HTTP_ERROR",error?.optString("message")?:"Ошибка сервера",status,error?.optJSONObject("details")?:JSONObject())
            }
            return json
        } finally { close(connection) }
    }
}
