clean-apk : $(wildcard *.apk)
	@echo "Cleaning APK files..."
	rm -f $^


clean-all : clean-aar clean-apk clean-bytecode clean-builds clean-dists
	uv run p4a clean-all
.PHONY : clean-all

clean-builds:
	uv run p4a clean builds
.PHONY : clean-builds

clean-bootstraps:
	uv run p4a clean bootstrap_builds
.PHONY : clean-bootstraps

clean-dists:
	uv run p4a clean dists
.PHONY : clean-dists


build-apk :  $(MINDREF_UTILS_DEBUG) clean-bytecode prebuild
	uv run p4a apk --private $(BUILD_DIR) \
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
  	--arch arm64-v8a \
  	--requirements=$(PROJECT_REQUIREMENTS) \
  	--enable-androidx \
  	--presplash $(PROJECT_ROOT)/assets/presplash.png \
  	--icon $(PROJECT_ROOT)/assets/logo.png \
  	--depend "com.google.guava:guava:31.1-android" \
  	--depend "org.apache.commons:commons-io:1.3.2" \
  	--add-aar $(ROOT_DIR)/$(MINDREF_UTILS_DEBUG) \
  	--no-byte-compile-python \
  	--add-debug-symbols \
  	--local-recipes $(LOCAL_RECIPES)
.PHONY : build-apk

copy-apk:
	cp $(MINDREF_APK) $(HOME)/ApkProjects/$(basename $(MINDREF_APK))/$(MINDREF_APK)
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

