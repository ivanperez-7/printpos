EXEC=PrintPOS

all: setup launch

resources_rc.py: resources.qrc resources/images/*
	pyside6-rcc -o $@ $<

ui/%.py: ui/%.ui
	pyside6-uic -o $@ $<

setup: resources_rc.py $(addsuffix .py, $(basename $(wildcard ui/*.ui)))

launch:
	python $(EXEC).py

install:
	nuitka $(EXEC).py \
		--standalone \
		--disable-console \
		--enable-plugin=pyside6 \
		--include-package-data=resources.pdf,resources.images \
		--include-data-files=config.ini=config.ini \
		--nofollow-import-to=unittest \
		--nofollow-import-to=tkinter \
		--windows-icon-from-ico=icon.ico \
		--assume-yes-for-downloads \
		--remove-output

pip_reinstall:
	pip --require-virtualenv freeze > installed.txt
	-pip uninstall -r installed.txt -y
	del installed.txt
	
	py -m pip install --upgrade pip
	pip install -r requirements.txt
