#include $(wildcard makefiles/*.mk)
include makefiles/vars.mk
include makefiles/secrets.mk
include makefiles/prebuild.mk
include makefiles/apk.mk
include makefiles/aar.mk
include makefiles/desktop.mk


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


emulator :
	$(EMULATOR_BIN) -avd $(AVD_NAME) &
.PHONY : emulator

install :
	adb $(ADB_TARGET) install -r -d $(MINDREF_DEBUG_APK)
.PHONY : install

install-emulator : ADB_TARGET := -e
install-emulator : install
.PHONY : install-emulator

install-release:
	adb $(ADB_TARGET) install -r $(MINDREF_RELEASE_SIGNED_APK)
.PHONY : install-release

uninstall :
	adb $(ADB_TARGET) uninstall org.test.mindref || true
.PHONY : uninstall

install-run : install
	adb $(ADB_TARGET) shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb $(ADB_TARGET) logcat -c \
	&& adb $(ADB_TARGET) logcat $(LOGCAT_FILTER)
.PHONY : install-run


install-run-release : install-release
	adb $(ADB_TARGET) shell am start -n org.test.mindref/org.kivy.android.PythonActivity \
	&& adb $(ADB_TARGET) logcat -c \
	&& adb $(ADB_TARGET) logcat $(LOGCAT_FILTER)