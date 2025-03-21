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
    'VentaPago'
]

Base = declarative_base()


class Caja(Base):
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
    __tablename__ = 'METODOS_PAGO'

    id_metodo_pago = Column(Integer, primary_key=True)
    metodo = Column(String(30), nullable=False)
    comision_porcentaje = Column(Float, default=0.0)


class Producto(Base):
    __tablename__ = 'PRODUCTOS'

    id_productos = Column(Integer, primary_key=True)
    codigo = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(100), nullable=False)
    abreviado = Column(String(50), nullable=False)
    categoria = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class ProductoGranFormato(Base):
    __tablename__ = 'PRODUCTOS_GRAN_FORMATO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    min_m2 = Column(Float, nullable=False)
    precio_m2 = Column(Float, nullable=False)

    producto = relationship('Producto', backref='gran_formato')


class ProductoIntervalo(Base):
    __tablename__ = 'PRODUCTOS_INTERVALOS'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    desde = Column(Float, nullable=False)
    precio_con_iva = Column(Float, nullable=False)
    duplex = Column(Boolean, nullable=False)

    producto = relationship('Producto', backref='intervalos')


class ProductoUtilizaInventario(Base):
    __tablename__ = 'PRODUCTOS_UTILIZA_INVENTARIO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    id_inventario = Column(Integer, ForeignKey('INVENTARIO.id_inventario'), primary_key=True)
    utiliza_inventario = Column(Float, nullable=False)

    producto = relationship('Producto', backref='utiliza_inventario')
    inventario = relationship('Inventario', backref='productos_utilizan')


class Usuario(Base):
    __tablename__ = 'USUARIOS'

    id_usuarios = Column(Integer, primary_key=True)
    usuario = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    permisos = Column(String(30))
    foto_perfil = Column(BLOB)


class Venta(Base):
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
