PROJECT_ROOT=mindref
PROJECT_REQUIREMENTS=python3==3.10.8,hostpython3==3.10.8,kivy,python-dotenv,toolz,pygments,docutils,urllib3,chardet,idna,android,pillow,mistune
UTIL_ROOT:=$(HOME)/AndroidStudioProjects/MindRefUtils
UTIL_OUTPUT:=$(UTIL_ROOT)/mindrefutils/build/outputs/aar
UTIL_AAR:=$(UTIL_OUTPUT)/mindrefutils-debug.aar
HERE=$(shell pwd)

default_target : all
.PHONY : default_target

clean-apk :
	find . -type f -name "*.apk" -exec rm {} \;
.PHONY : clean-apk

clean-aar :
	find $(UTIL_ROOT) -type f -name "*.aar" -exec rm {} \;
	find . -type f -name "*.aar" -exec rm {} \;
.PHONY : clean-aar

clean-bytecode :
	find $(PROJECT_ROOT) -name "__pycache__" -exec rm -rf {} \;
	find $(PROJECT_ROOT) -name "*.pyc" -exec rm {} \;
.PHONY : clean-bytecode

clean-builds :
	. venv10/bin/activate \
	&& python -m pythonforandroid.entrypoints clean builds
.PHONY : clean-builds

clean-dists :
	. venv10/bin/activate \
	&& python -m pythonforandroid.entrypoints clean builds
.PHONY : clean-dists

clean-all : clean-aar clean-apk clean-bytecode clean-builds clean-dists
	. venv10/bin/activate \
	&& python -m pythonforandroid.entrypoints clean-all
.PHONY : clean-all

*.aar : clean-aar
	@echo Building aar
	cd $(UTIL_ROOT) \
		&& ./gradlew :mindrefutils:build
	cp $(UTIL_AAR) .

build-apk :  *.aar
	. venv10/bin/activate \
	&& python -m pythonforandroid.entrypoints apk --private $(PROJECT_ROOT) \
  	--package=org.test.mindref \
  	--name "MindRef" \
  	--version 0.0.4 \
  	--bootstrap=sdl2 \
  	--dist-name=$(PROJECT_ROOT) \
  	--sdk-dir ~/Android/Sdk \
  	--ndk-dir ~/Android/android-ndk-r25 \
  	--ndk-api 29 \
  	--android-api 33 \
  	--requirements=$(PROJECT_REQUIREMENTS) \
  	--arch arm64-v8a \
  	--arch x86_64 \
  	--presplash ./$(PROJECT_ROOT)/assets/presplash.png \
  	--icon ./$(PROJECT_ROOT)/assets/logo.png \
  	--depend "com.google.guava:guava:31.1-android" \
  	--depend "org.apache.commons:commons-io:1.3.2" \
  	--add-aar $(HERE)/mindrefutils-debug.aar


install : build-apk
	adb install mindref*.apk
.PHONY : install

install-run : install
	adb shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb logcat -c \
	&& adb logcat *:S python:V mindrefutils:D
