clean-apk :
	@echo "Cleaning APK files..."
	rm -f $(wildcard *.apk)
.PHONY : clean-apk


clean-all : clean-aar clean-apk clean-bytecode clean-builds clean-dists
	uv run --group android p4a clean-all
.PHONY : clean-all

clean-builds:
	uv run --group android p4a clean builds
.PHONY : clean-builds

clean-bootstraps:
	uv run --group android p4a clean bootstrap_builds
.PHONY : clean-bootstraps

clean-dists:
	uv run --group android p4a clean dists
.PHONY : clean-dists


build-apk :  $(MINDREF_UTILS_DEBUG) clean-bytecode prebuild clean-dists
	JAVA_HOME=$(PROJECT_JAVA_HOME) PIP_CONSTRAINT=$(PIP_CONSTRAINTS_FILE) uv run --group android p4a apk --private $(BUILD_DIR) \
  	--package=$(PROJECT_JAVA_PACKAGE) \
  	--name $(PROJECT_NAME_READABLE) \
  	--version $(PROJECT_VERSION) \
  	--bootstrap=sdl2 \
  	--window \
  	--dist-name=$(PROJECT_NAME) \
  	--sdk-dir $(SDK_DIR) \
  	--ndk-dir $(NDK_DIR) \
  	--ndk-api $(NDK_API) \
  	--android-api $(SDK_VERSION) \
  	$(DEBUG_ARCHS) \
  	--requirements=$(PROJECT_REQUIREMENTS) \
  	--enable-androidx \
  	--presplash $(PROJECT_ROOT)/assets/presplash.png \
  	--presplash-color '#37464F' \
  	--icon $(PROJECT_ROOT)/assets/logo.png \
  	--icon-fg $(PROJECT_ROOT)/assets/icon_fg.png \
  	--icon-bg $(PROJECT_ROOT)/assets/icon_bg.png \
  	--depend "com.google.guava:guava:31.1-android" \
  	--depend "org.apache.commons:commons-io:1.3.2" \
  	--depend "androidx.core:core:1.13.1" \
  	--add-aar $(ROOT_DIR)/$(MINDREF_UTILS_DEBUG) \
  	--no-byte-compile-python \
  	--add-compile-option "sourceCompatibility=17" \
  	--add-compile-option "targetCompatibility=17" \
  	--local-recipes $(LOCAL_RECIPES) \
  	--hook $(P4A_HOOKS_FILE)
  	
.PHONY : build-apk



$(MINDREF_RELEASE_UNSIGNED_APK) : $(MINDREF_UTILS_RELEASE) clean-bytecode prebuild clean-dists
	JAVA_HOME=$(PROJECT_JAVA_HOME) \
 	PIP_CONSTRAINT=$(PIP_CONSTRAINTS_FILE) \
 	uv run --group android p4a apk --private $(BUILD_DIR) \
  	--package=$(PROJECT_JAVA_PACKAGE) \
  	--name $(PROJECT_NAME_READABLE) \
  	--version $(PROJECT_VERSION) \
  	--bootstrap=sdl2 \
  	--window \
  	--dist-name=$(PROJECT_NAME) \
  	--sdk-dir $(SDK_DIR) \
  	--ndk-dir $(NDK_DIR) \
  	--ndk-api $(NDK_API) \
  	--android-api $(SDK_VERSION) \
  	$(RELEASE_ARCHS) \
  	--requirements=$(PROJECT_REQUIREMENTS) \
  	--enable-androidx \
  	--presplash $(PROJECT_ROOT)/assets/presplash.png \
  	--presplash-color '#37464F' \
  	--icon $(PROJECT_ROOT)/assets/logo.png \
  	--icon-fg $(PROJECT_ROOT)/assets/icon_fg.png \
  	--icon-bg $(PROJECT_ROOT)/assets/icon_bg.png \
  	--depend "com.google.guava:guava:31.1-android" \
  	--depend "org.apache.commons:commons-io:1.3.2" \
  	--depend "androidx.core:core:1.13.1" \
  	--add-aar $(ROOT_DIR)/$(MINDREF_UTILS_RELEASE) \
  	--no-byte-compile-python \
  	--add-compile-option "sourceCompatibility=17" \
  	--add-compile-option "targetCompatibility=17" \
  	--local-recipes $(LOCAL_RECIPES) \
  	--hook $(P4A_HOOKS_FILE) \
  	--keystore $(KEYSTORE_FILE) \
  	--signkey mindref \
  	--keystorepw $(KEYSTORE_PASSWORD) \
  	--release
  	
$(MINDREF_RELEASE_ALIGNED_APK): $(MINDREF_RELEASE_UNSIGNED_APK)
	$(BUILD_TOOLS_DIR)/zipalign -p -f 4 $< $@

$(MINDREF_RELEASE_SIGNED_APK): $(MINDREF_RELEASE_ALIGNED_APK)
	$(BUILD_TOOLS_DIR)/apksigner sign --ks $(KEYSTORE_FILE) \
	--ks-key-alias mindref \
	--ks-pass pass:$(KEYSTORE_PASSWORD) \
	--out $@ $<


build-apk-release: $(MINDREF_RELEASE_SIGNED_APK)
.PHONY : build-apk-release
	
copy-apk:
	cp $(MINDREF_DEBUG_APK) $(HOME)/ApkProjects/$(basename $(MINDREF_DEBUG_APK))/$(MINDREF_DEBUG_APK)
.PHONY : copy-apk

$(UNPACK_DIR):
	rm -rf $(UNPACK_DIR)/*
	mkdir -p $(UNPACK_DIR)

$(UNPACK_DIR)/$(MINDREF_APK): $(UNPACK_DIR)
	cp $(MINDREF_APK) $(UNPACK_DIR)/

unpack-apk: $(UNPACK_DIR)/$(MINDREF_APK)
	cd $(UNPACK_DIR)
	rm -rf $(UNPACK_DIR)/contents
	unzip $(MINDREF_APK) -x *.dex -d $(UNPACK_DIR)/contents
	chmod -R 777 $(UNPACK_DIR)/contents
	find $(UNPACK_DIR)/contents -type f -name "libpybundle.so" -exec tar --no-same-owner -xf {} -C $(UNPACK_DIR)/contents \;
	find $(UNPACK_DIR)/contents -type d -name "_python_bundle" -exec chmod -R +x {} \;



.PHONY : unpack-apk

