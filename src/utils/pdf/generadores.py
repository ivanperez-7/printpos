""" Provee métodos para generar diversos PDF en bytes. """
import io

from PySide6.QtCore import QDateTime

from Caja import Caja
from Login import Usuario

from utils.dinero import Dinero
from utils.myutils import chunkify, formatDate, leer_config
from utils.sql import ManejadorVentas


def _generarOrdenCompra(manejadorVentas: ManejadorVentas, idx: int):
    """ Genera un PDF con el orden de compra correspondiente a 
        la venta con índice `idx` en la base de datos.

        La orden de compra contiene:
            - Folio de venta
            - Cliente: Nombre y teléfono
            - Tabla de productos: (Cantidad, producto, especificaciones, precio, importe)
                Máx. 6 por página
            - Total a pagar, anticipo recibido y saldo restante
            - Fecha de creación
            - Fecha de entrega """
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    
    # leer datos de venta y de cliente
    nombre, telefono = manejadorVentas.obtenerClienteAsociado(idx)
    creacion, entrega = manejadorVentas.obtenerFechas(idx)
    
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
        can.drawCentredString(353, 148, f'{saldo}')
        can.drawCentredString(353, 170, f'{anticipo}')
        
        can.setFont('Helvetica-Bold', 10)
        can.drawCentredString(353, 192, f'{total}')
        can.setFont('Helvetica', 10)
        
        for i, (prodCantidad, prodNombre, prodEspecificaciones,
                prodPrecio, prodImporte) in enumerate(chunk):
            y_sep = -32.4 * i  # separador por renglón de la tabla
            
            can.drawCentredString(49, 381 + y_sep, f'{prodCantidad:,.2f}')
            can.drawCentredString(306, 381 + y_sep, f'{prodPrecio:,.2f}')
            can.drawCentredString(353, 381 + y_sep, f'{prodImporte:,.2f}')
            
            estilos['codigo'].fontSize = 10
            
            # tamaño de fuente variable
            while estilos['codigo'].fontSize > 1:
                text = Paragraph(prodNombre, estilos['codigo'])
                w, h = text.wrap(59, 24)
                
                if h <= 24:
                    break
                estilos['codigo'].fontSize -= 0.1
            text.drawOn(can, 78.4, 398 + y_sep - h)
            
            estilos['especificaciones'].fontSize = 8
            
            # tamaño de fuente variable
            while estilos['especificaciones'].fontSize > 1:
                text = Paragraph(prodEspecificaciones, estilos['especificaciones'])
                w, h = text.wrap(125, 24)
                
                if h <= 24:
                    break
                estilos['especificaciones'].fontSize -= 0.1
            text.drawOn(can, 151.2, 396 + y_sep - h)
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
    buffer = io.BytesIO()
    writer.write(buffer)
    
    return buffer


def _generarTicketPDF(folio: int, productos: list[tuple[int, str, float, float, float]],
                      vendedor: str, fechaCreacion: QDateTime = QDateTime.currentDateTime(), 
                      pagado: float = 0., total: float = None, metodo_pago: str = None):
    """ Función general para generar el ticket de compra o presupuesto.
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
    
    # archivo temporal
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer,
                            pagesize=(80 * mm, 297 * mm),
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
    logo = Image('resources/images/logo.png', width=50 * mm, height=26.4 * mm)
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
    tabla_productos = Table(data, colWidths=[10 * mm, 28 * mm, 12 * mm, 12 * mm, 12 * mm])
    
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
    if total is None: total = sum(p[4] for p in productos)
    total = Dinero(total)
    pagado = Dinero(pagado)
    
    table2 = [['IMPORTE:', f'{total}']]
    
    if pagado:
        table2.extend([['Pagado:', f'{pagado}'],
                       ['Cambio:', f'{pagado - total}']])
    
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
        
        folio = f'<b>Folio de venta</b>: {folio} ' \
                + '&nbsp; ' * 7 + f'<b>Método de pago</b>: {metodo_pago}'
    else:
        titulo = 'COTIZACIÓN DE VENTA'
        pie = '¡Muchas gracias por su visita!'
        folio = ''
    
    # leer datos de sucursal de archivo de configuración
    config = leer_config()
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
        
        Paragraph('* ' * 40, styles['Center']),
        Paragraph(titulo, styles['Center']),
        Paragraph('* ' * 40, styles['Center']),
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
        
        Paragraph('Autoriza descuentos: ' + '_' * 24, styles['Left'])] if firma else []
    
    elements += [
        Spacer(1, 15),
        
        Paragraph(f'Le atendió: {vendedor}', styles['Center']),
        Paragraph(pie, styles['Center'])]
    
    # Build the PDF document
    doc.build(elements)
    
    return buffer


def _generarCortePDF(caja: Caja, user: Usuario):
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
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=(80 * mm, 297 * mm),
                            topMargin=0., bottomMargin=0.,
                            leftMargin=0., rightMargin=0.)
    
    # estilos de párrafos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                              fontSize=9, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Foot', fontName='Helvetica',
                              fontSize=11, alignment=TA_LEFT))
    
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
        
        Paragraph('Realizado por: ' + user.nombre, styles['Left']),
        Paragraph('Fecha y hora: ' + formatDate(QDateTime.currentDateTime()), styles['Left']),
        Spacer(1, 6),
        
        Paragraph('Resumen de ingresos', styles['Heading3']),
        Paragraph(f'Efectivo: ${ingresos_efectivo:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de crédito: ${ingresos_credito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de débito: ${ingresos_debito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Transferencias bancarias: ${ingresos_transferencia:,.2f}', styles['Left'], bulletText='•'),
        Spacer(1, 6),
        
        Paragraph('Resumen de egresos', styles['Heading3']),
        Paragraph(f'Efectivo: ${egresos_efectivo:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de crédito: ${egresos_credito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de débito: ${egresos_debito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Transferencias bancarias: ${egresos_transferencia:,.2f}', styles['Left'], bulletText='•'),
        Spacer(1, 6),
        
        Paragraph('Esperado', styles['Heading3']),
        Paragraph(f'Efectivo: ${total_efectivo:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de crédito: ${total_credito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Tarjeta de débito: ${total_debito:,.2f}', styles['Left'], bulletText='•'),
        Paragraph(f'Transferencias bancarias: ${total_transferencia:,.2f}', styles['Left'], bulletText='•'),
        Spacer(1, 20),
        
        Paragraph('<b>' + f'Total de ingresos: ${esperado_ingresos:,.2f}' + '</b>', styles['Foot']),
        Paragraph('<b>' + f'Total de egresos: ${esperado_egresos:,.2f}' + '</b>', styles['Foot']),
        Paragraph(f'<b>Esperado en caja: ${esperado:,.2f}</b>', styles['Foot']),
    ]
    
    # Build the PDF document
    doc.build(elements)
    
    return buffer
