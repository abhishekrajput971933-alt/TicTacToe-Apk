[app]

# (str) Title of your application
title = Tic Tac Toe

# (str) Package name
package.name = tictactoe

# (str) Package domain
package.domain = com.redboxmovie

# (str) Source code directory
source.dir = .

# (str) Main Python file
source.main = main.py

# (str) Files to include in the APK
source.include_exts = py,png,jpg,jpeg,json,mp3,wav

# (str) Application version
version = 1.0

# (str) Python dependencies
requirements = python3,pygame

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 1

# (str) Application icon
icon.filename = %(source.dir)s/icon.png

# (str) Presplash
presplash.filename = %(source.dir)s/presplash.png


[buildozer]

# (str) Log level
log_level = 2

# (bool) Warn about root user
warn_on_root = 1


[app:android]

# (str) Android API
android.api = 35

# (str) Android minimum API
android.minapi = 23

# (str) Android architecture
android.arch = arm64-v8a

# (str) Android orientation
orientation = portrait

# (bool) Android fullscreen
fullscreen = 1
