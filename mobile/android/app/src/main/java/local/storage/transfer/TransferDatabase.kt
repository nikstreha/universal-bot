package local.storage.transfer

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import org.json.JSONArray
import org.json.JSONObject

class TransferDatabase(context: Context) : SQLiteOpenHelper(context, "transfer.sqlite3", null, 2) {
    companion object {
        private val TERMINAL = setOf("done", "kept_local", "cancelled")
        private const val HISTORY_TTL_MS = 7L * 24 * 60 * 60 * 1000
    }
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("CREATE TABLE transfer(id TEXT PRIMARY KEY,owner_id TEXT NOT NULL,state TEXT NOT NULL,payload TEXT NOT NULL,created_at INTEGER NOT NULL,finished_at INTEGER)")
        db.execSQL("CREATE INDEX transfer_finished_at ON transfer(finished_at)")
    }
    override fun onUpgrade(db: SQLiteDatabase, old: Int, new: Int) {
        if (old < 2) {
            db.execSQL("ALTER TABLE transfer ADD COLUMN finished_at INTEGER")
            // Old records have no completion time. Preserve them for one week after migration.
            db.execSQL("UPDATE transfer SET finished_at=? WHERE state IN ('done','kept_local','cancelled')", arrayOf(System.currentTimeMillis()))
            db.execSQL("CREATE INDEX transfer_finished_at ON transfer(finished_at)")
        }
    }
    private fun pruneHistory() {
        writableDatabase.delete("transfer", "finished_at<=? AND state IN ('done','kept_local','cancelled')",
            arrayOf((System.currentTimeMillis() - HISTORY_TTL_MS).toString()))
    }
    @Synchronized fun add(row: JSONObject) {
        writableDatabase.insertOrThrow("transfer", null, ContentValues().apply {
            put("id", row.getString("id")); put("owner_id", row.getString("owner_id")); put("state", row.getString("state"))
            put("payload", row.toString()); put("created_at", System.currentTimeMillis())
            if (row.getString("state") in TERMINAL) put("finished_at", System.currentTimeMillis())
        })
    }
    @Synchronized fun addAll(rows:List<JSONObject>) {
        val db=writableDatabase;db.beginTransaction()
        try { rows.forEach { add(it) };db.setTransactionSuccessful() } finally { db.endTransaction() }
    }
    @Synchronized fun get(id: String): JSONObject? = readableDatabase.rawQuery("SELECT payload FROM transfer WHERE id=?", arrayOf(id)).use { if(it.moveToFirst()) JSONObject(it.getString(0)) else null }
    @Synchronized fun rows(owner: String, baseUrl: String): List<JSONObject> {
        pruneHistory()
        return readableDatabase.rawQuery("SELECT payload FROM transfer WHERE owner_id=? ORDER BY created_at", arrayOf(owner)).use { cursor ->
        buildList { while(cursor.moveToNext()) {
            val row=JSONObject(cursor.getString(0))
            if(row.optString("base_url")==baseUrl.trimEnd('/')) add(row)
        } }
        }
    }
    @Synchronized fun patch(id: String, changes: JSONObject, allowed: Set<String>? = null): Boolean {
        val db = writableDatabase; db.beginTransaction()
        try {
            val row = get(id) ?: return false
            if(allowed != null && row.getString("state") !in allowed) return false
            val wasTerminal = row.getString("state") in TERMINAL
            changes.keys().forEach { row.put(it, changes.get(it)) }
            db.update("transfer", ContentValues().apply {
                put("state",row.getString("state")); put("payload",row.toString())
                if (row.getString("state") !in TERMINAL) putNull("finished_at")
                else if (!wasTerminal) put("finished_at", System.currentTimeMillis())
            }, "id=?",arrayOf(id))
            db.setTransactionSuccessful(); return true
        } finally { db.endTransaction() }
    }
    fun patch(id: String, state: String) = patch(id, JSONObject().put("state",state))
}
