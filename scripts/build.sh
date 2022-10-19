#!/bin/bash

# No implementation found for void org.libsdl.app.SDLActivity.nativePermissionResult(int, boolean) (tried Java_org_libsdl_app_SDLActivity_nativePermissionResult and Java_org_libsdl_app_SDLActivity_nativePermissionResult__IZ)

set -euo pipefail

cd mindref || exit
find . -name "__pycache__" -exec rm -rf {} \;
find . -name "*.pyc" -exec rm {} \;

python -m pythonforandroid.entrypoints apk --private . \
  --package=org.test.mindref \
  --name "MindRef" \
  --version 0.0.4 \
  --bootstrap=sdl2 \
  --dist-name=mindref \
  --sdk-dir "$HOME/Android/Sdk" \
  --ndk-dir "$HOME/Android/android-ndk-r25" \
  --ndk-api 23 \
  --android-api 33 \
  --requirements=python3==3.10.8,hostpython3==3.10.8,kivy,python-dotenv,toolz,pygments,docutils,urllib3,chardet,idna,android,pillow,mistune \
  --arch arm64-v8a \
  --presplash ../mindref/assets/presplash.png \
  --icon ../mindref/assets/logo.png \
  --enable-androidx \
  --depend "androidx.documentfile:documentfile:1.0.1" \
  --depend "com.google.guava:guava:31.1-android" \
  --depend "org.apache.commons:commons-io:1.3.2" \
  --add-aar /home/eric/AndroidStudioProjects/MindRefUtils/mindrefutils/build/outputs/aar/mindrefutils-debug.aar \
  && adb install mindref*.apk \
  && adb logcat -c \
  && adb logcat *:S python:D PythonActivity:V SDLActivity:V
