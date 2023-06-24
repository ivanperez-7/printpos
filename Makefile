EXEC=PrintPOS

all: setup launch

resources/resources_rc.py: resources.qrc resources/images/*
	pyrcc5 -o $@ $<

src/%.py: src/%.ui
	pyuic5 --import-from=resources -o $@ $<

setup: resources/resources_rc.py $(addsuffix .py, $(basename $(wildcard src/**/*.ui)))

launch:
	python $(EXEC).py

install:
	nuitka $(EXEC).py --standalone --disable-console \
	--enable-plugin=pyqt5 --include-package-data=resources.pdf,resources.images \
	--include-data-files=config.ini=config.ini \
	--nofollow-import-to=unittest --nofollow-import-to=tkinter \
	--windows-icon-from-ico=icon.ico --assume-yes-for-downloads --remove-output

pip_reinstall:
	pip --require-virtualenv freeze > requirements.txt
	-pip uninstall -r requirements.txt -y
	del requirements.txt
	
	py -m pip install --upgrade pip
	pip install --upgrade fdb PyQt5 PyQtChart pypdf2 reportlab openpyxl pywhatkit nuitka ordered-set
