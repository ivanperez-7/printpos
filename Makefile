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
		--windows-console-mode=disable \
		--enable-plugin=pyside6 \
		--nofollow-import-to=unittest \
		--nofollow-import-to=pytest \
		--nofollow-import-to=setuptools \
		--nofollow-import-to=tkinter \
		--nofollow-import-to=pyreadline3 \
		--include-package=src \
		--force-stderr-spec={PROGRAM_BASE}.err.txt \
		--force-stdout-spec={PROGRAM_BASE}.out.txt \
		--windows-icon-from-ico=icon.ico \
		--assume-yes-for-downloads \
		--remove-output
#		--include-package-data=resources
#		7za a -tzip .\printpos.zip .\$(EXEC).dist\*

pip_reinstall:
	pip --require-virtualenv freeze > installed.txt
	-pip uninstall -r installed.txt -y
	del installed.txt
	
	py -m pip install --upgrade pip
	pip install -r requirements.txt
