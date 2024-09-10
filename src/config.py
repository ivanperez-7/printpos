""" Módulo con variables de configuraciones para varios usos. """

import base64
from configparser import ConfigParser
from pathlib import Path
import os

import machineid

############################
# VARIABLES PARA LICENCIAS #
############################
APPDATA_DIR = Path(os.environ['APPDATA']) / 'PrintPOS'
LICENSE_PATH = APPDATA_DIR / 'printpos.lic'

INSTANCE_NAME = machineid.id().split('-')[-1]
FERNET_KEY = base64.urlsafe_b64encode(bytes(machineid.hashed_id('PrintPOS'), 'utf-8')[-32:])


#################################
# VARIABLES PARA ACCEDER A .INI #
#################################
_INIParser = ConfigParser(inline_comment_prefixes=';')
filename = 'config.ini'


class _INIManager:
    def __init__(self):
        if not _INIParser.read(filename, encoding='utf8'):
            _INIParser.add_section('RED')
            _INIParser.add_section('SUCURSAL')
            _INIParser.add_section('DEBUG')
            _INIParser.set('RED', 'nombre_servidor', '127.0.0.1')
            _INIParser.set('RED', 'impresora', '')
            _INIParser.set('SUCURSAL', 'calle_1', '')
            _INIParser.set('SUCURSAL', 'calle_2', '')
            _INIParser.set('SUCURSAL', 'telefono', '')
            _INIParser.set('DEBUG', 'save_png', '')

        for section in _INIParser.sections():
            for option in _INIParser.options(section):
                self._create_property(section, option)

    def guardar(self):
        with open(filename, 'w+', encoding='utf8') as configfile:
            _INIParser.write(configfile)
        _INIParser.read(filename, encoding='utf8')

    def _create_property(self, section, option):
        def getter(self):
            return _INIParser.get(section, option)

        def setter(self, value):
            _INIParser.set(section, option, value)

        setattr(self.__class__, option.upper(), property(getter, setter))
        setattr(self, option.upper(), getter(self))


INI = _INIManager()
""" Manejador para el archivo `config.ini`.
    Revisar archivo para los atributos válidos del manejador. """
