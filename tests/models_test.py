from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql.models import *


# Usamos un engine de SQLite en memoria
@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:', echo=True)

@pytest.fixture(scope='module')
def setup_database(engine):
    # Crea las tablas en la base de datos en memoria
    Base.metadata.create_all(engine)
    yield engine
    # Elimina las tablas después de las pruebas
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(setup_database, engine):
    # Crea una sesión para interactuar con la base de datos
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()  # Deshace cualquier cambio después de cada prueba
    session.close()

# Pruebas de los modelos

def test_create_cliente(session):
    cliente = Cliente(
        nombre="Juan Pérez",
        telefono="123456789",
        correo="juanperez@example.com",
        direccion="Calle Ficticia 123",
        rfc="JUAP123456"
    )
    session.add(cliente)
    session.commit()
    
    # Verifica que el cliente se haya insertado
    cliente_guardado = session.query(Cliente).filter_by(nombre="Juan Pérez").first()
    assert cliente_guardado is not None
    assert cliente_guardado.nombre == "Juan Pérez"
    assert cliente_guardado.telefono == "123456789"
    
def test_create_metodo_pago(session):
    metodo_pago = MetodoPago(metodo="Tarjeta", comision_porcentaje=2.5)
    session.add(metodo_pago)
    session.commit()
    
    metodo_guardado = session.query(MetodoPago).filter_by(metodo="Tarjeta").first()
    assert metodo_guardado is not None
    assert metodo_guardado.comision_porcentaje == 2.5

def test_create_venta(session):
    # Primero, creamos un cliente y un usuario para la venta
    cliente = Cliente(nombre="Carlos Ruiz", telefono="987654321")
    usuario = Usuario(usuario="admin", nombre="Administrador")
    session.add(cliente)
    session.add(usuario)
    session.commit()
    
    # Ahora, creamos una venta
    venta = Venta(
        id_clientes=cliente.id_clientes,
        id_usuarios=usuario.id_usuarios,
        fecha_hora_creacion=datetime.now(),
        fecha_hora_entrega=datetime.now(),
        comentarios="Venta de prueba",
        requiere_factura=False,
        estado="En proceso"
    )
    session.add(venta)
    session.commit()
    
    venta_guardada = session.query(Venta).filter_by(estado="En proceso").first()
    assert venta_guardada is not None
    assert venta_guardada.estado == "En proceso"

def test_create_producto(session):
    producto = Producto(
        codigo="PROD123",
        descripcion="Producto de prueba",
        abreviado="Prod123",
        categoria="Categoría A"
    )
    session.add(producto)
    session.commit()
    
    producto_guardado = session.query(Producto).filter_by(codigo="PROD123").first()
    assert producto_guardado is not None
    assert producto_guardado.descripcion == "Producto de prueba"
    assert producto_guardado.is_active is True

def test_create_caja(session):
    metodo_pago = MetodoPago(metodo="Efectivo", comision_porcentaje=0.0)
    usuario = Usuario(usuario="vendedor", nombre="Vendedor")
    session.add(metodo_pago)
    session.add(usuario)
    session.commit()
    
    caja = Caja(
        fecha_hora=datetime.now(),
        monto=100.0,
        descripcion="Ingreso de efectivo",
        id_metodo_pago=metodo_pago.id_metodo_pago,
        id_usuarios=usuario.id_usuarios
    )
    session.add(caja)
    session.commit()
    
    caja_guardada = session.query(Caja).filter_by(descripcion="Ingreso de efectivo").first()
    assert caja_guardada is not None
    assert caja_guardada.monto == 100.0
    assert caja_guardada.metodo_pago.metodo == "Efectivo"

