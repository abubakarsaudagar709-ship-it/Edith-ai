[app]

title = Edith
package.name = edith
package.domain = org.abubakarsaudagar

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,plyer,certifi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
