PROJECT_NAME:=mindref
PROJECT_REQUIREMENTS=python3==3.10.8,hostpython3==3.10.8,kivy,python-dotenv,toolz,pygments,docutils,urllib3,chardet,idna,android,pillow,mistune
UTIL_ROOT:=$(HOME)/AndroidStudioProjects/MindRefUtils
UTIL_OUTPUT:=$(UTIL_ROOT)/mindrefutils/build/outputs/aar
UTIL_AAR:=$(UTIL_OUTPUT)/mindrefutils-debug.aar
# https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile/23324703#23324703
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_ROOT:=$(ROOT_DIR)/$(PROJECT_NAME)

# APK
VERSION ?= 0.0.1
NDK_VERSION ?= 29
SDK_VERSION ?= 33

# ADB
LOGCAT_FILTER ?= '*:S python:I mindrefutils:D'

default_target : all
.PHONY : default_target

test-clean:
	echo $(PROJECT_ROOT)
.PHONY : test-clean

clean-apk :
	find . -type f -name "*.apk" -exec rm {} \;
.PHONY : clean-apk

clean-aar :
	find $(UTIL_ROOT) -type f -name "*.aar" -delete
	find $(ROOT_DIR) -type f -name "*.aar" -delete
.PHONY : clean-aar

clean-bytecode :
	find $(PROJECT_ROOT) -name "*.pyc" -delete
	find $(PROJECT_ROOT) -name "__pycache__" -delete
.PHONY : clean-bytecode

clean-builds :
	. venv/bin/activate \
	&& python -m pythonforandroid.entrypoints clean builds
.PHONY : clean-builds

clean-dists :
	. venv/bin/activate \
	&& python -m pythonforandroid.entrypoints clean dists
.PHONY : clean-dists

clean-all : clean-aar clean-apk clean-bytecode clean-builds clean-dists
	. venv/bin/activate \
	&& python -m pythonforandroid.entrypoints clean-all
.PHONY : clean-all

*.aar : clean-aar
	cd $(UTIL_ROOT) \
		&& ./gradlew :mindrefutils:build
	cp $(UTIL_AAR) .

build-apk :  *.aar
	. venv/bin/activate \
	&& python -m pythonforandroid.entrypoints apk --private $(PROJECT_ROOT) \
  	--package=org.test.mindref \
  	--name "MindRef" \
  	--version $(VERSION) \
  	--bootstrap=sdl2 \
  	--dist-name=$(PROJECT_NAME) \
  	--sdk-dir ~/Android/Sdk \
  	--ndk-dir ~/Android/Sdk/ndk/25.1.8937393 \
  	--ndk-api $(NDK_VERSION) \
  	--android-api $(SDK_VERSION) \
  	--requirements=$(PROJECT_REQUIREMENTS) \
  	--arch arm64-v8a \
  	--arch x86_64 \
  	--enable-androidx \
  	--presplash $(PROJECT_ROOT)/assets/presplash.png \
  	--icon $(PROJECT_ROOT)/assets/logo.png \
  	--depend "com.google.guava:guava:31.1-android" \
  	--depend "org.apache.commons:commons-io:1.3.2" \
  	--add-aar $(ROOT_DIR)/mindrefutils-debug.aar


install : build-apk
	adb install mindref*.apk
.PHONY : install

install-run : install
	adb shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb logcat -c \
	&& adb logcat $(LOGCAT_FILTER)
.PHONY : install-run


all: clean-all build-apk install-run
