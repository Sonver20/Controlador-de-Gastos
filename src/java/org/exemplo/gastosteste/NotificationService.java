package org.exemplo.gastosteste;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.os.Environment;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.StringWriter;

public class NotificationService extends NotificationListenerService {

    @Override
    public void onCreate() {
        try {
            super.onCreate();
            logToFile("INFO: NotificationService onCreate executado com sucesso.");
        } catch (Throwable t) {
            logErrorToFile(t);
        }
    }

    @Override
    public void onListenerConnected() {
        try {
            super.onListenerConnected();
            logToFile("INFO: Serviço conectado ao sistema de notificações!");
        } catch (Throwable t) {
            logErrorToFile(t);
        }
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        try {
            // Lógica do seu leitor aqui
        } catch (Throwable t) {
            logErrorToFile(t);
        }
    }

    private void logToFile(String message) {
        saveText(message + "\n");
    }

    private void logErrorToFile(Throwable t) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        t.printStackTrace(pw);
        saveText("ERRO CRÍTICO:\n" + sw.toString() + "\n---------------------\n");
    }

    private synchronized void saveText(String text) {
        try {
            File downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
            File logFile = new File(downloadsDir, "meu_app_erro.txt");
            FileWriter writer = new FileWriter(logFile, true);
            writer.append(text);
            writer.flush();
            writer.close();
        } catch (Exception ignored) {
        }
    }
}
