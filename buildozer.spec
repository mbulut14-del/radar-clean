[app]
title = Hype Short Radar
package.name = hype_short_radar
package.domain = org.test

source.dir = .
source.include_exts = py

version = 0.1

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
