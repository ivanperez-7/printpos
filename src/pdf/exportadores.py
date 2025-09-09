from .generadores import generar_orden_compra
from sql import ManejadorVentas


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
