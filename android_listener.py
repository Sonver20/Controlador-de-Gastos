from jnius import autoclass, PythonJavaClass, java_method

# Importa as classes nativas do ecossistema Android através do JNI (Java Native Interface)
NotificationListenerService = autoclass('android.service.notification.NotificationListenerService')
StatusBarNotification = autoclass('android.service.notification.StatusBarNotification')

class AndroidNotificationListener(PythonJavaClass):
    """
    Esta classe se disfarça de código Java para o Android aceitá-la
    como um ouvinte oficial de notificações do sistema.
    """
    __javainterfaces__ = ['android/service/notification/NotificationListenerService']
    __javacontext__ = 'app'

    @java_method('(Landroid/service/notification/StatusBarNotification;)V')
    def onNotificationPosted(self, sbn):
        """Método nativo disparado pelo Android SEMPRE que qualquer push chega no celular."""
        try:
            # Extrai os dados puros da estrutura Java do Android
            pacote = sbn.getPackageName()
            notification = sbn.getNotification()
            extras = notification.extras
            
            # Captura o título e o texto do push
            titulo = extras.getString("android.title")
            texto = extras.getString("android.text")
            
            print(f"[Nativo] Capturado de {pacote}: {titulo} - {texto}")
            
            # Aqui chamamos o seu processador de Regex idêntico ao que já criamos
            from notification_processor import NotificationProcessor
            processor = NotificationProcessor()
            processor.processar_notificacao(pacote, texto)
            
        except Exception as e:
            print(f"[Erro Nativo] Falha ao processar evento de notificação: {e}")

    @java_method('(Landroid/service/notification/StatusBarNotification;)V')
    def onNotificationRemoved(self, sbn):
        # Obrigatório implementar pela interface do Java, mas podemos deixar vazio
        pass