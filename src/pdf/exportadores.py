import io

import fitz
from pypdf import PdfWriter

from .generadores import generar_orden_compra, generar_ticket_pdf
from sql import ManejadorVentas


_ABREV_METODO = {
    'Efectivo': 'EFEC',
    'Transferencia bancaria': 'TRF',
    'Tarjeta de crédito': 'TVP',
    'Tarjeta de débito': 'TVP',
}

# margen inferior (pt) que se deja debajo del último contenido al recortar
_MARGEN_RECORTE = 8


def _recortar_inferior(buffer):
    """
    Recorta el espacio en blanco inferior de un ticket de una sola página.

    El ticket se genera con una altura fija (297 mm) que necesita la impresora
    térmica para imprimir bien, pero al exportarlo a un archivo ese alto sobra y
    deja un gran espacio en blanco. Aquí se calcula el contenido real (texto,
    trazos e imágenes) y se ajusta la página a esa altura más un pequeño margen.

    Devuelve un BytesIO con el PDF recortado.
    """
    buffer.seek(0)
    doc = fitz.open('pdf', buffer.read())
    pagina = doc[0]

    # límite inferior del contenido (eje Y top-down de fitz)
    y_max = 0.0
    for bloque in pagina.get_text('dict')['blocks']:
        y_max = max(y_max, bloque['bbox'][3])
    for trazo in pagina.get_drawings():
        y_max = max(y_max, trazo['rect'].y1)
    for img in pagina.get_images():
        for rect in pagina.get_image_rects(img[0]):
            y_max = max(y_max, rect.y1)

    # si se detectó contenido, recortar a su altura más un margen
    if y_max > 0:
        altura = min(pagina.rect.height, y_max + _MARGEN_RECORTE)
        pagina.set_cropbox(fitz.Rect(0, 0, pagina.rect.width, altura))

    salida = io.BytesIO()
    doc.save(salida)
    doc.close()
    salida.seek(0)
    return salida


def guardar_orden_compra(idx: int, manejador: ManejadorVentas, ruta: str):
    """
    Genera una orden de compra y la guarda como PDF en la ruta elegida por el usuario.
    No usa impresoras, solo genera el archivo.
    """
    productos = manejador.obtenerTablaOrdenCompra(idx)
    total = manejador.obtenerImporteTotal(idx)
    anticipo = manejador.obtenerAnticipo(idx)
    nombre, telefono = manejador.obtenerClienteAsociado(idx)
    creacion, entrega = manejador.obtenerFechas(idx)

    # generar PDF en memoria
    data = generar_orden_compra(productos, idx, nombre, telefono, total, anticipo, creacion, entrega)

    # guardar en archivo
    with open(ruta, "wb") as f:
        f.write(data.getbuffer())

    return True


def guardar_ticket_compra(idx: int, manejador: ManejadorVentas, ruta: str, nums: list[int] | slice = None):
    """
    Genera el/los ticket(s) de compra de una venta y los combina en un solo
    PDF guardado en la ruta elegida. No usa impresoras.

    Si la venta tiene varios pagos, cada ticket se concatena como una página
    más dentro del mismo archivo. `nums` permite exportar pagos específicos.
    """
    productos = list(manejador.obtenerTablaTicket(idx))
    pagos = manejador.obtenerPagosVenta(idx)

    if isinstance(nums, list):
        pagos = [pagos[i] for i in nums]
    elif isinstance(nums, slice):
        pagos = pagos[nums]

    if not pagos:
        return False

    # generar cada ticket en memoria, recortar el blanco inferior y concatenarlos
    writer = PdfWriter()
    for fecha, metodo, monto, pagado, vendedor in pagos:
        data = generar_ticket_pdf(productos, vendedor, idx, monto, pagado, _ABREV_METODO[metodo], fecha)
        writer.append(_recortar_inferior(data))

    with open(ruta, "wb") as f:
        writer.write(f)

    return True
