"""
Key points:
Identity Columns: Firebird's GENERATED ALWAYS AS IDENTITY is translated to autoincrement=True in SQLAlchemy.
BLOB: Firebird's BLOB SUB_TYPE 1 or BLOB SUB_TYPE 0 corresponds to SQLAlchemy's BLOB type.
Unique Constraints: I've included the UniqueConstraint for columns that need to be unique.
Relationships: For foreign keys and relationships, I've used the ForeignKey and relationship constructs in SQLAlchemy.
Computed Columns: SQLAlchemy does not support direct computed columns like Firebird. You may need to handle them in your application
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base()


class Caja(Base):
    __tablename__ = 'CAJA'

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    fecha_hora = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(BLOB)  # Firebird BLOB SUB_TYPE 1
    id_metodo_pago = Column(Integer, ForeignKey('METODOS_PAGO.id_metodo_pago'), nullable=False)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)

    metodo_pago = relationship('MetodosPago', back_populates='cajas')
    usuario = relationship('Usuarios', back_populates='cajas')


class Clientes(Base):
    __tablename__ = 'CLIENTES'

    id_clientes = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(30), nullable=False)
    correo = Column(String(100))
    direccion = Column(String(100))
    rfc = Column(String(100))
    cliente_especial = Column(Boolean, default=False, nullable=False)
    descuentos = Column(BLOB)  # Firebird BLOB SUB_TYPE 1

    ventas = relationship('Ventas', back_populates='cliente')

    __table_args__ = (
        UniqueConstraint('nombre', 'telefono', name='unique_nombre_telefono'),
    )


class Inventario(Base):
    __tablename__ = 'INVENTARIO'

    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    tamano_lote = Column(Float, nullable=False)
    precio_lote = Column(Float, nullable=False)
    minimo_lotes = Column(Float, nullable=False)
    unidades_restantes = Column(Float, nullable=False)

    # Computed columns
    precio_unidad = Column(Float, default=None, nullable=False)
    lotes_restantes = Column(Integer, default=None, nullable=False)

    __table_args__ = (
        UniqueConstraint('nombre', name='unique_inventario_nombre'),
    )


class MetodosPago(Base):
    __tablename__ = 'METODOS_PAGO'

    id_metodo_pago = Column(Integer, primary_key=True, autoincrement=True)
    metodo = Column(String(30), nullable=False)
    comision_porcentaje = Column(Float, default=0.0, nullable=False)

    cajas = relationship('Caja', back_populates='metodo_pago')
    ventas_pagos = relationship('VentasPagos', back_populates='metodo_pago')

    __table_args__ = (
        UniqueConstraint('metodo', name='unique_metodo_pago'),
    )


class Productos(Base):
    __tablename__ = 'PRODUCTOS'

    id_productos = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(100), nullable=False)
    descripcion = Column(String(100), nullable=False)
    abreviado = Column(String(50), nullable=False)
    categoria = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    ventas_detallado = relationship('VentasDetallado', back_populates='producto')
    productos_gran_formato = relationship('ProductosGranFormato', back_populates='producto')
    productos_intervalos = relationship('ProductosIntervalos', back_populates='producto')
    productos_utiliza_inventario = relationship('ProductosUtilizaInventario', back_populates='producto')

    __table_args__ = (
        UniqueConstraint('codigo', name='unique_producto_codigo'),
    )


class ProductosGranFormato(Base):
    __tablename__ = 'PRODUCTOS_GRAN_FORMATO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    min_m2 = Column(Float, nullable=False)
    precio_m2 = Column(Float, nullable=False)

    producto = relationship('Productos', back_populates='productos_gran_formato')


class ProductosIntervalos(Base):
    __tablename__ = 'PRODUCTOS_INTERVALOS'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    desde = Column(Float, nullable=False)
    precio_con_iva = Column(Float, nullable=False)
    duplex = Column(Boolean, nullable=False)

    producto = relationship('Productos', back_populates='productos_intervalos')

    __table_args__ = (
        UniqueConstraint('id_productos', 'desde', 'duplex', name='unique_producto_intervalos'),
    )


class ProductosUtilizaInventario(Base):
    __tablename__ = 'PRODUCTOS_UTILIZA_INVENTARIO'

    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    id_inventario = Column(Integer, ForeignKey('INVENTARIO.id_inventario'), primary_key=True)
    utiliza_inventario = Column(Float, nullable=False)

    producto = relationship('Productos', back_populates='productos_utiliza_inventario')
    inventario = relationship('Inventario')


class Usuarios(Base):
    __tablename__ = 'USUARIOS'

    id_usuarios = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    permisos = Column(String(30))
    foto_perfil = Column(BLOB)  # Firebird BLOB SUB_TYPE 0

    cajas = relationship('Caja', back_populates='usuario')
    ventas = relationship('Ventas', back_populates='usuario')
    ventas_pagos = relationship('VentasPagos', back_populates='usuario')

    __table_args__ = (
        UniqueConstraint('usuario', name='unique_usuario'),
    )


class Ventas(Base):
    __tablename__ = 'VENTAS'

    id_ventas = Column(Integer, primary_key=True, autoincrement=True)
    id_clientes = Column(Integer, ForeignKey('CLIENTES.id_clientes'), nullable=False)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)
    fecha_hora_creacion = Column(DateTime, nullable=False)
    fecha_hora_entrega = Column(DateTime, nullable=False)
    comentarios = Column(BLOB)  # Firebird BLOB SUB_TYPE 1
    requiere_factura = Column(Boolean, nullable=False)
    estado = Column(BLOB, nullable=False)  # Firebird BLOB SUB_TYPE 1

    cliente = relationship('Clientes', back_populates='ventas')
    usuario = relationship('Usuarios', back_populates='ventas')
    ventas_detallado = relationship('VentasDetallado', back_populates='venta')
    ventas_pagos = relationship('VentasPagos', back_populates='venta')


class VentasDetallado(Base):
    __tablename__ = 'VENTAS_DETALLADO'

    id_ventas = Column(Integer, ForeignKey('VENTAS.id_ventas'), primary_key=True)
    id_productos = Column(Integer, ForeignKey('PRODUCTOS.id_productos'), primary_key=True)
    cantidad = Column(Float, nullable=False)
    precio = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0, nullable=False)
    especificaciones = Column(BLOB, nullable=False)  # Firebird BLOB SUB_TYPE 1
    duplex = Column(Boolean, nullable=False)
    importe = Column(Float, nullable=False)

    venta = relationship('Ventas', back_populates='ventas_detallado')
    producto = relationship('Productos', back_populates='ventas_detallado')


class VentasPagos(Base):
    __tablename__ = 'VENTAS_PAGOS'

    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_ventas = Column(Integer, ForeignKey('VENTAS.id_ventas'), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('METODOS_PAGO.id_metodo_pago'), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    recibido = Column(Float)
    id_usuarios = Column(Integer, ForeignKey('USUARIOS.id_usuarios'), nullable=False)

    venta = relationship('Ventas', back_populates='ventas_pagos')
    metodo_pago = relationship('MetodosPago', back_populates='ventas_pagos')
    usuario = relationship('Usuarios', back_populates='ventas_pagos')


# Create engine and session (example)
engine = create_engine('firebird+fdb://user:password@localhost:3050/db.fdb')
Base.metadata.create_all(engine)
