# https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile/23324703#23324703

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR:=$(ROOT_DIR)/build_p4a
SCRIPT_DIR:=$(ROOT_DIR)/scripts

UTIL_ROOT:=$(HOME)/AndroidStudioProjects/MindRefUtils
UTIL_OUTPUT:=$(UTIL_ROOT)/mindrefutils/build/outputs/aar
MINDREF_UTILS_DEBUG:=mindrefutils-debug.aar

PROJECT_NAME:=mindref
PROJECT_NAME_READABLE:=MindRef
PROJECT_JAVA_PACKAGE:=org.test.mindref
PROJECT_REQUIREMENTS=kivy,python-dotenv,toolz,pygments,pillow,mistune==2.0.5,mindref_android
PROJECT_ROOT:=$(ROOT_DIR)/src/mindref
PROJECT_VERSION ?= $(shell python3.12 -c "import tomllib;fp=open('pyproject.toml', 'rb');d=tomllib.load(fp);print(d['project']['version']);fp.close()" )

PRIVATE_DIR:=$(BUILD_DIR)
PRIVATE_ENTRYPOINT_SRC:=$(SCRIPT_DIR)/build/main.py
PRIVATE_ENTRYPOINT_DEST:=$(BUILD_DIR)/main.py

PYX_FILES := $(wildcard $(PROJECT_ROOT)/lib/**/*.pyx)
PYX_C_FILES := $(PYX_FILES:.pyx=.c)

PRESPLASH_SRC:= $(PROJECT_ROOT)/assets/presplash.png
PRESPLASH_DEST:= $(BUILD_DIR)/assets/presplash.png
ICON_SRC:= $(PROJECT_ROOT)/assets/logo.png
ICON_DEST:= $(BUILD_DIR)/assets/logo.png
ASSET_MATERIAL_TTF_SRC:= $(PROJECT_ROOT)/assets/MaterialIcons.ttf
ASSET_MATERIAL_TTF_DEST:= $(BUILD_DIR)/assets/MaterialIcons.ttf
ASSET_ROBOTO_TTF_SRC:= $(PROJECT_ROOT)/assets/RobotoMono-Regular.ttf
ASSET_ROBOTO_TTF_DEST:= $(BUILD_DIR)/assets/RobotoMono-Regular.ttf

NDK_VERSION:=25.2.9519653
SDK_DIR:=$(HOME)/.android
NDK_DIR:=$(HOME)/.android/ndk/$(NDK_VERSION)
NDK_API ?= 29
SDK_VERSION ?= 34


MINDREF_APK := $(PROJECT_NAME)-debug-$(PROJECT_VERSION).apk
UNPACK_DIR := $(HOME)/Downloads/apk

# ADB
PYTHON_LOG_LEVEL ?= 'I'
JAVA_LOG_LEVEL ?= 'D'
OTHER_LOG_LEVEL ?= '*:S'
LOGCAT_FILTER ?= '$(OTHER_LOG_LEVEL) python:$(PYTHON_LOG_LEVEL) mindrefutils:$(JAVA_LOG_LEVEL)'

LOCAL_RECIPES:=$(ROOT_DIR)/p4a-recipes



