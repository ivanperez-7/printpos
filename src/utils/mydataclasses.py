from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import overload, Iterator, Iterable, TYPE_CHECKING

from PySide6.QtCore import QDateTime

if TYPE_CHECKING:
    import sql
from . import Moneda


@dataclass
class Usuario:
    """ Clase para mantener registro de un usuario. """
    id: int
    usuario: str
    nombre: str
    permisos: str = 'Vendedor'
    foto_perfil: bytes = None
    rol: str = 'Vendedor'

    def __post_init__(self):
        self.rol = self.rol.upper()

    @property
    def administrador(self):
        """ Regresa un booleano que dice si el usuario es administrador. """
        return self.permisos.upper() == 'ADMINISTRADOR'

    @classmethod
    def generarUsuarioActivo(cls, manejador: sql.ManejadorUsuarios):
        """ Genera clase Usuario dada una conexión válida a la DB. """
        usuario = manejador.usuarioActivo
        result = manejador.obtenerUsuario(usuario)
        return cls(*result, manejador.rolActivo)


@dataclass
class BaseItem:
    """ Clase para mantener registro de un producto simple de la venta. """
    id: int  # identificador interno en la base de datos
    codigo: str  # nombre del producto
    nombre_ticket: str  # nombre para mostrar en tickets y órdenes
    precio_unit: float  # precio por unidad
    descuento_unit: float  # cantidad a descontar por unidad
    cantidad: int  # cantidad solicitada por el cliente
    notas: str  # especificaciones del producto

    @property
    def importe(self):
        """ Costo total del producto. """
        raise NotImplementedError('BEIS CLASSSS')

    @property
    def total_descuentos(self):
        """ Regresa el total de descuentos (descuento * cantidad). """
        raise NotImplementedError('BEIS CLASSSS')


@dataclass
class ItemVenta(BaseItem):
    """ Clase para mantener registro de un producto simple de la venta. """
    duplex: bool  # dicta si el producto es duplex

    def __post_init__(self):
        if self.duplex:
            self.nombre_ticket += ' (a doble cara)'

    @property
    def importe(self):
        """ Costo total del producto. """
        return (self.precio_unit - self.descuento_unit) * self.cantidad

    @property
    def total_descuentos(self):
        """ Regresa el total de descuentos (descuento * cantidad). """
        return self.descuento_unit * self.cantidad

    def __iter__(self):
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        yield from (self.cantidad,
                    self.codigo + (' (a doble cara)' if self.duplex else ''),
                    self.notas,
                    self.precio_unit,
                    self.descuento_unit,
                    self.importe)


@dataclass
class ItemGranFormato(BaseItem):
    """ Clase para un producto de tipo gran formato.
        Reimplementa métodos `importe` y `total_descuentos`. """
    min_m2: float
    
    def __post_init__(self):
        self.duplex = False

    @property
    def importe(self):
        cantidad = max(self.min_m2, self.cantidad)
        return (self.precio_unit - self.descuento_unit) * cantidad

    @property
    def total_descuentos(self):
        cantidad = max(self.min_m2, self.cantidad)
        return self.descuento_unit * cantidad

    def __iter__(self):
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        yield from (self.cantidad,
                    self.codigo,
                    self.notas,
                    self.precio_unit,
                    self.descuento_unit,
                    self.importe)


@dataclass
class Venta:
    """ Clase para mantener registro de una venta. """
    productos: list[BaseItem] = field(default_factory=list)
    fechaCreacion: QDateTime = QDateTime.currentDateTime()
    fechaEntrega: QDateTime = QDateTime(fechaCreacion)
    requiere_factura: bool = False
    comentarios: str = ''
    id_cliente: int = 1
    metodo_pago: str = 'Efectivo'

    @property
    def total(self):
        return Moneda.sum(prod.importe for prod in self.productos)

    @property
    def total_descuentos(self):
        return Moneda.sum(prod.total_descuentos for prod in self.productos)

    @property
    def esVentaDirecta(self):
        """ Compara fechas de creación y entrega para determinar si la venta será un pedido. """
        return self.fechaCreacion == self.fechaEntrega

    @property
    def ventaVacia(self):
        return len(self.productos) == 0

    def agregarProducto(self, item: ItemVenta):
        self.productos.append(item)

    def quitarProducto(self, idx: int):
        self.productos.pop(idx)

    def reajustarPrecios(self, manejador: sql.ManejadorProductos):
        """ Algoritmo para reajustar precios de productos simples al haber cambios de cantidad.
            Por cada grupo de productos idénticos:
                1. Calcular cantidad de productos duplex y cantidad de no duplex.
                2. Obtener precio NO DUPLEX con el total de ambas cantidades.
                3. Obtener precio DUPLEX con la cantidad duplex correspondiente.
                4. A todos los productos del grupo, asignar el mínimo de los dos precios obtenidos. """
        for productos in self._obtenerGruposProductos():
            id_prod = productos[0].id
            cantidad = sum(p.cantidad for p in productos)
            cantidadDuplex = sum(p.cantidad for p in productos if p.duplex)

            precioNormal = manejador.obtenerPrecioSimple(id_prod, cantidad, False)
            precioDuplex = manejador.obtenerPrecioSimple(id_prod, cantidadDuplex, True)
            nuevoPrecio = min(precioNormal, precioDuplex or precioNormal)

            for p in productos:
                p.precio_unit = nuevoPrecio

    def _obtenerGruposProductos(self) -> Iterator[list[ItemVenta]]:
        """ Obtiene un generador con listas de productos, separadas por identificador. """
        out = dict()
        for prod in self.productos:
            if not isinstance(prod, ItemVenta):
                continue
            try:
                out[prod.id].append(prod)
            except KeyError:
                out[prod.id] = [prod]
        yield from out.values()

    def __len__(self):
        return len(self.productos)

    def __iter__(self):
        yield from self.productos

    def __getitem__(self, i: int):
        return self.productos[i]


@dataclass
class Movimiento:
    """ Clase para mantener registro de un movimiento en la caja. """
    fecha_hora: datetime
    monto: float
    descripcion: str
    metodo: str
    usuario: str

    @property
    def esIngreso(self):
        return self.monto > 0

    def __iter__(self):
        """ Alimenta las tablas principales:
        
            Fecha y hora | Monto | Descripción | Método | Usuario. """
        yield from (self.fecha_hora, self.monto, self.descripcion,
                    self.metodo, self.usuario)


class Caja:
    """ Clase para manejar todos los movimientos en caja. """
    movimientos: list[Movimiento]

    @overload
    def __init__(self, movimientos: list[tuple]) -> None:
        ...

    @overload
    def __init__(self, movimientos: list[Movimiento]) -> None:
        ...

    def __init__(self, movimientos: list[tuple] | list[Movimiento] = None):
        if movimientos is not None and not isinstance(movimientos, list):
            raise TypeError('Esperada lista de tuplas o Movimiento.')
        if not movimientos:
            self.movimientos = []
            return

        mov = movimientos[0]

        if isinstance(mov, Movimiento):
            self.movimientos = movimientos
        elif isinstance(mov, tuple):
            self.movimientos = [Movimiento(*m) for m in movimientos]
        else:
            raise TypeError('Lista debe ser de tuplas o Movimiento.')

    @property
    def todoIngresos(self):
        """ Regresa objeto `filter` de movimientos que son ingresos. """
        return filter(lambda m: m.esIngreso, self.movimientos)

    @property
    def todoEgresos(self):
        """ Regresa objeto `filter` de movimientos que son egresos. """
        return filter(lambda m: not m.esIngreso, self.movimientos)

    def _total(self, _iter: Iterable[Movimiento], metodo: str = None):
        if metodo:
            _iter = filter(lambda m: m.metodo.startswith(metodo), _iter)
        return Moneda.sum(m.monto for m in _iter)

    def totalIngresos(self, metodo: str = None):
        return self._total(self.todoIngresos, metodo)

    def totalEgresos(self, metodo: str = None):
        return self._total(self.todoEgresos, metodo)

    def totalCorte(self, metodo: str = None):
        return self._total(self.movimientos, metodo)
