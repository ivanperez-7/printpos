""" Módulo con variables de configuraciones para varios usos. """
from configparser import ConfigParser
import base64
from pathlib import Path
import os
import uuid


############################
# VARIABLES PARA LICENCIAS #
############################
APPDATA_DIR = Path(os.environ['APPDATA']) / 'PrintPOS'
LICENSE_PATH = APPDATA_DIR / 'printpos.lic'

MOBO_UUID = str(uuid.UUID(int=uuid.getnode()))
INSTANCE_NAME = MOBO_UUID.split('-')[-1]
FERNET_KEY = base64.urlsafe_b64encode(bytes(MOBO_UUID, 'utf-8')[-32:])


#################################
# VARIABLES PARA ACCEDER A .INI #
#################################
def _get(section, option):
    """ Lee config.ini y regresa objeto ConfigParser. """
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini', encoding='UTF8')
    return config[section][option]

RED_LOCAL = _get('DEFAULT', 'red_local')
IMPRESORA_TICKETS = _get('DEFAULT', 'impresora')
NOMBRE_SUCURSAL = _get('SUCURSAL', 'nombre')
DIRECCION_SUCURSAL = _get('SUCURSAL', 'p1'), _get('SUCURSAL', 'p2')
TELEFONO_SUCURSAL = _get('SUCURSAL', 'p3')
