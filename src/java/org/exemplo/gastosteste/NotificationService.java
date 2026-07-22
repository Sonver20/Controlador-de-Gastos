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
            String pacote = sbn.getPackageName();
            String texto = "";
        
            if (sbn.getNotification().extras != null) {
                CharSequence title = sbn.getNotification().extras.getCharSequence("android.title");
                CharSequence text = sbn.getNotification().extras.getCharSequence("android.text");
                texto = (title != null ? title.toString() : "") + " - " + (text != null ? text.toString() : "");
            }

        // Formato: pacote|texto_da_notificacao
        String linha = pacote + "|" + texto + "\n";
        
        // Salva na pasta interna /data/data/org.exemplo.gastosteste/files/notificacoes_log.txt
        File internalDir = getFilesDir();
        File logFile = new File(internalDir, "notificacoes_log.txt");
        FileWriter writer = new FileWriter(logFile, true);
        writer.append(linha);
        writer.flush();
        writer.close();
    } catch (Exception e) {
        e.printStackTrace();
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
        // Usa o armazenamento INTERNO do app (não requer permissões)
        File internalDir = getFilesDir();
        File logFile = new File(internalDir, "notificacoes_log.txt");
        FileWriter writer = new FileWriter(logFile, true);
        writer.append(text);
        writer.flush();
        writer.close();
    } catch (Exception e) {
        e.printStackTrace();
    }
 }

