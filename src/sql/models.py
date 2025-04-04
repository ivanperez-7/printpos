from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, ForeignKey, Text, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from core import Moneda

__all__ = [
    'Base',
    'Caja',
    'Cliente',
    'Inventario',
    'MetodoPago',
    'Producto',
    'ProductoGranFormato',
    'ProductoIntervalo',
    'ProductoUtilizaInventario',
    'Usuario',
    'Venta',
    'VentaDetalle',
    'VentaPago',
]

Base = declarative_base()


class Caja(Base):
    """
    Representa un movimiento de caja en el sistema.

    Atributos:
        id_movimiento (int): Identificador único del movimiento.
        fecha_hora (datetime): Fecha y hora del movimiento.
        monto (float): Monto del movimiento.
        descripcion (str): Descripción del movimiento.
        id_metodo_pago (int): Identificador del método de pago asociado.
        id_usuarios (int): Identificador del usuario que realizó el movimiento.
    """
    __tablename__ = 'CAJA'

    id_movimiento = Column(Integer, primary_key=True)
    fecha_hora = Column(TIMESTAMP, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(Text)
    id_metodo_pago = Column(Integer, ForeignKey('METODOS_PAGO.id_metodo_pago'), nullable=False)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)

    metodo_pago = relationship('MetodoPago', backref='movimientos_caja')
    usuario = relationship('Usuario', backref='movimientos_caja')


class Cliente(Base):
    """
    Representa un cliente en el sistema.

    Atributos:
        id_clientes (int): Identificador único del cliente.
        nombre (str): Nombre del cliente.
        telefono (str): Teléfono del cliente.
        correo (str): Correo electrónico del cliente.
        direccion (str): Dirección del cliente.
        rfc (str): RFC del cliente.
        cliente_especial (bool): Indica si el cliente es especial.
        descuentos (str): Descuentos aplicables al cliente.
    """
    __tablename__ = 'CLIENTES'

    id_clientes = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(30), nullable=False)
    correo = Column(String(100))
    direccion = Column(String(100))
    rfc = Column(String(100))
    cliente_especial = Column(Boolean, default=False, nullable=False)
    descuentos = Column(Text)


class Inventario(Base):
    """
    Representa un inventario de productos.

    Atributos:
        id_inventario (int): Identificador único del inventario.
        nombre (str): Nombre del inventario.
        tamano_lote (float): Tamaño del lote en unidades.
        precio_lote (float): Precio del lote.
        minimo_lotes (float): Mínimo de lotes requeridos.
        unidades_restantes (float): Unidades restantes en el inventario.
    """
    __tablename__ = 'INVENTARIO'

    id_inventario = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    tamano_lote = Column(Float, nullable=False)
    precio_lote = Column(Float, nullable=False)
    minimo_lotes = Column(Float, nullable=False)
    unidades_restantes = Column(Float, nullable=False)

    @property
    def precio_unidad(self):
        return self.precio_lote / self.tamano_lote

    @property
    def lotes_restantes(self):
        return self.unidades_restantes // self.tamano_lote


class MetodoPago(Base):
    """
    Representa un método de pago.

    Atributos:
        id_metodo_pago (int): Identificador único del método de pago.
        metodo (str): Nombre del método de pago.
        comision_porcentaje (float): Porcentaje de comisión asociado.
    """
    __tablename__ = 'METODOS_PAGO'

    id_metodo_pago = Column(Integer, primary_key=True)
    metodo = Column(String(30), nullable=False)
    comision_porcentaje = Column(Float, default=0.0)


class Producto(Base):
    """
    Representa un producto en el sistema.

    Atributos:
        id_productos (int): Identificador único del producto.
        codigo (str): Código único del producto.
        descripcion (str): Descripción del producto.
        abreviado (str): Nombre abreviado del producto.
        categoria (str): Categoría del producto.
        is_active (bool): Indica si el producto está activo.
    """
    __tablename__ = 'PRODUCTOS'

    id_productos = Column(Integer, primary_key=True)
    codigo = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(100), nullable=False)
    abreviado = Column(String(50), nullable=False)
    categoria = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ProductoGranFormato(Base):
    """
    Representa un producto de gran formato.

    Atributos:
        id_productos (int): Identificador del producto asociado.
        min_m2 (float): Mínimo de metros cuadrados requeridos.
        precio_m2 (float): Precio por metro cuadrado.
    """
    __tablename__ = 'PRODUCTOS_GRAN_FORMATO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    min_m2 = Column(Float, nullable=False)
    precio_m2 = Column(Float, nullable=False)

    producto = relationship('Producto', backref='gran_formato')


class ProductoIntervalo(Base):
    """
    Representa un producto con precios por intervalos.

    Atributos:
        id_productos (int): Identificador del producto asociado.
        desde (float): Cantidad mínima para aplicar el precio.
        precio_con_iva (float): Precio con IVA incluido.
        duplex (bool): Indica si el producto es dúplex.
    """
    __tablename__ = 'PRODUCTOS_INTERVALOS'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    desde = Column(Float, nullable=False)
    precio_con_iva = Column(Float, nullable=False)
    duplex = Column(Boolean, nullable=False)

    producto = relationship('Producto', backref='intervalos')


class ProductoUtilizaInventario(Base):
    """
    Relaciona un producto con un inventario.

    Atributos:
        id_productos (int): Identificador del producto asociado.
        id_inventario (int): Identificador del inventario asociado.
        utiliza_inventario (float): Cantidad de inventario utilizada.
    """
    __tablename__ = 'PRODUCTOS_UTILIZA_INVENTARIO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    id_inventario = Column(Integer, ForeignKey('INVENTARIO.id_inventario'), primary_key=True)
    utiliza_inventario = Column(Float, nullable=False)

    producto = relationship('Producto', backref='utiliza_inventario')
    inventario = relationship('Inventario', backref='productos_utilizan')


class Usuario(Base):
    """
    Representa un usuario del sistema.

    Atributos:
        id_usuarios (int): Identificador único del usuario.
        usuario (str): Nombre de usuario.
        nombre (str): Nombre completo del usuario.
        permisos (str): Permisos asignados al usuario.
        foto_perfil (bytes): Foto de perfil del usuario.
    """
    __tablename__ = 'USUARIOS'

    id_usuarios = Column(Integer, primary_key=True)
    usuario = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    permisos = Column(String(30))
    foto_perfil = Column(BLOB)


class Venta(Base):
    """
    Representa una venta realizada en el sistema.

    Atributos:
        id_ventas (int): Identificador único de la venta.
        id_clientes (int): Identificador del cliente asociado.
        id_usuarios (int): Identificador del usuario que realizó la venta.
        fecha_hora_creacion (datetime): Fecha y hora de creación de la venta.
        fecha_hora_entrega (datetime): Fecha y hora de entrega de la venta.
        comentarios (str): Comentarios adicionales sobre la venta.
        requiere_factura (bool): Indica si la venta requiere factura.
        estado (str): Estado actual de la venta.
    """
    __tablename__ = 'VENTAS'

    id_ventas = Column(Integer, primary_key=True)
    id_clientes = Column(Integer, ForeignKey('CLIENTES.id_clientes'), nullable=False)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)
    fecha_hora_creacion = Column(TIMESTAMP, nullable=False)
    fecha_hora_entrega = Column(TIMESTAMP, nullable=False)
    comentarios = Column(Text)
    requiere_factura = Column(Boolean, nullable=False)
    estado = Column(Text, nullable=False)

    cliente = relationship('Cliente', backref='ventas')
    usuario = relationship('Usuario', backref='ventas')


class VentaDetalle(Base):
    """
    Representa el detalle de una venta.

    Atributos:
        id_ventas (int): Identificador de la venta asociada.
        id_productos (int): Identificador del producto vendido.
        cantidad (float): Cantidad vendida.
        precio (float): Precio unitario del producto.
        descuento (float): Descuento aplicado.
        especificaciones (str): Especificaciones adicionales.
        duplex (bool): Indica si el producto es dúplex.
        importe (float): Importe total del detalle.
    """
    __tablename__ = 'VENTAS_DETALLADO'

    id_ventas = Column(Integer, ForeignKey('VENTAS.id_ventas'), primary_key=True)
    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    cantidad = Column(Float, nullable=False)
    precio = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0, nullable=False)
    especificaciones = Column(Text, nullable=False)
    duplex = Column(Boolean, nullable=False)
    importe = Column(Float, nullable=False)

    venta = relationship('Venta', backref='detalles')
    producto = relationship('Producto', backref='detalles')


class VentaPago(Base):
    """
    Representa un pago realizado para una venta.

    Atributos:
        id_pago (int): Identificador único del pago.
        id_ventas (int): Identificador de la venta asociada.
        id_metodo_pago (int): Identificador del método de pago utilizado.
        fecha_hora (datetime): Fecha y hora del pago.
        monto (float): Monto pagado.
        recibido (float): Monto recibido.
        id_usuarios (int): Identificador del usuario que registró el pago.
    """
    __tablename__ = 'VENTAS_PAGOS'

    id_pago = Column(Integer, primary_key=True)
    id_ventas = Column(Integer, ForeignKey('VENTAS.id_ventas'), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('METODOS_PAGO.id_metodo_pago'), nullable=False)
    fecha_hora = Column(TIMESTAMP, nullable=False)
    monto = Column(Float, nullable=False)
    recibido = Column(Float)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)

    venta = relationship('Venta', backref='pagos')
    metodo_pago = relationship('MetodoPago', backref='pagos')
    usuario = relationship('Usuario', backref='pagos')
