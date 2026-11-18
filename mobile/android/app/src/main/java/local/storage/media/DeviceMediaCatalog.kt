package local.storage.media

import android.content.ContentUris
import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.os.Bundle
import android.content.ContentResolver
import android.provider.MediaStore
import org.json.JSONArray
import org.json.JSONObject

/** Local indexed photos/videos only. Never accepts filesystem paths from JS. */
class DeviceMediaCatalog(private val context: Context) {
    private val collection = MediaStore.Files.getContentUri(MediaStore.VOLUME_EXTERNAL)
    private val visible = "media_type IN (1,3) AND is_pending=0 AND is_trashed=0"
    private val projection = arrayOf("_id", "_display_name", "_size", "mime_type", "media_type", "volume_name", "bucket_id", "bucket_display_name")

    private fun file(cursor: Cursor): JSONObject {
        val volume = cursor.getString(5)
        val video = cursor.getInt(4) == MediaStore.Files.FileColumns.MEDIA_TYPE_VIDEO
        val base = if (video) MediaStore.Video.Media.getContentUri(volume) else MediaStore.Images.Media.getContentUri(volume)
        return JSONObject().put("uri", ContentUris.withAppendedId(base, cursor.getLong(0)).toString())
            .put("name", cursor.getString(1) ?: "file").put("size", cursor.getLong(2).coerceAtLeast(0))
            .put("mime", cursor.getString(3) ?: if (video) "video/mp4" else "image/jpeg")
            .put("kind", if (video) "video" else "photo")
    }

    fun albums(): JSONArray {
        val albums = linkedMapOf<String, JSONObject>()
        context.contentResolver.query(collection, arrayOf("volume_name", "bucket_id", "bucket_display_name"), visible, null, null)?.use { cursor ->
            while (cursor.moveToNext()) {
                val id = cursor.getString(0) + ":" + cursor.getString(1)
                val album = albums.getOrPut(id) {
                    JSONObject().put("id", id).put("name", cursor.getString(2) ?: "Без альбома").put("count", 0)
                }
                album.put("count", album.getInt("count") + 1)
            }
        }
        return JSONArray(albums.values.sortedBy { it.getString("name").lowercase() })
    }

    fun page(album: String, before: String): JSONObject {
        val clauses = mutableListOf(visible)
        val arguments = mutableListOf<String>()
        if (album.isNotEmpty()) {
            val parts = album.split(':', limit = 2)
            require(parts.size == 2 && parts.all { it.isNotEmpty() })
            clauses.add("volume_name=? AND bucket_id=?")
            arguments.addAll(parts)
        }
        if (before.isNotEmpty()) {
            require(before.toLong() > 0)
            clauses.add("_id<?"); arguments.add(before)
        }
        val query = Bundle().apply {
            putString(ContentResolver.QUERY_ARG_SQL_SELECTION, clauses.joinToString(" AND "))
            putStringArray(ContentResolver.QUERY_ARG_SQL_SELECTION_ARGS, arguments.toTypedArray())
            putString(ContentResolver.QUERY_ARG_SQL_SORT_ORDER, "_id DESC")
            putInt(ContentResolver.QUERY_ARG_LIMIT, 121)
        }
        val items = JSONArray()
        var cursorId: String? = null
        var more = false
        context.contentResolver.query(collection, projection, query, null)?.use { cursor ->
            while (cursor.moveToNext()) {
                if (items.length() == 120) { more = true; break }
                items.put(file(cursor)); cursorId = cursor.getLong(0).toString()
            }
        }
        return JSONObject().put("items", items).put("next_cursor", if (more) cursorId else JSONObject.NULL)
    }

    fun resolve(raw: String): JSONObject {
        val uri = Uri.parse(raw)
        val parts = uri.pathSegments
        require(uri.scheme == "content" && uri.authority == "media" && uri.query == null && uri.fragment == null)
        require(parts.size == 4 && parts[1] in setOf("images", "video") && parts[2] == "media")
        val id = parts[3].toLong(); require(id > 0)
        val type = if (parts[1] == "images") "1" else "3"
        return context.contentResolver.query(collection, projection, "$visible AND _id=? AND volume_name=? AND media_type=?",
            arrayOf(id.toString(), parts[0], type), null)?.use { cursor ->
            require(cursor.moveToFirst()) { "Файл больше недоступен. Обновите выбор." }
            file(cursor).also { require(it.getString("uri") == raw) }
        } ?: throw IllegalArgumentException("Не удалось прочитать файл")
    }
}
