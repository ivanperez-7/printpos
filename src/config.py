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
FERNET_KEY = base64.urlsafe_b64encode(
    bytes(machineid.hashed_id('PrintPOS'), 'utf-8')[-32:])


#################################
# VARIABLES PARA ACCEDER A .INI #
#################################
_INIParser = ConfigParser(inline_comment_prefixes=';')
filename = 'config.ini'

class _INIManager:
    def __init__(self):
        _INIParser.read(filename, encoding='UTF8')

        for section in _INIParser.sections():
            for option in _INIParser.options(section):
                self._create_property(section, option)
    
    def guardar(self):
        with open(filename, 'w+', encoding='utf8') as configfile:
            _INIParser.write(configfile)
    
    def _create_property(self, section, option):
        def getter(self):
            _INIParser.read(filename, encoding='UTF8')
            return _INIParser.get(section, option)

        def setter(self, value):
            _INIParser.set(section, option, value)
        
        setattr(self.__class__, option.upper(), property(getter, setter))
        setattr(self, option.upper(), getter(self))
    
    @property
    def DIRECCION_SUCURSAL(self):
        """ Calles y fracc. de la sucursal. Regresa una cadena por cada dato. """
        return self.P1, self.P2

INI = _INIManager()
""" Manejador para el archivo `config.ini`.
    Revisar archivo para los atributos válidos del manejador. """
