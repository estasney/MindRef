#!/bin/bash

python -m pythonforandroid.entrypoints apk --private ../mindref \
  --package=org.test.mindref \
  --name "MindRef" \
  --version 0.0.2 \
  --bootstrap=sdl2 \
  --dist_name=mindref \
  --sdk-dir "$HOME/Android/Sdk" \
  --ndk-dir "$HOME/.buildozer/android/platform/android-ndk-r25b" \
  --android_api 33 \
  --ndk-api 23 \
  --requirements=python3==3.10.7,hostpython3==3.10.7,kivy,python-dotenv,toolz,pygments,docutils,urllib3,chardet,idna,android,pillow,mistune,lxml \
  --arch arm64-v8a \
  --presplash ../mindref/assets/presplash.png \
  --icon ../mindref/assets/logo.png \
  --permission INTERNET \
  --permission WRITE_EXTERNAL_STORAGE \
  --permission READ_EXTERNAL_STORAGE \
  --permission MANAGE_EXTERNAL_STORAGE \
  && adb install mindref*.apk \
  && adb logcat *:S python:D
