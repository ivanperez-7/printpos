""" Módulo con variables de configuraciones para varios usos. """
from configparser import ConfigParser
import base64
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
class _INIManager:
    def __init__(self):
        self.config = ConfigParser(inline_comment_prefixes=';')
        
    def _get(self, section, option):
        self.config.read('config.ini', encoding='UTF8')
        return self.config[section][option]
    
    @property
    def RED_LOCAL(self):
        return self._get('DEFAULT', 'red_local')
    
    @property
    def IMPRESORA_TICKETS(self):
        return self._get('DEFAULT', 'impresora')
    
    @property
    def NOMBRE_SUCURSAL(self):
        return self._get('SUCURSAL', 'nombre')
    
    @property
    def DIRECCION_SUCURSAL(self):
        return self._get('SUCURSAL', 'p1'), self._get('SUCURSAL', 'p2')
    
    @property
    def TELEFONO_SUCURSAL(self):
        return self._get('SUCURSAL', 'p3')

INI = _INIManager()
