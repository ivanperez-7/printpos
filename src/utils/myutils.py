""" Provee varias funciones útiles utilizadas frecuentemente. """
from datetime import datetime
from typing import SupportsFloat

from PySide6.QtCore import QDateTime

from utils.mydecorators import run_in_thread


class ColorsEnum:
    """ Clase para almacenar colores (hexadecimal) en variables. """
    VERDE = 0xB2FFAE
    AMARILLO = 0xFDFDA9
    ROJO = 0xFFB2AE


def clamp(value, smallest, largest) -> SupportsFloat:
    """ Trunca un valor dentro de un rango. """
    return sorted((value, smallest, largest))[1]


def chunkify(array: list, size: int):
    """ Divide un arreglo en subarreglos de un tamaño dado. """
    return [array[x : x+size] for x in range(0, len(array), size)]


def unidecode(input_str: str):
    """ Elimina (normaliza) los acentos en una cadena de texto y 
        convierte a minúsculas. Ejemplo: 'Pérez' -> 'perez'. """
    import unicodedata

    nfkd_form = unicodedata.normalize('NFKD', input_str)
    normalized = u''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    return normalized.lower()


def son_similar(str1: str, str2: str):
    """ Determina si dos cadenas son similares o no. """
    import re
    
    # convertir, por si acaso
    str1 = str(str1)
    str2 = str(str2)
    
    str1_clean = unidecode(re.sub(r'\W+', ' ', str1))
    str2_clean = unidecode(re.sub(r'\W+', ' ', str2))
    
    return str1_clean in str2_clean


def formatDate(date: QDateTime | datetime) -> str:
    """ Da formato en texto a un dato QDateTime o datetime de Python.
        Ejemplo: 08 de febrero 2023, 4:56 p. m. """
    if not date:
        return ''
    
    from PySide6.QtCore import QLocale
    
    if isinstance(date, datetime):
        date = QDateTime(date)

    locale = QLocale(QLocale.Spanish, QLocale.Mexico)

    return locale.toString(date, "d 'de' MMMM yyyy, h:mm ap")


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

    if '+' not in phone_no:     # agregar código de país de México
        phone_no = '+52' + phone_no

    try:
        web.open_new_tab(f'https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}')
    except Exception as err:
        print('Could not open browser: ' + str(err))
