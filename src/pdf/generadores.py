""" Provee métodos para generar diversos PDF en bytes. """

from __future__ import annotations

from datetime import datetime
import io
from typing import TYPE_CHECKING

from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from PySide6.QtCore import QFile, QIODevice

if TYPE_CHECKING:
    from utils.mydataclasses import BaseItem, Caja
from config import INI
from core import Moneda
from utils.myutils import chunkify, formatdate, stringify_float

__all__ = ['generarOrdenCompra', 'generarTicketPDF', 'generarCortePDF']


def generarOrdenCompra(
    productos: list[tuple],
    folio: int,
    nombre: str,
    telefono: str,
    total: Moneda,
    anticipo: Moneda,
    fecha_creacion: datetime,
    fecha_entrega: datetime,
):
    """ Genera un PDF con el orden de compra correspondiente a
    la venta con índice `folio` en la base de datos.

    La orden de compra contiene:
        - Folio de venta
        - Cliente: Nombre y teléfono
        - Tabla de productos: (Cantidad, producto, especificaciones, precio, importe)
            Máx. 6 por página
        - Total a pagar, anticipo recibido y saldo restante
        - Fecha de creación
        - Fecha de entrega """
    assert isinstance(productos, list) and len(productos), f'Argumento {productos=} no valido.'
    assert anticipo is not None, f'Venta {folio=} es directa, no pedido.'

    # objetos para PDF combinado y PDF base
    orden_writer = PdfWriter()

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='codigo', fontSize=10))
    estilos.add(ParagraphStyle(name='especificaciones', fontSize=8, leading=11))

    # divide en grupos de 6 productos e itera sobre ellos
    for chunk in chunkify(productos, 6):
        # inicializar canvas y E/S de bytes
        packet = io.BytesIO()
        can = Canvas(packet)

        # <escribir datos en el canvas>
        can.setFont('Helvetica-Bold', 10)
        can.drawRightString(373, 491, str(folio))
        can.drawCentredString(353, 192, str(total))

        can.setFont('Helvetica', 12)
        can.drawRightString(373, 546, formatdate(fecha_creacion))

        can.setFontSize(10)
        can.drawString(75, 493, nombre)
        can.drawString(75, 470, telefono)
        can.drawString(150, 448, formatdate(fecha_entrega))
        can.drawCentredString(353, 148, str(total - anticipo))
        can.drawCentredString(353, 170, str(anticipo))

        for (idx, producto) in enumerate(chunk):  # <tabla de productos>
            prodCantidad, prodNombre, prodEspecificaciones, prodPrecio, prodImporte = producto
            y_sep = 32.4 * idx  # separador por renglón de la tabla

            can.drawCentredString(49, 381 - y_sep, stringify_float(prodCantidad))
            can.drawCentredString(306, 381 - y_sep, f'{prodPrecio:,.2f}')
            can.drawCentredString(353, 381 - y_sep, f'{prodImporte:,.2f}')

            # nombre de producto, tamaño de fuente variable
            estilos['codigo'].fontSize = 10
            while estilos['codigo'].fontSize > 1:
                text = Paragraph(prodNombre, estilos['codigo'])
                w, h = text.wrap(59, 24)

                if h <= 24:
                    break
                estilos['codigo'].fontSize -= 0.1
            text.drawOn(can, 78.4, 398 - y_sep - h)

            # especificaciones, tamaño de fuente variable
            estilos['especificaciones'].fontSize = 9
            while estilos['especificaciones'].fontSize > 1:
                text = Paragraph(prodEspecificaciones, estilos['especificaciones'])
                w, h = text.wrap(125, 24)

                if h <= 24:
                    break
                estilos['especificaciones'].fontSize -= 0.1
            text.drawOn(can, 151.2, 398 - y_sep - h)  # </tabla de productos>
        # </escribir datos en el canvas>

        # guardar canvas y mover puntero de bytes al principio
        can.save()
        packet.seek(0)
        # crear variable para nuevo PDF y leer plantilla
        text_pdf = PdfReader(packet)
        # agregar trazados en el PDF de la plantilla
        base_pdf = PdfReader(INI.ORDEN_PDF)
        base_page = base_pdf.pages[0]
        base_page.merge_page(text_pdf.pages[0])

        orden_writer.add_page(base_page)

    # crear archivo temporal e imprimir
    orden_writer.write(buffer := io.BytesIO())
    assert buffer.getbuffer().nbytes > 0

    return buffer


def generarTicketPDF(
    productos: list[BaseItem],
    vendedor: str,
    folio: int = None,
    total: float = None,
    recibido: float = 0.0,
    metodo_pago: str = None,
    fecha_creacion=datetime.now(),
):
    """ Función general para generar el ticket de compra o presupuesto.
    Contiene:
        - Logo
        - Tabla de productos [Cantidad | Producto | Precio | Descuento | Importe]
        - Precio total
        - Nombre del vendedor
        - Folio de venta
        - Fecha y hora de creación """
    assert isinstance(productos, list) and len(productos), f'Argumento {productos=} no valido.'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=(80 * mm, 297 * mm), rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', fontSize=8, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Center_desc', fontSize=11, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', fontSize=8, alignment=TA_LEFT))

    # <contenido del PDF>
    data = [['CANT.', 'PRODUCTO', 'P/U', 'DESC.', 'TOTAL']]
    total_desc = Moneda.sum(prod.total_descuentos for prod in productos)

    for prod in productos:
        data.append(
            [
                stringify_float(prod.cantidad),
                Paragraph(prod.nombre_ticket, styles['Center']),
                f'{prod.precio_unit:,.2f}',
                f'{prod.descuento_unit:,.2f}' if prod.descuento_unit else '',
                f'{prod.importe:,.2f}',
            ]
        )

    # tabla de productos
    tabla_productos = Table(data, colWidths=[10 * mm, 28 * mm, 12 * mm, 12 * mm, 12 * mm])
    tabla_productos.setStyle(
        TableStyle(
            [  # ??? guatdefoq
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('LINEBELOW', (0, 0), (-1, 0), 0.4, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.black),
            ]
        )
    )

    # tablita pequeña para total y cambio
    if total is None:
        total = Moneda.sum(prod.importe for prod in productos)
    else:
        total = Moneda(total)

    data = [['IMPORTE:', str(total)]]

    if recibido and metodo_pago == 'EFEC':  # el único lugar donde sirve el dato 'recibido' xd
        recibido = Moneda(recibido)
        data += [['Pagado:', str(recibido)], ['Cambio:', str(recibido - total)]]

    tabla_importe = Table(data, hAlign='RIGHT')
    tabla_importe.setStyle(
        TableStyle(
            [
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]
        )
    )

    # elementos dinámicos, según se requieran
    if folio:
        titulo = 'TICKET DE COMPRA'
        pie = '¡Muchas gracias por su compra!'
        folio_str = '<b>Folio de venta</b>: {} {} <b>Método de pago</b>: {}'.format(
            folio, '&nbsp; ' * 7, metodo_pago
        )
    else:
        titulo = 'COTIZACIÓN DE VENTA'
        pie = '¡Muchas gracias por su visita!'
        folio_str = ''

    # convertir imagen en .qrc a imagen normal
    loggg = QFile(':img/resources/images/logo.png')
    assert loggg.open(QIODevice.ReadOnly), 'cant open logo.png pls check'
    baits = io.BytesIO(loggg.readAll().data())

    t = 0.017  # dimensiones del logo
    w, h = (3479 * t, 1845 * t)
    # </contenido del PDF>

    elements = [
        Image(baits, width=w * mm, height=h * mm),
        Spacer(1, 6),
        Paragraph(INI.CALLE_1, styles['Center']),
        Paragraph(INI.CALLE_2, styles['Center']),
        Spacer(1, 6),
        Paragraph(INI.TELEFONO, styles['Center']),
        Spacer(1, 6),
        Paragraph('* ' * 40, styles['Center']),
        Paragraph(titulo, styles['Center']),
        Paragraph('* ' * 40, styles['Center']),
        Paragraph(folio_str, styles['Left']),
        Paragraph('<b>Fecha</b>: ' + formatdate(fecha_creacion), styles['Left']),
        Spacer(1, 10),
        tabla_productos,
        Spacer(1, 7),
        tabla_importe,
    ]

    if total_desc:
        elements += [
            Spacer(1, 12),
            Paragraph(f'¡Hoy se ahorró ${total_desc}!', styles['Center_desc']),
            Spacer(1, 25),
            Paragraph('Autoriza descuentos: ' + '_' * 24, styles['Left']),
        ]

    elements += [
        Spacer(1, 15),
        Paragraph(f'Le atendió: {vendedor}', styles['Center']),
        Paragraph(pie, styles['Center']),
    ]

    doc.build(elements)
    assert buffer.getbuffer().nbytes > 0

    return buffer


def generarCortePDF(caja: Caja, responsable: str):
    """ Función para generar el corte de caja, comprendido entre fechas dadas.
    Contiene:
        - Realizado el: (fecha)
        - Nombre del usuario activo
        - Fecha inicial y final
        - Fondo inicial de caja
        - Tabla de movimientos
            Fecha y hora | Descripción | Método de pago | Cantidad
        - Tabla de resumen de movimientos
            Método de pago -> Ingresos | Egresos """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(80 * mm, 297 * mm),
        topMargin=0.0,
        bottomMargin=0.0,
        leftMargin=0.0,
        rightMargin=0.0,
    )

    # estilos de párrafos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', fontName='Helvetica', fontSize=9, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Foot', fontName='Helvetica', fontSize=11, alignment=TA_LEFT))

    # cálculos de ingresos
    ingresos_efectivo = caja.totalIngresos('Efectivo')
    ingresos_transferencia = caja.totalIngresos('Transferencia')
    ingresos_credito = caja.totalIngresos('Tarjeta de crédito')
    ingresos_debito = caja.totalIngresos('Tarjeta de débito')

    # cálculos de egresos
    egresos_efectivo = -caja.totalEgresos('Efectivo')
    egresos_transferencia = -caja.totalEgresos('Transferencia')
    egresos_credito = -caja.totalEgresos('Tarjeta de crédito')
    egresos_debito = -caja.totalEgresos('Tarjeta de débito')

    # totales (todos los métodos)
    total_efectivo = ingresos_efectivo - egresos_efectivo
    total_transferencia = ingresos_transferencia - egresos_transferencia
    total_credito = ingresos_credito - egresos_credito
    total_debito = ingresos_debito - egresos_debito

    esperado_ingresos = caja.totalIngresos()
    esperado_egresos = -caja.totalEgresos()
    esperado = caja.totalCorte()

    # elementos para constuir el PDF
    elements = [
        Paragraph('Resumen de movimientos de caja', styles['Heading1']),
        Spacer(1, 6),
        Paragraph('Realizado por: ' + responsable, styles['Left']),
        Paragraph('Fecha y hora: ' + formatdate(), styles['Left']),
        Spacer(1, 6),
        Paragraph('Resumen de ingresos', styles['Heading3']),
        Paragraph(f'Efectivo: ${ingresos_efectivo}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de crédito: ${ingresos_credito}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de débito: ${ingresos_debito}', styles['Left'], bulletText=' '),
        Paragraph(f'Transferencias bancarias: ${ingresos_transferencia}', styles['Left'], bulletText=' ',),
        Spacer(1, 6),
        Paragraph('Resumen de egresos', styles['Heading3']),
        Paragraph(f'Efectivo: ${egresos_efectivo}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de crédito: ${egresos_credito}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de débito: ${egresos_debito}', styles['Left'], bulletText=' '),
        Paragraph(f'Transferencias bancarias: ${egresos_transferencia}', styles['Left'], bulletText=' ',),
        Spacer(1, 6),
        Paragraph('Esperado', styles['Heading3']),
        Paragraph(f'Efectivo: ${total_efectivo}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de crédito: ${total_credito}', styles['Left'], bulletText=' '),
        Paragraph(f'Tarjeta de débito: ${total_debito}', styles['Left'], bulletText=' '),
        Paragraph(f'Transferencias bancarias: ${total_transferencia}', styles['Left'], bulletText=' ',),
        Spacer(1, 20),
        Paragraph('<b>' + f'Total de ingresos: ${esperado_ingresos}' + '</b>', styles['Foot']),
        Paragraph('<b>' + f'Total de egresos: ${esperado_egresos}' + '</b>', styles['Foot']),
        Paragraph(f'<b>Esperado en caja: ${esperado}</b>', styles['Foot']),
    ]

    # Build the PDF document
    doc.build(elements)
    assert buffer.getbuffer().nbytes > 0

    return buffer
