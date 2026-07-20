# Desktop run targets. These replace the PyCharm run configurations in .run/

DESKTOP_ENV := PYTHONUNBUFFERED=1

# A separate KIVY_HOME keeps phone-sized window state and logs out of ~/.kivy
PHONE_KIVY_HOME ?= $(HOME)/.kivyscreen

PHONE_DPI ?= 240
PHONE_DENSITY ?= 1.5
PHONE_PORTRAIT ?= 640x1314
PHONE_LANDSCAPE ?= 1350x604

PHONE_ENV = $(DESKTOP_ENV) \
	KIVY_HOME=$(PHONE_KIVY_HOME) \
	KIVY_DPI=$(PHONE_DPI) \
	KIVY_METRICS_DENSITY=$(PHONE_DENSITY) \
	KIVY_METRICS_FONTSCALE=1 \
	ENVIRONMENT=DEBUG

run :
	$(DESKTOP_ENV) uv run mindref
.PHONY : run

run-debug :
	$(DESKTOP_ENV) LOG_LEVEL=10 ENVIRONMENT=DEBUG uv run mindref
.PHONY : run-debug

run-phone :
	$(PHONE_ENV) uv run mindref --size=$(PHONE_PORTRAIT)
.PHONY : run-phone

run-phone-landscape :
	$(PHONE_ENV) uv run mindref --size=$(PHONE_LANDSCAPE)
.PHONY : run-phone-landscape

echo-desktop-vars :
	@echo PHONE_DPI = \"$(PHONE_DPI)\"
	@echo PHONE_DENSITY = \"$(PHONE_DENSITY)\"
	@echo PHONE_PORTRAIT = \"$(PHONE_PORTRAIT)\"
	@echo PHONE_LANDSCAPE = \"$(PHONE_LANDSCAPE)\"
	@echo PHONE_KIVY_HOME = \"$(PHONE_KIVY_HOME)\"
.PHONY : echo-desktop-vars
