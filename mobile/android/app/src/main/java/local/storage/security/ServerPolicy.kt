package local.storage.security

import local.storage.BuildConfig
import java.net.URI
import java.util.Locale
import java.util.UUID

/** A release can only send credentials and files to the server embedded at build time. */
object ServerPolicy {
    private val developmentHosts = setOf("localhost", "127.0.0.1", "10.0.2.2")

    private fun origin(raw: String): URI {
        require(raw == raw.trim() && raw.none { it <= ' ' || it == '\\' }) { "Неверный адрес сервера" }
        val uri = URI(raw)
        require(uri.isAbsolute && !uri.host.isNullOrBlank() && uri.rawUserInfo == null &&
            uri.rawQuery == null && uri.rawFragment == null && uri.rawPath in listOf("", "/") &&
            uri.port in -1..65535 && uri.port != 0) { "Укажите адрес сервера без пути и параметров" }
        val scheme = uri.scheme.lowercase(Locale.ROOT)
        val host = uri.host.lowercase(Locale.ROOT)
        require(scheme == "https" || BuildConfig.DEBUG && scheme == "http" && host in developmentHosts) {
            "Используйте HTTPS; HTTP разрешён только для локальной отладки"
        }
        return URI(scheme, null, host, if(uri.port == 443 && scheme == "https" || uri.port == 80 && scheme == "http") -1 else uri.port, null, null, null)
    }

    fun base(raw: String): String {
        val result = origin(raw)
        if (!BuildConfig.DEBUG) {
            require(result == origin(BuildConfig.SERVER_URL)) { "Этот сервер не разрешён для приложения" }
        }
        return result.toASCIIString()
    }

    fun request(rawBase: String, path: String): String {
        val server = base(rawBase)
        val uri = URI(path)
        require(path.startsWith("/") && !path.startsWith("//") && uri.scheme == null &&
            uri.rawAuthority == null && uri.rawFragment == null && uri.normalize() == uri &&
            '\\' !in path && path.none { it < ' ' } &&
            !Regex("(?i)%2e|%2f|%5c").containsMatchIn(uri.rawPath)) { "Неверный путь запроса" }
        return server + "/api/v1" + path
    }

    fun uuid(raw: String): String {
        require(raw == UUID.fromString(raw).toString()) { "Неверный идентификатор" }
        return raw
    }

    fun loginLink(attempt: String, returned: String): String {
        val username = BuildConfig.BOT_USERNAME
        require(Regex("[A-Za-z0-9_]{5,32}").matches(username) && username.endsWith("bot", true)) {
            "Telegram-бот не настроен в сборке"
        }
        val expected = "https://t.me/$username?start=login_${uuid(attempt)}"
        require(returned == expected) { "Сервер вернул постороннюю ссылку авторизации" }
        return expected
    }

    fun media(raw: String, server: String): String {
        val uri = URI(raw)
        require(uri.rawFragment == null && uri.rawUserInfo == null) { "Неверный адрес медиа" }
        val prefix = base(server)
        require(raw.startsWith("$prefix/api/v1/files/")) { "Посторонний адрес медиа" }
        require(Regex("/api/v1/files/[0-9a-f-]{36}/(content|thumbnail)").matches(uri.rawPath) &&
            uri.rawQuery in listOf(null, "disposition=inline")) { "Неверный адрес медиа" }
        return raw
    }
}
