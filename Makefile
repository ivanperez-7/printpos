EXEC=PrintPOS

all: setup launch

resources_rc.py: resources.qrc resources/images/*
	pyside6-rcc -o $@ $<

src/%.py: src/%.ui
	pyside6-uic -o $@ $<

setup: resources_rc.py $(addsuffix .py, $(basename $(wildcard src/**/*.ui)))

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
	pip --require-virtualenv freeze > requirements.txt
	-pip uninstall -r requirements.txt -y
	del requirements.txt
	
	py -m pip install --upgrade pip
	pip install --upgrade fdb PySide6 pypdf2 reportlab openpyxl nuitka ordered-set
