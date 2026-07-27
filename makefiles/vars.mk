# https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile/23324703#23324703

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR:=$(ROOT_DIR)/build_p4a
SCRIPT_DIR:=$(ROOT_DIR)/scripts
P4A_HOOKS_DIR:=$(SCRIPT_DIR)/p4a
P4A_HOOKS_FILE:=$(P4A_HOOKS_DIR)/hook.py

UTIL_ROOT:=$(HOME)/AndroidStudioProjects/MindRefUtils
UTIL_OUTPUT:=$(UTIL_ROOT)/mindrefutils/build/outputs/aar
MINDREF_UTILS_DEBUG:=mindrefutils-debug.aar
MINDREF_UTILS_RELEASE:=mindrefutils-release.aar

PROJECT_NAME:=mindref
PROJECT_NAME_READABLE:=MindRef
PROJECT_JAVA_PACKAGE:=org.test.mindref
PROJECT_JAVA_HOME:=/usr/lib/jvm/java-17-openjdk-amd64
PROJECT_REQUIREMENTS='kivy==2.3.1',python-dotenv,pygments,pillow,mistune==2.0.5,mindref_android,filetype
PROJECT_ROOT:=$(ROOT_DIR)/src/mindref
PROJECT_VERSION ?= $(shell python3.12 -c "import tomllib;fp=open('pyproject.toml', 'rb');d=tomllib.load(fp);print(d['project']['version']);fp.close()" )

PRIVATE_DIR:=$(BUILD_DIR)
PRIVATE_ENTRYPOINT_SRC:=$(ROOT_DIR)/p4a-recipes/mindref_android/main.py
PRIVATE_ENTRYPOINT_DEST:=$(BUILD_DIR)/main.py

PYX_FILES := $(wildcard $(PROJECT_ROOT)/lib/**/*.pyx)
PYX_C_FILES := $(PYX_FILES:.pyx=.c)

PRESPLASH_SRC:= $(PROJECT_ROOT)/assets/presplash.png
PRESPLASH_DEST:= $(BUILD_DIR)/assets/presplash.png
ICON_SRC:= $(PROJECT_ROOT)/assets/logo.png
ICON_DEST:= $(BUILD_DIR)/assets/logo.png
ASSET_MATERIAL_TTF_SRC:= $(PROJECT_ROOT)/assets/MaterialIcons.ttf
ASSET_MATERIAL_TTF_DEST:= $(BUILD_DIR)/assets/MaterialIcons.ttf
ASSET_MONO_TTF_SRC:= $(PROJECT_ROOT)/assets/JetBrainsMono-Regular.ttf
ASSET_MONO_TTF_DEST:= $(BUILD_DIR)/assets/JetBrainsMono-Regular.ttf

NDK_VERSION:=28.2.13676358
SDK_DIR:=$(HOME)/.android
NDK_DIR:=$(HOME)/.android/ndk/$(NDK_VERSION)
NDK_API ?= 29
SDK_VERSION ?= 35
BUILD_TOOLS_DIR:=$(SDK_DIR)/build-tools/$(SDK_VERSION).0.0


# Debug builds include x86_64 so they run on the emulator; release targets
# hardware only, which keeps the shipped APK to a single architecture.
DEBUG_ARCHS ?= --arch arm64-v8a --arch x86_64
RELEASE_ARCHS ?= --arch arm64-v8a

MINDREF_DEBUG_APK := $(PROJECT_NAME)-debug-$(PROJECT_VERSION).apk
MINDREF_RELEASE_UNSIGNED_APK := $(PROJECT_NAME)-release-unsigned-$(PROJECT_VERSION).apk
MINDREF_RELEASE_ALIGNED_APK := $(PROJECT_NAME)-release-aligned-$(PROJECT_VERSION).apk
MINDREF_RELEASE_SIGNED_APK := $(PROJECT_NAME)-release-signed-$(PROJECT_VERSION).apk
UNPACK_DIR := $(HOME)/Downloads/apk

# ADB
# -d targets a USB device, -e an emulator
ADB_TARGET ?= -d
AVD_NAME ?= Pixel_10_Pro
EMULATOR_BIN := $(SDK_DIR)/emulator/emulator
PYTHON_LOG_LEVEL ?= 'I'
JAVA_LOG_LEVEL ?= 'D'
OTHER_LOG_LEVEL ?= '*:S'
LOGCAT_FILTER ?= '$(OTHER_LOG_LEVEL) python:$(PYTHON_LOG_LEVEL) mindrefutils:$(JAVA_LOG_LEVEL)'

LOCAL_RECIPES:=$(ROOT_DIR)/p4a-recipes



