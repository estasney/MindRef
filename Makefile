PROJECT_NAME:=mindref
PROJECT_REQUIREMENTS=python3==3.10.13,hostpython3==3.10.13,kivy,python-dotenv,toolz,pygments,docutils,urllib3,chardet,idna,android,pillow,mistune==2.0.4,mindref_cython
UTIL_ROOT:=$(HOME)/AndroidStudioProjects/MindRefUtils
UTIL_OUTPUT:=$(UTIL_ROOT)/mindrefutils/build/outputs/aar
UTIL_AAR:=$(UTIL_OUTPUT)/mindrefutils-debug.aar
# https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile/23324703#23324703
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_ROOT:=$(ROOT_DIR)/src/$(PROJECT_NAME)
BUILD_REF_DIR:=$(ROOT_DIR)/scripts/build
SDK_DIR:=$(HOME)/Documents/Android/
NDK_DIR:=$(HOME)/Documents/Android/ndk/25.2.9519653

# APK
APK_VERSION ?= $(shell sed -e '1s/__version__ = //g' -e '1s/"//g' -e '2,//d' mindref/__version__.py)
NDK_VERSION ?= 29
SDK_VERSION ?= 34

# ADB
PYTHON_LOG_LEVEL ?= 'I'
JAVA_LOG_LEVEL ?= 'D'
OTHER_LOG_LEVEL ?= '*:S'
LOGCAT_FILTER ?= '$(OTHER_LOG_LEVEL) python:$(PYTHON_LOG_LEVEL) mindrefutils:$(JAVA_LOG_LEVEL)'

echo-vars:
	@echo PROJECT_ROOT = \"$(PROJECT_ROOT)\"
	@echo ROOT_DIR = \"$(ROOT_DIR)\"
	@echo BUILD_REF_DIR = \"$(BUILD_REF_DIR)\"
	@echo UTIL_ROOT = \"$(UTIL_ROOT)\"
	@echo UTIL_OUTPUT = \"$(UTIL_OUTPUT)\"
	@echo UTIL_AAR = \"$(UTIL_AAR)\"
	@echo APK_VERSION = \"$(APK_VERSION)\"
	@echo NDK_VERSION = \"$(NDK_VERSION)\"
	@echo SDK_VERSION = \"$(SDK_VERSION)\"
	@echo LOGCAT_FILTER = \"$(LOGCAT_FILTER)\"
.PHONY : echo-vars

clean-apk :
	find . -type f -name "*.apk" -delete
.PHONY : clean-apk

clean-aar :
	find $(UTIL_ROOT) -type f -name "*.aar" -delete
	find $(ROOT_DIR) -type f -name "*.aar" -delete
.PHONY : clean-aar

clean-bytecode :
	find $(PROJECT_ROOT) -name "*.pyc" -delete
	find $(PROJECT_ROOT) -name "__pycache__" -type d -print0 | xargs -0 rm -rf
	find $(PROJECT_ROOT) -name ".mypy_cache" -type d -print0 | xargs -0 rm -rf
.PHONY : clean-bytecode

clean-cythonized:
	find $(PROJECT_ROOT) -name "*.c" -delete
	find $(PROJECT_ROOT) -name "*.so" -delete
	find $(PROJECT_ROOT) -name "*.html" -delete
	. venv/bin/activate \
	&& p4a clean-recipe-build mindref_cython

clean-builds :
	. venv/bin/activate \
	&& p4a clean builds
.PHONY : clean-builds

clean-dists :
	. venv/bin/activate \
	&& p4a clean dists
.PHONY : clean-dists

clean-all : clean-aar clean-apk clean-bytecode clean-builds clean-dists clean-cythonized
	. venv/bin/activate \
	&& p4a clean-all
.PHONY : clean-all

*.aar : clean-aar
	cd $(UTIL_ROOT) \
		&& ./gradlew mindrefutils:build
	cp $(UTIL_AAR) .

cythonize:
	find ./src -name "*.pyx" -exec uv run python -m cython {} --3str \;

build-apk :  *.aar clean-bytecode clean-cythonized
	. venv/bin/activate \
	&& p4a apk --private $(PROJECT_ROOT) \
  	--package=org.test.mindref \
  	--name "MindRef" \
  	--version $(APK_VERSION) \
  	--bootstrap=sdl2 \
  	--window \
  	--dist-name=$(PROJECT_NAME) \
  	--sdk-dir $(HOME)/Documents/Android/ \
  	--ndk-dir ~/Documents/Android/ndk/25.2.9519653 \
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
  	--add-aar $(ROOT_DIR)/mindrefutils-debug.aar \
  	--no-byte-compile-python
.PHONY : build-apk

install :
	adb install mindref*.apk
.PHONY : install

install-run : install
	adb shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb logcat -c \
	&& adb logcat $(LOGCAT_FILTER)
.PHONY : install-run
