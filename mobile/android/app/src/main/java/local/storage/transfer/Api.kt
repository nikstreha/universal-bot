package local.storage.transfer

import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class ApiException(val code: String, override val message: String, val status: Int, val details:JSONObject=JSONObject()) : Exception(message)

class Api(private val base: String, private val token: String = "") {
    fun connection(path: String): HttpURLConnection = (URL(base.trimEnd('/')+"/api/v1"+path).openConnection() as HttpURLConnection).apply {
        instanceFollowRedirects=false
        connectTimeout=20000; readTimeout=60000
        if(token.isNotEmpty()) setRequestProperty("Authorization","Bearer $token")
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
            val text=(if(status in 200..299) connection.inputStream else connection.errorStream)?.bufferedReader()?.use { it.readText() }.orEmpty()
            val json=if(text.isBlank()) JSONObject() else JSONObject(text)
            if(status !in 200..299) {
                val error=json.optJSONObject("error")
                throw ApiException(error?.optString("code")?:"HTTP_ERROR",error?.optString("message")?:"Ошибка сервера",status,error?.optJSONObject("details")?:JSONObject())
            }
            return json
        } finally { connection.disconnect() }
    }
}
