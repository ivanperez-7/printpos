""" Provee varias funciones útiles utilizadas frecuentemente. """
from datetime import datetime
from typing import SupportsFloat

import fdb
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


def chunkify(array, size: int):
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


def generarPDFTemporal():
    """ Genera para archivo PDF temporal en directorio temporal `tmp`. """
    import os
    import uuid
    
    base = os.environ['USERPROFILE'] + '\\Documents\\tmp'
    os.makedirs(base, exist_ok=True)
    
    return base + uuid.uuid4().hex[:10] + '.pdf'


def formatDate(date: QDateTime | datetime) -> str:
    """ Da formato en texto a un dato QDateTime.
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


def enviarAImpresora(ruta: str, prompt: bool):
    from configparser import ConfigParser
    import subprocess
    
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini')
    
    acrobat = config['DEFAULT']['acrobat']
    prompt_arg = '/P' if prompt else '/T'
    printer = config['IMPRESORAS']['default'] if not prompt else ''
    
    args = [acrobat, '/N', prompt_arg, ruta, printer]
    
    subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@run_in_thread
def generarOrdenCompra(conn: fdb.Connection, idx: int):
    """ Genera un PDF con el orden de compra correspondiente a la venta con índice
        `idx` en la base de datos. Recibe también un cursor a la base de datos.

        La orden de compra contiene:
            - Folio de venta
            - Cliente: Nombre y teléfono
            - Tabla de productos: (Cantidad, producto, especificaciones, precio, importe)
                Máx. 6 por página
            - Total a pagar, anticipo recibido y saldo restante
            - Fecha de creación
            - Fecha de entrega """
    import io
    
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    
    from utils.databasemanagers import ManejadorVentas

    manejadorVentas = ManejadorVentas(conn)
    
    # leer datos de venta y de cliente
    nombre, telefono = manejadorVentas.obtenerClienteAsociado(idx)
    _, _, _, creacion, entrega, *_ = manejadorVentas.obtenerVenta(idx)
    
    total = manejadorVentas.obtenerImporteTotal(idx)
    anticipo = manejadorVentas.obtenerAnticipo(idx)
    saldo = total - anticipo

    # datos para la tabla de productos
    productos = manejadorVentas.obtenerTablaOrdenCompra(idx)
    # se dividen los productos de la orden en grupos de 6
    chunks = chunkify(productos, 6)

    writer = PdfWriter()

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='codigo', fontName='Helvetica', fontSize=10))
    estilos.add(ParagraphStyle(name='especificaciones', fontName='Helvetica', fontSize=8))

    # itera sobre cada grupo de 6 productos
    for chunk in chunks:
        # inicializar canvas y E/S de bytes
        packet = io.BytesIO()
        can = Canvas(packet)

        # <escribir datos en el canvas>
        can.setFont('Helvetica-Bold', 10)
        can.drawRightString(373, 491, str(idx))

        can.setFont('Helvetica', 12)
        can.drawRightString(373, 546, formatDate(creacion))

        can.setFont('Helvetica', 10)
        can.drawString(75, 493, nombre)
        can.drawString(75, 470, telefono)
        can.drawString(150, 448, formatDate(entrega))
        can.drawCentredString(353, 148, f'{saldo:,.2f}')
        can.drawCentredString(353, 170, f'{anticipo:,.2f}')

        can.setFont('Helvetica-Bold', 10)
        can.drawCentredString(353, 192, f'{total:,.2f}')
        can.setFont('Helvetica', 10)

        for i, (prodCantidad, prodNombre, prodEspecificaciones,
                prodPrecio, prodImporte) in enumerate(chunk):
            y_sep = -32.4*i     # separador por renglón de la tabla

            can.drawCentredString(49, 381+y_sep, f'{prodCantidad:,.2f}')
            can.drawCentredString(306, 381+y_sep, f'{prodPrecio:,.2f}')
            can.drawCentredString(353, 381+y_sep, f'{prodImporte:,.2f}')

            estilos['codigo'].fontSize = 10

            # tamaño de fuente variable
            while estilos['codigo'].fontSize > 1:
                text = Paragraph(prodNombre, estilos['codigo'])
                w, h = text.wrap(59, 24)

                if h <= 24:
                    break
                estilos['codigo'].fontSize -= 0.1
            text.drawOn(can, 78.4, 398+y_sep-h)

            estilos['especificaciones'].fontSize = 8

            # tamaño de fuente variable
            while estilos['especificaciones'].fontSize > 1:
                text = Paragraph(prodEspecificaciones, estilos['especificaciones'])
                w, h = text.wrap(125, 24)

                if h <= 24:
                    break
                estilos['especificaciones'].fontSize -= 0.1
            text.drawOn(can, 151.2, 396+y_sep-h)
        # </escribir datos en el canvas>

        # guardar cambios y mover puntero de bytes al principio
        can.save()
        packet.seek(0)

        # crear variable para nuevo PDF y leer plantilla
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open('resources/pdf/orden_compra2023.pdf', 'rb'))

        # agregar trazados en el PDF de la plantilla
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
    
    # crear archivo temporal e imprimir        
    filename = generarPDFTemporal()
    
    with open(filename, 'wb') as f:
        writer.write(f)
    enviarAImpresora(filename, True)


####################################
# <FUNCIONES PARA GENERAR TICKETS> #
####################################
@run_in_thread
def _generarTicketPDF(folio, productos, vendedor, fechaCreacion, pagado, metodo_pago):
    """ Función abstracta para generar el ticket de compra o presupuesto.
        Contiene:
            - Logo
            - Tabla de productos [Cantidad | Producto | Precio | Descuento | Importe]
            - Precio total
            - Nombre del vendedor
            - Folio de venta
            - Fecha y hora de creación """
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    from reportlab.platypus import (Table, TableStyle, SimpleDocTemplate,
                                    Paragraph, Spacer, Image)
    
    # archivo y directorio temporales
    filename = generarPDFTemporal()

    doc = SimpleDocTemplate(filename,
                            pagesize=(80*mm, 297*mm),
                            rightMargin=0, leftMargin=0,
                            topMargin=0, bottomMargin=0)

    # Define styles for the document
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', fontName='Helvetica', 
                              fontSize=8, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Center_2', fontName='Helvetica', 
                              fontSize=11, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                              fontSize=8, alignment=TA_LEFT))

    # contenido del PDF
    logo = Image('resources/images/logo.png', width=50*mm, height=26.4*mm)

    data = [['CANT.', 'PRODUCTO', 'P/U', 'DESC.', 'TOTAL']]
    
    firma = False
    total_desc = 0

    for cantidad, nombre, precio, descuento, importe in productos:
        data.append([
            f'{cantidad:,.2f}',
            Paragraph(nombre, styles['Center']),
            f'{precio:,.2f}',
            f'{descuento:,.2f}' if descuento > 0 else '',
            f'{importe:,.2f}'
        ])
        if descuento > 0: 
            firma = True
            total_desc += descuento * cantidad

    # productos de la compra
    tabla_productos = Table(data, colWidths=[10*mm, 28*mm, 12*mm, 12*mm, 12*mm])

    tabla_productos.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONT', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, 0), 0.4, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.black)
    ]))
    
    # total a pagar       
    total = sum(importe for _, _, _, _, importe in productos)
    total = round(total, 2)
    pagado = round(pagado, 2)
    
    table2 = [['IMPORTE:', f'{total:,.2f}']]
    
    if pagado:
        table2.extend([['Pagado:', f'{pagado:,.2f}'],
                       ['Cambio:', f'{pagado-total:,.2f}']])
    
    table2 = Table(table2, hAlign='RIGHT')

    table2.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0)
    ]))
    
    # elementos dinámicos, según se requieran
    if folio:
        titulo = 'TICKET DE COMPRA'
        pie = '¡Muchas gracias por su compra!'
        
        folio= f'<b>Folio de venta</b>: {folio} ' \
                  + '&nbsp; '*7 + f'<b>Método de pago</b>: {metodo_pago}'
    else:
        titulo = 'COTIZACIÓN DE VENTA'
        pie = '¡Muchas gracias por su visita!'
        folio = ''
    
    # leer datos de sucursal de archivo de configuración
    from configparser import ConfigParser
    
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini', encoding='utf8')
    SUCURSAL = config['SUCURSAL']

    # elementos para constuir el PDF
    elements = [
        logo,
        Spacer(1, 6),

        Paragraph(SUCURSAL['p1'], styles['Center']),
        Paragraph(SUCURSAL['p2'], styles['Center']),
        Spacer(1, 6),

        Paragraph(SUCURSAL['p3'], styles['Center']),
        Spacer(1, 6),

        Paragraph('* '*40, styles['Center']),
        Paragraph(titulo, styles['Center']),
        Paragraph('* '*40, styles['Center']),
        Paragraph(folio, styles['Left']),
        Paragraph(f'<b>Fecha</b>: {formatDate(fechaCreacion)}', styles['Left']),
        Spacer(1, 10),

        tabla_productos,
        Spacer(1, 7),

        table2]
    
    elements += [
        Spacer(1, 6),
        
        Paragraph(f'¡Hoy se ahorró ${total_desc:,.2f}!', styles['Center_2']), 
        Spacer(1, 25),
        
        Paragraph('Autoriza descuentos: ' + '_'*24, styles['Left'])] if firma else []
    
    elements += [
        Spacer(1, 15),
        
        Paragraph(f'Le atendió: {vendedor}', styles['Center']),
        Paragraph(pie, styles['Center'])]

    # Build the PDF document
    doc.build(elements)

    enviarAImpresora(filename, False)


def generarTicketCompra(conn: fdb.Connection, idx):
    """ Genera el ticket de compra a partir de un identificador en la base de datos. """
    from utils.databasemanagers import ManejadorVentas
    
    # obtener datos de la compra, de la base de datos
    manejador = ManejadorVentas(conn)
    productos = manejador.obtenerTablaTicket(idx)

    # más datos para el ticket
    vendedor = manejador.obtenerUsuarioAsociado(idx)
    datos = manejador.obtenerVenta(idx)

    _, _, _, fechaCreacion, _, _, metodo, _, _, pagado = datos
    
    # cambiar método de pago (abreviatura)
    if metodo == 'Efectivo': metodo = 'EFEC'
    elif metodo == 'Transferencia bancaria': metodo = 'TRF'
    else: metodo = 'TVP'
    
    _generarTicketPDF(idx, productos, vendedor, 
                      fechaCreacion, pagado, metodo)


def generarTicketPresupuesto(productos, vendedor):
    """ Genera un ticket para el presupuesto de una compra. """
    _generarTicketPDF(0, productos, vendedor, 
                      QDateTime.currentDateTime(), 0., None)
#####################################
# </FUNCIONES PARA GENERAR TICKETS> #
#####################################
