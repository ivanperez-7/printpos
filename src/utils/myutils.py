""" Provee varias funciones útiles utilizadas frecuentemente. """
from configparser import ConfigParser
import re
import unicodedata

from PySide6.QtCore import QDateTime, QThread, QLocale
from PySide6.QtGui import QRegularExpressionValidator

from utils.mydecorators import run_in_thread


__all__ = ['ColorsEnum', 'FabricaValidadores', 'clamp', 'chunkify',
           'unidecode', 'son_similar', 'contiene_duplicados', 'formatDate',
           'leer_config', 'exportarXlsx', 'enviarWhatsApp']


class ColorsEnum:
    """ Clase para almacenar colores (hexadecimal) en variables. """
    VERDE = 0xB2FFAE
    AMARILLO = 0xFDFDA9
    ROJO = 0xFFB2AE


class FabricaValidadores:
    """ Clase para generar validadores de expresiones regulares
        (`QRegularExpressionValidator`) para widgets. """
    @classmethod
    @property
    def IdFirebird(cls):
        return QRegularExpressionValidator(r'[a-zA-Z0-9_$]+')
    
    @classmethod
    @property
    def NumeroDecimal(cls):
        return QRegularExpressionValidator(r'\d*\.?\d*')


class Runner(QThread):
    """ Clase derivada de QThread para manejar manualmente cuándo un hilo comienza y termina.
        Para manejo automático, usar decorador `run_in_thread`. """
    
    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs
    
    def run(self):
        self._target(*self._args, **self._kwargs)
    
    def stop(self):
        """ Llama a métodos `terminate` y luego `wait`. """
        self.terminate()
        self.wait()


def clamp(value, smallest, largest):
    """ Trunca un valor dentro de un rango. """
    return sorted((value, smallest, largest))[1]


def chunkify(array: list, size: int):
    """ Divide un arreglo en subarreglos de un tamaño dado. """
    return [array[x: x + size] for x in range(0, len(array), size)]


def unidecode(input_str: str):
    """ Elimina (normaliza) los acentos en una cadena de texto y 
        convierte a minúsculas. Ejemplo: 'Pérez' -> 'perez'. """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    normalized = u''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    return normalized.lower()


def son_similar(str1: str, str2: str):
    """ Determina si dos cadenas son similares o no. """
    # convertir, por si acaso
    str1 = str(str1)
    str2 = str(str2)
    
    str1_clean = unidecode(re.sub(r'\W+', ' ', str1))
    str2_clean = unidecode(re.sub(r'\W+', ' ', str2))
    
    return str1_clean in str2_clean


def contiene_duplicados(lista: list):
    """ Regresa `True` si la lista dada contiene elementos duplicados. """
    return len(lista) != len(set(lista))


def formatDate(date = None):
    """ Da formato en texto a un dato QDateTime o datetime de Python.
        Ejemplo: 08 de febrero 2023, 4:56 p. m. """
    if not date:
        date = QDateTime.currentDateTime()
    
    locale = QLocale(QLocale.Spanish, QLocale.Mexico)
    return locale.toString(date, "d 'de' MMMM yyyy, h:mm ap")


def leer_config():
    """ Lee config.ini y regresa objeto ConfigParser. """
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini', encoding='UTF8')
    return config


@run_in_thread
def exportarXlsx(rutaArchivo, titulos, datos):
    """ Exporta una lista de tuplas a un archivo MS Excel, con extensión xlsx.
        Requiere el nombre del archivo, una lista con los títulos para las
        columnas, y una lista de tuplas con los datos principales. """
    from openpyxl import Workbook
    from openpyxl.styles import Font
    
    wb = Workbook()
    ws = wb.active
    
    # títulos de las columnas
    ws.append(titulos)
    
    # agregar columnas con información
    for row in datos:
        ws.append(row)
    
    # cambiar fuente (agregar negritas)
    for cell in ws['1']:
        cell.font = Font(bold=True)
    
    wb.save(rutaArchivo)


def enviarWhatsApp(phone_no: str, message: str):
    """ Enviar mensaje por WhatsApp abriendo el navegador de internet.
        TODO:
            - open("https://web.whatsapp.com/accept?code=" + receiver) """
    from urllib.parse import quote
    import webbrowser as web
    
    if '+' not in phone_no:  # agregar código de país de México
        phone_no = '+52' + phone_no
    
    try:
        web.open_new_tab(f'https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}')
    except Exception as err:
        print('Could not open browser: ' + str(err))
