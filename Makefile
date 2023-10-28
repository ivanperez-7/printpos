EXEC=PrintPOS

all: setup

src/ui/resources_rc.py: resources.qrc resources/images/*
	pyside6-rcc -o $@ $<

src/ui/%.py: designer/%.ui
	pyside6-uic --from-imports -o $@ $<

UI_FILES := $(wildcard designer/*.ui)
PY_FILES := $(patsubst designer/%.ui, src/ui/%.py, $(UI_FILES))

setup: src/ui/resources_rc.py $(PY_FILES)

launch:
	python $(EXEC).py

install:
	nuitka $(EXEC).py \
		--standalone \
		--disable-console \
		--enable-plugin=pyside6 \
		--include-package-data=resources \
		--include-data-files=config.ini=config.ini \
		--include-data-files=icon.ico=icon.ico \
		--nofollow-import-to=unittest \
		--nofollow-import-to=tkinter \
		--force-stderr-spec=%PROGRAM_BASE%.err.txt \
		--force-stdout-spec=%PROGRAM_BASE%.out.txt \
		--windows-icon-from-ico=icon.ico \
		--assume-yes-for-downloads \
		--remove-output

pip_reinstall:
	pip --require-virtualenv freeze > installed.txt
	-pip uninstall -r installed.txt -y
	del installed.txt
	
	py -m pip install --upgrade pip
	pip install -r requirements.txt
