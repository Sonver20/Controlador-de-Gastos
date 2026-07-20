[app]
title = Meu App de Gastos
package.name = gastosteste
package.domain = org.exemplo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3==3.11.0, hostpython3==3.11.0, kivy==2.3.1, kivymd==1.2.0, pyjnius
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
# (list) List of Java source to split
android.add_src = src/java
# (str) XML to add to the <application> tag
android.manifest.application = <service android:name="org.exemplo.gastosteste.NotificationReceiver" android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE" android:exported="true"><intent-filter><action android:name="android.service.notification.NotificationListenerService" /></intent-filter></service>
