# Rule to compile .pyx files to .c files (if a .c file does not exist or is older than the .pyx file)
$(PROJECT_ROOT)/%.c: $(PROJECT_ROOT)/%.pyx
	uv run cythonize -i -f $< -3 && git add $@

cythonize: $(PYX_C_FILES)

clean-bytecode :
	# Remove this projects bytecode
	find $(PROJECT_ROOT) -name "*.pyc" -delete
	find $(PROJECT_ROOT) -name "__pycache__" -type d -print0 | xargs -0 rm -rf
	find $(PROJECT_ROOT) -name ".mypy_cache" -type d -print0 | xargs -0 rm -rf
.PHONY : clean-bytecode

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/assets:
	mkdir -p $(BUILD_DIR)/assets

$(PRESPLASH_DEST): $(BUILD_DIR)/assets
	cp $(PRESPLASH_SRC) $(PRESPLASH_DEST)

$(ICON_DEST): $(BUILD_DIR)/assets
	cp $(ICON_SRC) $(ICON_DEST)

$(ASSET_MATERIAL_TTF_DEST): $(BUILD_DIR)/assets
	cp $(ASSET_MATERIAL_TTF_SRC) $(ASSET_MATERIAL_TTF_DEST)

$(ASSET_ROBOTO_TTF_DEST): $(BUILD_DIR)/assets
	cp $(ASSET_ROBOTO_TTF_SRC) $(ASSET_ROBOTO_TTF_DEST)

$(PRIVATE_ENTRYPOINT_DEST): $(BUILD_DIR)
	cp $(PRIVATE_ENTRYPOINT_SRC) $(PRIVATE_ENTRYPOINT_DEST)

asset-image: $(PRESPLASH_DEST) $(ICON_DEST)
.PHONY : asset-image

asset-fonts: $(ASSET_MATERIAL_TTF_DEST) $(ASSET_ROBOTO_TTF_DEST)
.PHONY : asset-fonts

clean-mindref-p4a-src:
	rm -rf ~/.local/share/python-for-android/packages/mindref
	uv run p4a clean-recipe-build mindref_android || true
	uv run p4a clean_dists
.PHONY : clean-mindref-p4a-src

prebuild : $(BUILD_DIR) $(PRIVATE_ENTRYPOINT_DEST) asset-image asset-fonts clean-mindref-p4a-src
.PHONY : prebuild


