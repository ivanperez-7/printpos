""" Módulo con métodos de activación, desactivación y validación de licencias.

    Provee también una clase `Enum` para manejar los errores que puedan resultar. """
from cryptography.fernet import Fernet as _Fernet
from enum import Enum as _Enum, auto as _auto
import json
import requests
import shutil
from time import sleep as _sleep

import config as _config

BASE_URL = 'https://api.lemonsqueezy.com'
POST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}


class Errores(_Enum):
    ACTIVACION_FALLIDA = _auto()
    ACTIVACION_NO_VALIDA = _auto()

    VERIFICACION_FALLIDA = _auto()
    LICENCIA_NO_EXISTENTE = _auto()
    LICENCIA_NO_VALIDA = _auto()


def activar_licencia(license_key: str):
    """ Activar licencia pasando solamente la llave. Al activarse correctamente,
        se creará un archivo encriptado donde se guardarán la llave de la licencia
        y el ID de instancia devuelto por la API. 
        
        Regresa un booleano que dicta si la operación fue exitosa o no. """
    if not license_key:
        return False, Errores.ACTIVACION_NO_VALIDA

    try:
        # datos para solicitud POST
        r = requests.post(
            BASE_URL + '/v1/licenses/activate',
            headers=POST_HEADERS,
            data={
                'license_key': license_key,
                'instance_name': _config.INSTANCE_NAME
            }
        )
        r = r.json()
        activated = False
    except requests.exceptions.ConnectionError:
        _sleep(0.2)
        return False, Errores.ACTIVACION_FALLIDA

    if r['activated'] == True:
        # crear carpeta appdata
        if not _config.APPDATA_DIR.exists():
            _config.APPDATA_DIR.mkdir(parents=True)
        # verificar que carpeta de licencia no exista ya
        if _config.LICENSE_PATH.exists() and _config.LICENSE_PATH.is_dir():
            shutil.rmtree(_config.LICENSE_PATH, ignore_errors=True)

        with open(_config.LICENSE_PATH, 'wb') as license_file:
            f = _Fernet(_config.FERNET_KEY)
            license_data = {
                'license_key': license_key,
                'instance_id': r['instance']['id']
            }
            license_file.write(f.encrypt(bytes(json.dumps(license_data), 'utf-8')))
        activated = True
        flag = None
    else:
        activated = False
        flag = Errores.ACTIVACION_NO_VALIDA
        _config.LICENSE_PATH.unlink(missing_ok=True)

    return activated, flag


def desactivar_licencia():
    """ Intenta desactivar la licencia para esta máquina leyendo el archivo
        de licencia que se obtiene durante la activación.
        
        Regresa un booleano que dicta si la operación fue exitosa o no. """
    # leer archivo .lic
    if not _config.LICENSE_PATH.exists():
        return False

    with open(_config.LICENSE_PATH, 'rb') as license_file:
        f = _Fernet(_config.FERNET_KEY)
        data = f.decrypt(license_file.read())

        license_data = json.loads(data.decode('utf-8'))
        license_key = license_data['license_key']
        instance_id = license_data['instance_id']

    if license_key is None or instance_id is None:
        return False

    # datos para solicitud POST
    r = requests.post(
        BASE_URL + '/v1/licenses/deactivate',
        headers=POST_HEADERS,
        data={
            'license_key': license_key,
            'instance_id': instance_id
        }
    )
    r = r.json()
    desactivada = False

    if r['deactivated'] == True:
        desactivada = True
        _config.LICENSE_PATH.unlink(missing_ok=True)
    else:
        desactivada = False
    return desactivada


def validar_licencia():
    """ Validar licencia proporcionando llave e instancia, o bien, leyendo
        el archivo de licencia que se obtiene durante la activación.
        
        Regresa un booleano que dicta si la licencia es válida y está activa.
        Al no ser el caso, regresa también LICENCIA_NO_EXISTENTE o VERIFICACION_FALLIDA. """
    if not _config.LICENSE_PATH.exists():
        return False, Errores.LICENCIA_NO_EXISTENTE

    with open(_config.LICENSE_PATH, 'rb') as license_file:
        f = _Fernet(_config.FERNET_KEY)
        data = f.decrypt(license_file.read())

        license_data = json.loads(data.decode('utf-8'))
        license_key = license_data['license_key']
        instance_id = license_data['instance_id']

    if license_key is None or instance_id is None:
        return False, Errores.LICENCIA_NO_EXISTENTE

    try:
        # datos para solicitud POST
        r = requests.post(
            BASE_URL + '/v1/licenses/validate',
            headers=POST_HEADERS,
            data={
                'license_key': license_key,
                'instance_id': instance_id
            }
        )
        r = r.json()
    except requests.exceptions.ConnectionError:
        _sleep(0.5)
        return False, Errores.VERIFICACION_FALLIDA

    if (
            r['valid'] == True
            and r['license_key']['status'] == 'active'
            and r['instance']['id'] == instance_id
            and r['meta']['product_name'] == 'Licencia PrintPOS'
    ):
        return True, None
    else:
        return False, Errores.LICENCIA_NO_VALIDA
