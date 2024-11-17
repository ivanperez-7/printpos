""" Provee varias funciones útiles utilizadas frecuentemente. """

import random
import re
import string
import unicodedata
from urllib.parse import quote
import webbrowser as web

from openpyxl import Workbook
from openpyxl.styles import Font
from PySide6.QtCore import QDateTime, QLocale

__all__ = [
    'clamp',
    'chunkify',
    'daysTo',
    'unidecode',
    'randFile',
    'son_similar',
    'stringify_float',
    'formatdate',
    'exportarXlsx',
    'enviarWhatsApp',
]


def clamp(value, smallest, largest):
    """ Trunca un valor dentro de un rango. """
    return sorted((value, smallest, largest))[1]


def chunkify(array: list, size: int):
    """ Divide un arreglo en subarreglos de un tamaño dado. """
    if not isinstance(array, list):
        array = list(array)
    return [array[x : x + size] for x in range(0, len(array), size)]


def daysTo(num_days: int):
    """ Dar formato a un número de días a 'hace {} días/semanas/años'. """
    if num_days < 0:
        return 'Invalid input'

    if num_days < 1:
        return 'hoy'
    elif num_days == 1:
        return 'hace un día'
    elif num_days < 7:
        return f'hace {num_days} días'
    elif num_days < 14:
        return 'hace una semana'
    elif num_days < 30:
        weeks_ago = num_days // 7
        return f'hace {weeks_ago} semanas'
    elif num_days < 365:
        months_ago = num_days // 30
        return f"hace {months_ago} mes{'es' if months_ago > 1 else ''}"
    else:
        years_ago = num_days // 365
        return f"hace {years_ago} año{'s' if years_ago > 1 else ''}"


def formatdate(date=None):
    """ Da formato en texto a un dato QDateTime o datetime de Python.
    Ejemplo: 08 de febrero 2023, 4:56 p. m. """
    locale = QLocale(QLocale.Spanish, QLocale.Mexico)
    formatted = locale.toString(date or QDateTime.currentDateTime(), "d 'de' MMMM yyyy, h:mm ap")
    return unicodedata.normalize('NFKD', formatted)


def unidecode(input_str: str):
    """ Elimina (normaliza) los acentos en una cadena de texto y
    convierte a minúsculas. Ejemplo: 'Pérez' -> 'perez'. """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    normalized = ''.join(c for c in nfkd_form if not unicodedata.combining(c))
    return normalized.lower()


def randFile(ext: str = ''):
    """ Genera archivo de extensión dada con nombre aleatorio. """
    ext = re.sub('[^a-zA-Z]*', '', ext)
    chars = string.ascii_letters + string.digits
    rand = ''.join(random.choice(chars) for _ in range(8))
    return f'auto-{rand}.{ext}'


def stringify_float(f):
    try:
        return f'{int(f):,}' if f.is_integer() else f'{f:,.2f}'
    except AttributeError:
        return f'{f:,}'


def son_similar(obj1, obj2):
    """ Determina si dos cadenas son similares o no. """
    if not obj1 or not obj2:
        return False

    str1_clean = unidecode(re.sub(r'\W+', ' ', str(obj1)))
    str2_clean = unidecode(re.sub(r'\W+', ' ', str(obj2)))

    return str1_clean in str2_clean


def exportarXlsx(rutaArchivo, titulos, datos):
    """ Exporta una lista de tuplas a un archivo MS Excel, con extensión xlsx.
    Requiere el nombre del archivo, una lista con los títulos para las
    columnas, y una lista de tuplas con los datos principales. """
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
    """ Enviar mensaje por WhatsApp abriendo el navegador de internet. """
    if '+' not in phone_no:  # agregar código de país de México
        phone_no = '+52' + phone_no
    return web.open_new_tab(f'https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}')
