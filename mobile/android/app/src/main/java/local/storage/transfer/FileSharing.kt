package local.storage.transfer

import android.content.ClipData
import android.content.Context
import android.content.Intent
import android.os.Parcel
import android.webkit.MimeTypeMap
import androidx.core.content.FileProvider
import local.storage.security.ServerPolicy
import org.json.JSONObject
import java.io.File

object FileSharing {
    const val TTL=24L*60*60*1000
    fun file(context:Context,row:JSONObject):File {
        val batch=ServerPolicy.uuid(row.getString("share_batch"))
        val id=ServerPolicy.uuid(row.getString("id"))
        val extension=MimeTypeMap.getSingleton().getExtensionFromMimeType(row.getString("mime"))
            ?.takeIf { Regex("[a-zA-Z0-9]{1,12}").matches(it) }?:"bin"
        return File(context.filesDir,"shares/$batch/$id.$extension")
    }
    fun cleanup(context:Context,activeBatches:Set<String>) {
        File(context.filesDir,"shares").listFiles()?.forEach { folder ->
            if(folder.name !in activeBatches && System.currentTimeMillis()-folder.lastModified()>TTL)folder.deleteRecursively()
        }
    }
    fun intent(context:Context,rows:List<JSONObject>):Intent {
        require(rows.isNotEmpty() && rows.size<=100) { "Для одной отправки выберите не больше 100 файлов" }
        val uris=ArrayList(rows.map { row ->
            val source=file(context,row)
            require(source.isFile && source.length()==row.getLong("size")) { "Файлы отправки больше недоступны. Подготовьте их заново." }
            FileProvider.getUriForFile(context,"${context.packageName}.share",source,row.getString("name"))
        })
        val types=rows.map { it.getString("mime") }.distinct()
        val type=if(types.size==1)types.first() else if(types.map { it.substringBefore('/') }.distinct().size==1)types.first().substringBefore('/')+"/*" else "*/*"
        val send=Intent(if(uris.size==1)Intent.ACTION_SEND else Intent.ACTION_SEND_MULTIPLE).setType(type)
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        if(uris.size==1)send.putExtra(Intent.EXTRA_STREAM,uris.first()) else send.putParcelableArrayListExtra(Intent.EXTRA_STREAM,uris)
        send.clipData=ClipData.newUri(context.contentResolver,"storage",uris.first()).apply { uris.drop(1).forEach { addItem(ClipData.Item(it)) } }
        val chooser=Intent.createChooser(send,"Поделиться файлами").addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        chooser.clipData=send.clipData
        val parcel=Parcel.obtain()
        try { chooser.writeToParcel(parcel,0);require(parcel.dataSize()<256*1024) { "Слишком много файлов для одной отправки" } } finally { parcel.recycle() }
        return chooser
    }
}
