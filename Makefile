#include $(wildcard makefiles/*.mk)
include makefiles/vars.mk
include makefiles/prebuild.mk
include makefiles/apk.mk

echo-vars:
	@echo PROJECT_ROOT = \"$(PROJECT_ROOT)\"
	@echo ROOT_DIR = \"$(ROOT_DIR)\"
	@echo LOCAL_RECIPES = \"$(LOCAL_RECIPES)\"
	@echo UTIL_ROOT = \"$(UTIL_ROOT)\"
	@echo UTIL_OUTPUT = \"$(UTIL_OUTPUT)\"
	@echo PROJECT_VERSION = \"$(PROJECT_VERSION)\"
	@echo NDK_VERSION = \"$(NDK_VERSION)\"
	@echo NDK_API = \"$(NDK_API)\"
	@echo SDK_VERSION = \"$(SDK_VERSION)\"
	@echo LOGCAT_FILTER = \"$(LOGCAT_FILTER)\"
	@echo PYX_FILES = \"$(PYX_FILES)\"
	@echo MINDREF_APK = \"$(MINDREF_APK)\"
.PHONY : echo-vars


install :
	adb -d install mindref*.apk
.PHONY : install

install-run : install
	adb -d shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb -d logcat -c \
	&& adb -d logcat $(LOGCAT_FILTER)
.PHONY : install-run
