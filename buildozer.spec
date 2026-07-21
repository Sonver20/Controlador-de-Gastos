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
android.add_src = src/java
android.permissions = POST_NOTIFICATIONS
# Instrui o python-for-android a buscar templates customizados na pasta templates/
p4a.template_dir = templates

