
# Copy the AAR files to the project root
$(MINDREF_UTILS_DEBUG): $(UTIL_OUTPUT)/$(MINDREF_UTILS_DEBUG)
	@echo "Copying $< to $@"
	cp $< $@


# Rule to ensure .aar files are built
$(UTIL_OUTPUT)/$(MINDREF_UTILS_DEBUG):
	@echo "Building AAR files..."
	cd $(UTIL_ROOT) && ./gradlew mindrefutils:build

build-aar : $(MINDREF_UTILS_DEBUG)

clean-aar :
	cd $(UTIL_ROOT) && ./gradlew clean mindrefutils:clean
.PHONY : clean-aar