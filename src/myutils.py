"""
Provee varias funciones útiles utilizadas frecuentemente.
"""
from contextlib import contextmanager
from fdb import Connection, Error
from mydecorators import run_in_thread


class ColorsEnum:
    """
    Clase para almacenar colores (hexadecimal) en variables.
    """
    VERDE = 0xB2FFAE
    AMARILLO = 0xFDFDA9
    ROJO = 0xFFB2AE


def clamp(value, smallest, largest):
    """
    Trunca un valor dentro de un rango.
    """
    return sorted((value, smallest, largest))[1]


def chunkify(array, size: int):
    """
    Divide un arreglo en subarreglos de un tamaño dado.
    """
    return [array[x : x+size] for x in range(0, len(array), size)]


def unidecode(input_str: str):
    """
    Elimina (normaliza) los acentos en una cadena de texto y convierte a 
    minúsculas. Ejemplo: 'Pérez' -> 'perez'.
    """
    import unicodedata

    nfkd_form = unicodedata.normalize('NFKD', input_str)
    normalized = u''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    return normalized.lower()


def son_similar(str1: str, str2: str) -> bool:
    """
    Determina si dos cadenas son similares o no.
    """
    import re
    
    # convertir, por si acaso
    str1 = str(str1)
    str2 = str(str2)
    
    str1_clean = unidecode(re.sub(r'\W+', ' ', str1))
    str2_clean = unidecode(re.sub(r'\W+', ' ', str2))
    
    return str1_clean in str2_clean


def formatDate(date) -> str:
    """
    Da formato en texto a un dato QDateTime.
    Ejemplo: 08 de febrero 2023, 4:56 p. m.
    """
    if not date:
        return ''
    
    from PyQt5.QtCore import QDateTime, QLocale

    QLocale.setDefault(QLocale('es_MX'))

    if isinstance(date, int):
        date = QDateTime.fromSecsSinceEpoch(date)

    return date.toString("d 'de' MMMM yyyy, h:mm ap")


@contextmanager
def manejar_transaccion(conn: Connection):
    """
    Context manager for handling transactions. Automatically rolls back
    the transaction if an exception occurs, otherwise commits the changes.
    """
    try:
        crsr = conn.cursor()
        yield crsr
        conn.commit()
    except Error:
        conn.rollback()
        raise


@run_in_thread
def exportarXlsx(rutaArchivo, titulos, datos):
    """
    Exporta una lista de tuplas a un archivo MS Excel, con extensión xlsx.
    Requiere el nombre del archivo, una lista con los títulos para las
    columnas, y una lista de tuplas con los datos principales.
    """
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
    """
    Enviar mensaje por WhatsApp abriendo el navegador de internet.
    TODO:
        - open("https://web.whatsapp.com/accept?code=" + receiver)
    """
    from urllib.parse import quote
    import webbrowser as web

    if '+' not in phone_no:     # agregar código de país de México
        phone_no = '+52' + phone_no

    try:
        web.open_new_tab(f'https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}')
    except Exception as err:
        print('Could not open browser: ' + str(err))


def enviarAImpresora(ruta: str, prompt: int | bool):
    from configparser import ConfigParser
    import subprocess
    
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini')
    
    acrobat = config['DEFAULT']['acrobat']
    prompt_arg = '/P' if prompt else '/T'
    printer = config['IMPRESORAS']['default'] if not prompt else ''

    subprocess.run([acrobat, '/N', prompt_arg, ruta, printer])


@run_in_thread
def generarOrdenCompra(crsr, idx: int):
    """
    Genera un PDF con el orden de compra correspondiente a la venta con índice
    `idx` en la base de datos. Recibe también un cursor a la base de datos.

    La orden de compra contiene:
        - Folio de venta
        - Cliente: Nombre y teléfono
        - Tabla de productos: (Cantidad, producto, especificaciones, precio, importe), máx. 6 por página
        - Total a pagar, anticipo recibido y saldo restante
        - Fecha de creación
        - Fecha de entrega
    """
    from PyPDF2 import PdfReader, PdfWriter

    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    import io

    # leer venta con índice idx de la base de datos y datos principales
    crsr.execute('''
    SELECT  Ventas.id_ventas,
            nombre,
            telefono,
            fecha_hora_creacion,
            fecha_hora_entrega,
            estado,
            SUM(importe) AS importe
    FROM    Ventas
            LEFT JOIN Clientes
                   ON Ventas.id_clientes = Clientes.id_clientes
            LEFT JOIN Ventas_Detallado
                   ON Ventas.id_ventas = Ventas_Detallado.id_ventas
    WHERE   Ventas.id_ventas = ?
    GROUP   BY 1, 2, 3, 4, 5, 6;
    ''', (idx,))

    folio, nombre, telefono, creacion, entrega, estado, total = crsr.fetchone()
    anticipo = float(estado.split()[1])
    saldo = total - anticipo

    # datos para la tabla de productos
    crsr.execute('''
    SELECT  cantidad,
            abreviado || IIF(duplex, ' (a doble cara)', ''),
            especificaciones,
            precio,
            importe AS importe
    FROM    Ventas_Detallado
            LEFT JOIN Productos
                   ON Ventas_Detallado.id_productos = Productos.id_productos
    WHERE   id_ventas = ?;
    ''', (idx,))

    # se dividen los productos de la orden en grupos de 6
    productos = crsr.fetchall()
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
        can.drawRightString(373, 491, str(folio))

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

            can.drawCentredString(49, 381+y_sep, str(prodCantidad))
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
    import os
    import uuid
    
    os.makedirs('./tmp/', exist_ok=True)
    
    filename = f'.\\tmp\\{uuid.uuid4().hex}.pdf'
    
    writer.write(open(filename, 'wb'))
    enviarAImpresora(filename, True)



####################################
# <FUNCIONES PARA GENERAR TICKETS> #
####################################
@run_in_thread
def _generarTicketPDF(folio, productos, vendedor, fechaCreacion, pagado, metodo_pago):
    """
    Función abstracta para generar el ticket de compra o presupuesto.
    Contiene:
        - Logo
        - Tabla de productos [Cantidad | Producto | Precio | Descuento | Importe]
        - Precio total
        - Nombre del vendedor
        - Folio de venta
        - Fecha y hora de creación
    """
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    from reportlab.platypus import (Table, TableStyle, SimpleDocTemplate,
                                    Paragraph, Spacer, Image)
    import os
    import uuid
    
    # archivo y directorio temporales
    os.makedirs('./tmp/', exist_ok=True)
    
    filename = f'.\\tmp\\{uuid.uuid4().hex}.pdf'

    doc = SimpleDocTemplate(filename,
                            pagesize=(80*mm, 297*mm),
                            rightMargin=0, leftMargin=0,
                            topMargin=0, bottomMargin=0)

    # Define styles for the document
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', fontName='Helvetica', 
                              fontSize=8, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                              fontSize=8, alignment=TA_LEFT))

    # contenido del PDF
    logo = Image('resources/images/logo.png', width=50*mm, height=26.4*mm)

    data = [['CANT.', 'PRODUCTO', 'P/U', 'DESC.', 'TOTAL']]
    
    firma = False
    total_desc = 0

    for cantidad, nombre, precio, descuento, importe in productos:
        data.append([
            cantidad,
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
    table2 = [['IMPORTE:', f'{total:,.2f}']]
    
    if pagado:
        table2.extend([['Pagado:', f'{pagado:,.2f}'],
                       ['Cambio:', f'{pagado-total + 0.:,.2f}']])
    
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

    # elementos para constuir el PDF
    elements = [
        logo,
        Spacer(1, 6),

        Paragraph('Avenida 15 No. 394 entre 52 y 54', styles['Center']),
        Paragraph('Fracc. Residencial Pensiones', styles['Center']),
        Spacer(1, 6),

        Paragraph('Teléfono: 999 649 0443', styles['Center']),
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
        
        Paragraph(f'¡Hoy se ahorró ${total_desc:,.2f}!', styles['Center']), 
        Spacer(1, 25),
        
        Paragraph('Autoriza descuentos: ' + '_'*24, styles['Left'])] if firma else []
    
    elements += [
        Spacer(1, 15),
        
        Paragraph(f'Le atendió: {vendedor}', styles['Center']),
        Paragraph(pie, styles['Center'])]

    # Build the PDF document
    doc.build(elements)
    
    # imprimir archivo temporal
    from configparser import ConfigParser
    
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini')
    
    enviarAImpresora(filename, int(config['IMPRESORAS']['prompt_tickets']))


def generarTicketCompra(crsr, idx):
    """
    Genera el ticket de compra a partir de un identificador en la base de datos.
    """
    # obtener datos de la compra, de la base de datos
    crsr.execute('''
    SELECT	cantidad,
            P.abreviado || IIF(VD.duplex, ' (a doble cara)', ''),
            precio,
            descuento,
            importe
    FROM	Ventas_Detallado AS VD
            LEFT JOIN Productos AS P
                   ON VD.id_productos = P.id_productos
    WHERE	id_ventas = ?;
    ''', (idx,))

    productos = crsr.fetchall()

    # más datos para el ticket
    crsr.execute('''
    SELECT	U.nombre,
            fecha_hora_creacion,
            recibido,
            metodo_pago
    FROM	Ventas_Detallado AS VD
            LEFT JOIN Ventas AS V
                   ON VD.id_ventas = V.id_ventas
            LEFT JOIN Usuarios AS U
                   ON V.id_usuarios = U.id_usuarios
    WHERE	VD.id_ventas = ?;
    ''', (idx,))

    vendedor, fechaCreacion, pagado, metodo = crsr.fetchone()
    
    # cambiar método de pago (abreviatura)
    if metodo == 'Efectivo': metodo = 'EFEC'
    elif metodo == 'Transferencia bancaria': metodo = 'TRF'
    else: metodo = 'TVP'
    
    _generarTicketPDF(idx, productos, vendedor, fechaCreacion, pagado, metodo)


def generarTicketPresupuesto(productos, vendedor):
    """
    Genera un ticket para el presupuesto de una compra.
    """
    from PyQt5.QtCore import QDateTime
    
    _generarTicketPDF(0, productos, vendedor, 
                      QDateTime.currentDateTime(), 0., None)
#####################################
# </FUNCIONES PARA GENERAR TICKETS> #
#####################################
