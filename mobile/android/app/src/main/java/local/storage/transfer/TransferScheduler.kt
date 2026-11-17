package local.storage.transfer

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.job.JobInfo
import android.app.job.JobParameters
import android.app.job.JobScheduler
import android.app.job.JobService
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.Constraints
import androidx.work.ExistingWorkPolicy
import androidx.work.ForegroundInfo
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import local.storage.MainActivity
import org.json.JSONObject
import java.util.concurrent.Executors

object TransferScheduler {
    const val NOTIFICATION=1008
    fun notification(context: Context): Notification {
        val manager=context.getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel("transfer","Передача файлов",NotificationManager.IMPORTANCE_LOW))
        val open=PendingIntent.getActivity(context,0,Intent(context,MainActivity::class.java),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        fun action(name: String, code: Int)=PendingIntent.getBroadcast(context,code,Intent(context,TransferActions::class.java).setAction(name),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        return NotificationCompat.Builder(context,"transfer").setSmallIcon(android.R.drawable.stat_sys_upload)
            .setContentTitle("storage · передача файлов").setContentText("Загрузка и проверка серверных копий")
            .setContentIntent(open).setOngoing(true).setOnlyAlertOnce(true)
            .addAction(android.R.drawable.ic_media_pause,"Пауза",action("pause",1))
            .addAction(android.R.drawable.ic_menu_close_clear_cancel,"Отмена",action("cancel",2)).build()
    }
    fun kick(context: Context) {
        val session=SecureStore(context).read("session")?:return
        val pending=TransferDatabase(context).rows(session.getString("userId")).any { it.getString("state") in TransferEngine.RUNNABLE }
        if(!pending)return
        if(Build.VERSION.SDK_INT>=34) {
            val job=JobInfo.Builder(1007,ComponentName(context,TransferJobService::class.java))
                .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY).setUserInitiated(true).build()
            try { context.getSystemService(JobScheduler::class.java).schedule(job) } catch (_: IllegalStateException) { /* Resume on the next visible user action. */ }
        } else {
            val work=OneTimeWorkRequestBuilder<TransferWorker>().setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()).build()
            WorkManager.getInstance(context).enqueueUniqueWork("storage-transfer",ExistingWorkPolicy.KEEP,work)
        }
    }
}

class TransferWorker(context: Context,params: WorkerParameters):Worker(context,params) {
    override fun doWork(): Result {
        setForegroundAsync(ForegroundInfo(TransferScheduler.NOTIFICATION,TransferScheduler.notification(applicationContext),ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)).get()
        return if(TransferEngine(applicationContext).run()) Result.retry() else Result.success()
    }
}

class TransferJobService:JobService() {
    private val executor=Executors.newSingleThreadExecutor()
    override fun onStartJob(params: JobParameters): Boolean {
        if(Build.VERSION.SDK_INT>=34) setNotification(params,TransferScheduler.NOTIFICATION,TransferScheduler.notification(this),JOB_END_NOTIFICATION_POLICY_REMOVE)
        executor.execute { val retry=TransferEngine(this).run(); jobFinished(params,retry) }
        return true
    }
    override fun onStopJob(params: JobParameters):Boolean = true
    override fun onDestroy() { executor.shutdown(); super.onDestroy() }
}

class TransferActions:BroadcastReceiver() {
    override fun onReceive(context:Context,intent:Intent) {
        val session=SecureStore(context).read("session")?:return
        val db=TransferDatabase(context)
        db.rows(session.getString("userId")).filter { it.getString("state") in TransferEngine.RUNNABLE }.forEach {
            db.patch(it.getString("id"),if(intent.action=="cancel")"cancelled" else "paused")
        }
    }
}
