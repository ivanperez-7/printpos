""" Módulo con manejadores para tablas en la base de datos. """
import fdb

from PySide6.QtCore import QDate

from utils.mywidgets import WarningDialog


def crear_conexion(usuario: str, psswd: str, rol: str = None):
    from configparser import ConfigParser
    
    # leer datos de config.ini
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini')
    
    red_local = config['DEFAULT']['red_local']
    nombre = config['SUCURSAL']['nombre']
    
    try:
        conn = fdb.connect(
            dsn=red_local + f':{nombre}.fdb',
            user=usuario,
            password=psswd,
            charset='UTF8',
            role=rol)
        return conn
    except fdb.Error as err:
        print(f'Cannot open connection to database: {str(err)}')
        return None


class DatabaseManager:
    """ Clase general de un administrador de bases de datos.
    Permite ejecutar consultas varias y manejar las excepciones."""
    
    def __init__(self, conn: fdb.Connection,
                 error_txt: str = None,
                 handle_exceptions: bool = True):
        self.conn = conn
        self.crsr: fdb.Cursor = conn.cursor()
        self.error_txt = error_txt or '¡Acceso fallido a base de datos!'
        self.handle_exceptions = handle_exceptions
    
    def execute(self, query, parameters=None, commit=False):
        try:
            if parameters is None:
                self.crsr.execute(query)
            else:
                self.crsr.execute(query, parameters)
            if commit:
                self.conn.commit()
            return True
        except fdb.Error as err:
            if not self.handle_exceptions:
                raise err
            self.conn.rollback()
            WarningDialog(self.error_txt, str(err))
            return False
    
    def executemany(self, query, parameters=None, commit=False):
        try:
            if parameters is None:
                self.crsr.executemany(query)
            else:
                self.crsr.executemany(query, parameters)
            if commit:
                self.conn.commit()
            return True
        except fdb.Error as err:
            if not self.handle_exceptions:
                raise err
            self.conn.rollback()
            WarningDialog(self.error_txt, str(err))
            return False
    
    def fetchall(self, query, parameters=None) -> list | None:
        try:
            if parameters is None:
                self.crsr.execute(query)
            else:
                self.crsr.execute(query, parameters)
            return self.crsr.fetchall()
        except fdb.Error as err:
            if not self.handle_exceptions:
                raise err
            WarningDialog(self.error_txt, str(err))
            return None
    
    def fetchone(self, query, parameters=None) -> tuple | None:
        try:
            if parameters is None:
                self.crsr.execute(query)
            else:
                self.crsr.execute(query, parameters)
            return self.crsr.fetchone()
        except fdb.Error as err:
            if not self.handle_exceptions:
                raise err
            WarningDialog(self.error_txt, str(err))
            return None
    
    def obtenerUsuario(self) -> str | None:
        """ Obtiene nombre del usuario activo de la conexión. """
        result = self.fetchone("""
            SELECT  nombre
            FROM    usuarios
            WHERE   usuario = (
                SELECT  USER 
                FROM    RDB$DATABASE
            );
        """)
        
        if result:
            nombre, = result
            return nombre
        return None
    
    def obtenerVista(self, vista: str):
        """ Atajo de sentencia SELECT para obtener una vista. """
        return self.fetchall(f'SELECT * FROM {vista};')


class ManejadorCaja(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Caja. """
    
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        super().__init__(conn, error_txt)
    
    def obtenerMovimientos(self, inicio: QDate, final: QDate):
        """ Obtener historial completo de movimientos de caja.
            
            Requiere fechas de inicio y final, de tipo QDate. """
        return self.fetchall('''
            SELECT 	fecha_hora,
                    monto,
                    descripcion,
                    metodo,
                    U.nombre
            FROM 	Caja AS C
                    LEFT JOIN Usuarios AS U
                           ON C.id_usuarios = U.id_usuarios
            WHERE   ? <= CAST(fecha_hora AS DATE)
                    AND CAST(fecha_hora AS DATE) <= ?
            ORDER   BY fecha_hora DESC;
        ''', (inicio.toPython(), final.toPython()))
    
    def obtenerFechaPrimerMov(self):
        """ Obtener fecha del movimiento más antiguo. """
        result = self.fetchone('SELECT MIN(fecha_hora) FROM Caja;')
        
        if result:
            fecha, = result
            return fecha
    
    def insertarMovimiento(self, params: tuple, commit: bool = True):
        """ Registra ingreso o egreso en tabla historial de movimientos.
        
            Hace commit automáticamente, a menos que se indique lo contrario. """
        return self.execute('''
            INSERT INTO Caja (
                fecha_hora, monto,
                descripcion, metodo, id_usuarios
            )
            VALUES
                (?,?,?,?,?);
        ''', params, commit=commit)


class ManejadorClientes(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Clientes. """
    
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        super().__init__(conn, error_txt)
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar la tabla principal de clientes. """
        return self.fetchall('''
            SELECT  C.id_clientes,
                    nombre,
                    telefono,
                    correo,
                    direccion,
                    RFC,
                    MAX(fecha_hora_creacion) AS ultimaVenta
            FROM    Clientes AS C
                    LEFT JOIN Ventas AS V
                           ON C.id_clientes = V.id_clientes
            GROUP   BY 1, 2, 3, 4, 5, 6
            ORDER   BY C.id_clientes;
        ''')
    
    def obtenerCliente(self, id_cliente: int):
        """ Sentencia para obtener un cliente. """
        return self.fetchone('''
            SELECT  * 
            FROM    Clientes 
            WHERE id_clientes = ?;
        ''', (id_cliente,))
    
    def verificarCliente(self, nombre: str, telefono: str):
        """ Regresa cliente dados el nombre y el teléfono. """
        return self.fetchone('''
            SELECT  *
            FROM    Clientes
            WHERE   nombre = ?
                    AND telefono = ?;
        ''', (nombre, telefono))
    
    def obtenerDescuentosCliente(self, nombre: str, telefono: str):
        """ Obtener booleano de cliente especial, y cadena de descuentos. """
        return self.fetchone('''
            SELECT  cliente_especial,
                    descuentos
            FROM    Clientes
            WHERE   nombre = ?
                    AND telefono = ?;
        ''', (nombre, telefono))
    
    def insertarCliente(self, datosCliente: tuple):
        """ Sentencia para registrar cliente. Hace commit automáticamente. """
        return self.execute('''
            INSERT INTO Clientes (
                nombre, telefono, correo, direccion,
                RFC, cliente_especial, descuentos
            )
            VALUES
                (?,?,?,?,?,?,?);
        ''', datosCliente, commit=True)
    
    def actualizarCliente(self, idCliente, datosCliente: tuple):
        """ Sentencia para actualizar cliente. Hace commit automáticamente. """
        return self.execute('''
            UPDATE  Clientes
            SET     nombre = ?,
                    telefono = ?,
                    correo = ?,
                    direccion = ?,
                    RFC = ?,
                    cliente_especial = ?,
                    descuentos = ?
            WHERE   id_clientes = ?;
        ''', (*datosCliente, idCliente), commit=True)
    
    def eliminarCliente(self, idCliente):
        """ Sentencia para eliminar cliente. Hace commit automáticamente. """
        return self.execute('''
            DELETE  FROM Clientes
            WHERE   id_clientes = ?;
        ''', (idCliente,), commit=True)


class ManejadorInventario(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Inventario. """
    
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        super().__init__(conn, error_txt)
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar tabla principal de elementos. """
        return self.fetchall('''
            SELECT  id_inventario,
                    nombre,
                    tamano_lote,
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes,
                    lotes_restantes
            FROM    Inventario;
        ''')
    
    def obtenerInformacionPrincipal(self, id_inventario: int):
        """ Regresa información principal de un elemento:
            nombre, tamaño de lote, precio de lote, mínimo de lotes, unidades restantes. """
        return self.fetchone('''
            SELECT  nombre,
                    tamano_lote, 
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes
            FROM    Inventario 
            WHERE   id_inventario = ?;
        ''', (id_inventario,))
    
    def obtenerInventarioFaltante(self):
        """ Obtener inventario faltante (lotes < mínimo de lotes):
            nombre, lotes restantes, mínimo de lotes. """
        return self.fetchall('''
            SELECT  nombre,
                    lotes_restantes,
                    minimo_lotes
            FROM    Inventario 
            WHERE   lotes_restantes < minimo_lotes;
        ''')
    
    def obtenerIdInventario(self, nombre: str):
        """ Obtener id_inventario dado nombre de un elemento de inventario. """
        return self.fetchone('''
            SELECT  id_inventario
            FROM    Inventario 
            WHERE   nombre = ?;
        ''', (nombre,))
    
    def obtenerListaNombres(self):
        """ Obtener lista con nombres de todos los elementos de inventario. """
        return self.fetchall('SELECT nombre FROM Inventario;')
    
    def obtenerProdUtilizaInv(self, id_inventario: int):
        """ Obtener relación con productos en la tabla productos_utiliza_inventario. """
        return self.fetchall('''
            SELECT	codigo,
                    utiliza_inventario
            FROM	Productos_Utiliza_Inventario AS PUI
                    LEFT JOIN Productos AS P
                           ON PUI.id_productos = P.id_productos
            WHERE 	id_inventario = ?;
        ''', (id_inventario,))
    
    def agregarLotes(self, id_inventario: int, num_lotes: float):
        """ Agrega lotes a existencia del elemento. Hace commit automáticamente. """
        return self.execute('''
            UPDATE  Inventario
            SET     unidades_restantes = unidades_restantes + tamano_lote * ?
            WHERE   id_inventario = ?;
        ''', (num_lotes, id_inventario), commit=True)
    
    def insertarElemento(self, datos_elemento: tuple):
        """ Intenta registrar un elemento en la tabla y regresar 
            tupla con el índice recién insertado. No hace commit. """
        return self.fetchone('''
            INSERT INTO Inventario (
                nombre, tamano_lote, precio_lote,
                minimo_lotes, unidades_restantes
            )
            VALUES
                (?,?,?,?,?)
            RETURNING
                id_inventario;
        ''', datos_elemento)
    
    def editarElemento(self, id_inventario: int, datos_elemento: tuple):
        """ Intenta editar datos de un elemento en la tabla y regresar
            tupla con el índice recién editado. No hace commit. """
        return self.fetchone('''
            UPDATE  Inventario
            SET     nombre = ?,
                    tamano_lote = ?,
                    precio_lote = ?,
                    minimo_lotes = ?,
                    unidades_restantes = ?
            WHERE   id_inventario = ?
            RETURNING id_inventario;
        ''', (*datos_elemento, id_inventario))
    
    def eliminarElemento(self, id_inventario: int):
        """ Elimina un elemento de la tabla. Hace commit automáticamente. """
        return self.execute('''
            DELETE  FROM Inventario 
            WHERE   id_inventario = ?;
        ''', (id_inventario,), commit=True)
    
    def eliminarProdUtilizaInv(self, id_inventario: int):
        """ Elimina elemento de la tabla productos_utiliza_inventario.
            No hace commit, al ser parte inicial del proceso de registro/modificación. """
        return self.execute('''
            DELETE  FROM productos_utiliza_inventario
            WHERE   id_inventario = ?;
        ''', (id_inventario,), commit=False)
    
    def insertarProdUtilizaInv(self, id_inventario: int, params: list[tuple]):
        """ Inserta elemento en la tabla productos_utiliza_inventario.
            Hace commit, al ser parte final del proceso de registro/modificación. """
        params = [(id_inventario,) + param for param in params]
        
        return self.executemany('''
            INSERT INTO productos_utiliza_inventario (
                id_inventario, id_productos, utiliza_inventario
            )
            VALUES
                (?,?,?);
        ''', params, commit=True)


class ManejadorProductos(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Inventario. """
    
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        super().__init__(conn, error_txt)
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar tabla principal de productos. """
        return self.fetchall('''
            WITH Costo_Produccion (id_productos, costo) AS (
            SELECT	P.id_productos,
                    SUM(
                        COALESCE(PUI.utiliza_inventario * I.precio_unidad, 
                                0.0)
                    ) AS costo
            FROM  	Productos AS P
                    LEFT JOIN Productos_Utiliza_Inventario AS PUI
                           ON P.id_productos = PUI.id_productos
                    LEFT JOIN Inventario AS I
                           ON PUI.id_inventario = I.id_inventario
            GROUP	BY P.id_productos
            ORDER	BY P.id_productos ASC
            )

            SELECT  P.id_productos,
                    P.codigo,
                    P.descripcion 
                        || IIF(desde > 1, ', desde ' || ROUND(desde, 1) || ' unidades ', '')
                        || IIF(P_Inv.duplex, ' [PRECIO DUPLEX]', ''),
                    P.abreviado,
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) AS precio_con_iva, 
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) / 1.16 AS precio_sin_iva,
                    C_Prod.costo,
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) - C_Prod.costo AS utilidad
            FROM    Productos AS P
                    LEFT JOIN Productos_Intervalos AS P_Inv
                           ON P_Inv.id_productos = P.id_productos
                    LEFT JOIN Productos_Gran_Formato AS P_gran
                           ON P.id_productos = P_gran.id_productos
                    LEFT JOIN Costo_Produccion AS C_Prod
                           ON P.id_productos = C_Prod.id_productos
            ORDER   BY P.id_productos, desde ASC;
        ''')
    
    def obtenerProducto(self, id_productos: int):
        """ Obtener todas las columnas de un producto. """
        return self.fetchone('''
            SELECT  * 
            FROM    Productos 
            WHERE   id_productos = ?;
        ''', (id_productos,))
    
    def obtenerListaCodigos(self):
        """ Obtener lista con códigos de todos los productos. """
        return self.fetchall('SELECT codigo FROM Productos;')
    
    def obtenerIdProducto(self, codigo: str):
        """ Obtener id_producto dado código de un producto. """
        result = self.fetchone('''
            SELECT  id_productos
            FROM    Productos 
            WHERE   codigo = ?;
        ''', (codigo,))
        
        if result:
            id, = result
            return id
        
        return None
    
    def obtenerRelacionVentas(self, id_productos: int):
        """ Obtener relación con ventas en la tabla ventas_detallado. """
        return self.fetchall('''
            SELECT	id_productos
            FROM	Ventas_Detallado
            WHERE	id_productos = ?;
        ''', (id_productos,))
    
    def obtenerTablaPrecios(self, id_productos: int):
        """ Obtener tabla de precios, asumiendo producto simple. """
        return self.fetchall('''
            SELECT	desde,
                    precio_con_iva,
                    duplex
            FROM	Productos_Intervalos AS P_Inv
            WHERE 	id_productos = ?
            ORDER   BY desde ASC, duplex ASC;
        ''', (id_productos,))
    
    def obtenerPrecioSimple(self, id_productos: int, cantidad: int, duplex: bool):
        """ Obtener precio de producto categoría simple. """
        restrict = 'AND duplex' if duplex else ''
        
        result = self.fetchone(f'''
            SELECT * FROM (
                SELECT  FIRST 1 precio_con_iva
                FROM    Productos_Intervalos
                WHERE   id_productos = ?
                        AND desde <= ?
                        {restrict}
                ORDER   BY desde DESC)
            UNION ALL
            SELECT * FROM (
                SELECT  FIRST 1 precio_con_iva
                FROM    Productos_Intervalos
                WHERE   id_productos = ?
                        AND desde <= ?
                ORDER   BY desde DESC)
        ''', (id_productos, cantidad) * 2)
        
        try:
            precio, = result
            return precio
        except TypeError:
            return None
    
    def obtenerPrecioGranFormato(self, id_productos: int, ancho: float, alto: float):
        """ Obtener precio de producto gran formato.

            Verifica si las medidas caen dentro del mínimo. Si no, regresa precio normal. """
        result = self.obtenerGranFormato(id_productos)
        if not result:
            return None
        
        min_m2, precio_m2 = result
        cantidad = ancho * alto
        
        return cantidad * precio_m2 if cantidad >= min_m2 else precio_m2
    
    def obtenerGranFormato(self, id_productos: int):
        """ Obtener mínimo de metros cuadrados y precio de metro cuadrado
            de producto categoría gran formato. """
        return self.fetchone('''
            SELECT  min_m2,
                    precio_m2
            FROM    Productos_Gran_Formato
            WHERE 	id_productos = ?;
        ''', (id_productos,))
    
    def obtenerUtilizaInventario(self, id_productos: int):
        """ Obtener relación del producto con elementos del inventario. """
        return self.fetchall('''
            SELECT	nombre,
                    utiliza_inventario
            FROM	Productos_Utiliza_Inventario AS PUI
                    LEFT JOIN Inventario AS I
                            ON PUI.id_inventario = I.id_inventario
            WHERE 	id_productos = ?;
        ''', (id_productos,))
    
    def insertarProducto(self, params: tuple):
        """ Intenta insertar un producto y regresar tupla
            con el índice recién insertado. No hace commit. """
        return self.fetchone('''
            INSERT INTO Productos (
                codigo, descripcion, abreviado, categoria
            )
            VALUES
                (?,?,?,?)
            RETURNING
                id_productos;
        ''', params)
    
    def editarProducto(self, id_productos: int, params: tuple):
        """ Intenta editar un productos y regresar tupla
            con el índice recién modificado. No hace commit. """
        return self.fetchone('''
            UPDATE  Productos
            SET     codigo = ?,
                    descripcion = ?,
                    abreviado = ?,
                    categoria = ?
            WHERE   id_productos = ?
            RETURNING id_productos;
        ''', (*params, id_productos))
    
    def eliminarProducto(self, id_productos: int):
        """ Elimina el producto y sus relaciones con las tablas productos_intervalos,
            productos_gran_formato, productos_utiliza_inventario y productos.
            Hace commit automáticamente. """
        param = (id_productos,)
        query = lambda tabla: f'DELETE FROM {tabla} WHERE id_productos = ?;'
        
        # primero borrar en tres tablas, antes de hacer commit
        if all(self.execute(query(tabla), param) for tabla in [
            'Productos_Utiliza_Inventario',
            'Productos_Gran_Formato',
            'Productos_Intervalos']):
            return self.execute(query('Productos'), param, commit=True)
        else:
            return False
    
    def eliminarProdUtilizaInv(self, id_productos: int):
        """ Elimina producto de la tabla productos_utiliza_inventario.
            No hace commit, al ser parte inicial del proceso de registro/modificación. """
        return self.execute('''
            DELETE  FROM productos_utiliza_inventario
            WHERE   id_productos = ?;
        ''', (id_productos,), commit=False)
    
    def insertarProdUtilizaInv(self, id_productos: int, params: list[tuple]):
        """ Inserta producto en la tabla productos_utiliza_inventario.
            No hace commit, al ser parte del proceso de registro/modificación. """
        params = [(id_productos,) + param for param in params]
        
        return self.executemany('''
            INSERT INTO productos_utiliza_inventario (
                id_productos, id_inventario, utiliza_inventario
            )
            VALUES
                (?,?,?);
        ''', params, commit=False)
    
    def eliminarPrecios(self, id_productos: int):
        """ Eliminar todos los precios del producto, en las tablas 
            productos_intervalos y productos_gran_formato. 
            No hace commit, al ser parte del proceso de registro/modificación. """
        param = (id_productos,)
        query = lambda tabla: f'DELETE FROM {tabla} WHERE id_productos = ?;'
        
        return all(self.execute(query(tabla), param) for tabla in [
            'Productos_Intervalos',
            'Productos_Gran_Formato'])
    
    def insertarProductosIntervalos(self, id_productos: int, params: list[tuple]):
        """ Inserta precios para el producto en la tabla productos_intervalos.
            Hace commit, al ser parte final del proceso de registro/modificación."""
        params = [(id_productos,) + param for param in params]
        
        return self.executemany('''
            INSERT INTO Productos_Intervalos (
                id_productos, desde, precio_con_iva, duplex
            )
            VALUES
                (?,?,?,?);
        ''', params, commit=True)
    
    def insertarProductoGranFormato(self, id_productos: int, params: tuple):
        """ Inserta precios para el producto en la tabla productos_gran_formato.
            Hace commit, al ser parte final del proceso de registro/modificación."""
        return self.execute('''
            INSERT INTO Productos_Gran_Formato (
                id_productos, min_m2, precio_m2
            )
            VALUES
                (?,?,?);
        ''', (id_productos,) + params, commit=True)


class ManejadorVentas(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Ventas. """
    
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        super().__init__(conn, error_txt)
    
    def tablaVentas(self, inicio: QDate = QDate.currentDate(),
                    final: QDate = QDate.currentDate(),
                    restrict: int = None):
        """ Sentencia para alimentar la tabla principal de ventas directas. 
        
            Requiere fechas de inicio y final, tipo QDate.
            
            Restringir a un solo usuario, si se desea. """
        restrict = f'AND Usuarios.id_usuarios = {restrict}' if restrict else ''
        
        return self.fetchall(f'''
            SELECT  Ventas.id_ventas,
                    Usuarios.nombre,
                    Clientes.nombre,
                    fecha_hora_creacion,
                    SUM(importe) AS total,
                    estado,
                    metodo_pago,
                    comentarios
            FROM    Ventas
                    LEFT JOIN Usuarios
                           ON Ventas.id_usuarios = Usuarios.id_usuarios
                    LEFT JOIN Clientes
                           ON Ventas.id_clientes = Clientes.id_clientes
                    LEFT JOIN Ventas_Detallado
                           ON Ventas.id_ventas = Ventas_Detallado.id_ventas
			WHERE   fecha_hora_creacion = fecha_hora_entrega
                    AND ? <= CAST(fecha_hora_creacion AS DATE)
                    AND CAST(fecha_hora_creacion AS DATE) <= ?
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 6, 7, 8
            ORDER	BY Ventas.id_ventas DESC;
        ''', (inicio.toPython(), final.toPython()))
    
    def tablaPedidos(self, inicio: QDate = QDate.currentDate(),
                     final: QDate = QDate.currentDate(),
                     restrict: int = None):
        """ Sentencia para alimentar la tabla principal de pedidos. 
        
            Requiere fechas de inicio y final, tipo QDate.
            
            Restringir a un solo usuario, si se desea. """
        restrict = f'AND Usuarios.id_usuarios = {restrict}' if restrict else ''
        
        return self.fetchall(f'''
            SELECT  Ventas.id_ventas,
                    Usuarios.nombre,
                    Clientes.nombre,
                    fecha_hora_creacion,
                    fecha_hora_entrega,
                    SUM(importe) AS total,
                    estado,
                    metodo_pago,
                    comentarios
            FROM    Ventas
                    LEFT JOIN Usuarios
                           ON Ventas.id_usuarios = Usuarios.id_usuarios
                    LEFT JOIN Clientes
                           ON Ventas.id_clientes = Clientes.id_clientes
                    LEFT JOIN Ventas_Detallado
                           ON Ventas.id_ventas = Ventas_Detallado.id_ventas
			WHERE   fecha_hora_creacion != fecha_hora_entrega
                    AND (? <= CAST(fecha_hora_creacion AS DATE)
                         AND CAST(fecha_hora_creacion AS DATE) <= ?
                         OR estado LIKE 'Recibido%')
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 5, 7, 8, 9
            ORDER	BY Ventas.id_ventas DESC;
        ''', (inicio.toPython(), final.toPython()))
    
    def obtenerVenta(self, id_venta):
        """ Sentencia para obtener una venta. """
        return self.fetchone('''
            SELECT  * 
            FROM    Ventas 
            WHERE   id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerNumPendientes(self, id_usuario: int):
        """ Obtener número de pedidos pendientes del usuario. """
        return self.fetchone('''
            SELECT	COUNT(*)
            FROM	Ventas
            WHERE	fecha_hora_creacion != fecha_hora_entrega
                    AND estado LIKE 'Recibido%'
                    AND id_usuarios = ?;
        ''', (id_usuario,))
    
    def obtenerDatosGeneralesVenta(self, id_venta: int):
        """ Obtiene otros datos generales de una venta:
            nombre de cliente, correo, teléfono, fecha y hora de creación,
            fecha y hora de entrega, comentarios generales, nombre de vendedor. """
        return self.fetchone('''
            SELECT  Clientes.nombre,
                    correo,
                    telefono,
                    fecha_hora_creacion,
                    fecha_hora_entrega,
                    comentarios,
                    Usuarios.nombre
            FROM    Ventas
                    LEFT JOIN Clientes
                           ON Ventas.id_clientes = Clientes.id_clientes
                    LEFT JOIN Usuarios
                           ON Ventas.id_usuarios = Usuarios.id_usuarios
            WHERE   id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerTablaOrdenCompra(self, id_venta: int):
        """ Obtiene tabla de productos para las órdenes de compra:
        
            Cantidad | Producto | Especificaciones | Precio | Importe """
        return self.fetchall('''
            SELECT  cantidad,
                    abreviado || IIF(duplex, ' (a doble cara)', ''),
                    especificaciones,
                    precio,
                    importe
            FROM    Ventas_Detallado AS VD
                    LEFT JOIN Productos AS P
                           ON VD.id_productos = P.id_productos
            WHERE   id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerTablaTicket(self, id_venta: int):
        """ Obtiene tabla de productos para los tickets de ventas directas.
        
            Cantidad | Producto | Precio | Descuento | Importe """
        return self.fetchall('''
            SELECT	cantidad,
                    abreviado || IIF(VD.duplex, ' (a doble cara)', ''),
                    precio,
                    descuento,
                    importe
            FROM	Ventas_Detallado AS VD
                    LEFT JOIN Productos AS P
                        ON VD.id_productos = P.id_productos
            WHERE	id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerTablaProductosVenta(self, id_venta: int):
        """ Obtener tabla de productos para widgets de
            detalles de venta, terminar compra, etc. 
            
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        return self.fetchall('''
            SELECT  cantidad,
                    codigo || IIF(duplex, ' (a doble cara)', ''),
                    especificaciones,
                    precio,
                    descuento,
                    importe
            FROM    Ventas_Detallado
                    LEFT JOIN Productos
                           ON Ventas_Detallado.id_productos = Productos.id_productos
            WHERE   id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerClienteAsociado(self, id_venta: int):
        """ Obtener nombre y teléfono de cliente asociado a la venta. """
        return self.fetchone('''
            SELECT  C.nombre,
                    C.telefono
            FROM    Ventas AS V
                    LEFT JOIN Clientes AS C
                           ON V.id_clientes = C.id_clientes
            WHERE   id_ventas = ?;
        ''', (id_venta,))
    
    def obtenerUsuarioAsociado(self, id_venta: int):
        """ Obtener nombre de vendedor asociado a la venta. """
        result = self.fetchone('''
            SELECT	U.nombre
            FROM	Ventas AS V
                    LEFT JOIN Usuarios AS U
                           ON V.id_usuarios = U.id_usuarios
            WHERE	V.id_ventas = ?;
        ''', (id_venta,))
        
        if result:
            nombre, = result
            return nombre
        
        return None
    
    def obtenerImporteTotal(self, id_venta: int):
        """ Obtiene el importe total de una venta. """
        t = self.fetchone('''
            SELECT  SUM(importe)
            FROM    Ventas_Detallado
            WHERE   id_ventas = ?;
        ''', (id_venta,))
        
        try:
            importe, = t
            return round(importe, 2)
        except ValueError:
            return None
    
    def obtenerAnticipo(self, id_venta: int):
        """ Obtiene el anticipo recibido de una orden pendiente.
            Si no es una orden pendiente, regresa None. """
        t: str = self.fetchone('''
            SELECT  estado
            FROM    Ventas
            WHERE   id_ventas = ?;
        ''', (id_venta,))
        
        try:
            estado, = t
            return float(estado.split()[1])
        except (ValueError, IndexError):
            return None
    
    def obtenerFechaPrimeraVenta(self, id_usuario: int = None):
        """ Obtener fecha de la venta más antigüa. 
            Se puede restringir a cierto usuario. """
        restrict = f'WHERE id_usuarios = {id_usuario}' if id_usuario else ''
        
        result = self.fetchone(f'''
            SELECT  MIN(fecha_hora_creacion) 
            FROM    Ventas
            {restrict};
        ''')
        if result:
            fecha, = result
            return fecha
    
    def insertarVenta(self, params: tuple):
        """ Insertar venta nueva en la tabla ventas e intenta 
            regresar tupla con índice de venta recién insertada.
            
            No hace commit. """
        return self.fetchone('''
            INSERT INTO Ventas (
                id_clientes, id_usuarios, fecha_hora_creacion, 
                fecha_hora_entrega, comentarios,
                requiere_factura, estado
            ) 
            VALUES 
                (?,?,?,?,?,?,?)
            RETURNING
                id_ventas;
        ''', params)
    
    def insertarDetallesVenta(self, id_ventas: int, params: list[tuple]):
        """ Insertar detalles de venta en tabla ventas_detallado e intenta 
            regresar tupla con índice de venta recién insertada.
            
            Hace commit automáticamente. """
        params = [(id_ventas,) + param for param in params]
        
        return self.executemany('''
            INSERT INTO Ventas_Detallado (
                id_ventas, id_productos, cantidad, precio, 
                descuento, especificaciones, duplex, importe
            ) 
            VALUES 
                (?,?,?,?,?,?,?,?);
        ''', params, commit=True)
    
    def actualizarEstadoVenta(self, id_ventas: int, estado: str, commit: bool = False):
        """ Actualiza estado de venta a parámetro.
        
            No hace `commit`, a menos que se indique lo contrario. """
        return self.execute('''
            UPDATE  Ventas
            SET     estado = ?
            WHERE   id_ventas = ?;
        ''', (estado, id_ventas), commit=commit)
    
    def agregarComision(self, id_ventas: int, importe: float, commit: bool = False):
        """ Agregar producto de comisión por pago con tarjeta a venta.
        
            No hace `commit`, a menos que se indique lo contrario. """
        if importe <= 0.:
            return True
        
        manejador = ManejadorProductos(self.conn)
        id_producto = manejador.obtenerIdProducto('COMISION')
        
        params = (id_ventas, id_producto, importe,
                  1., 0., 'COMISIÓN POR PAGO CON TARJETA', False)
        
        return self.execute('''
            INSERT INTO Ventas_Detallado (
                id_ventas, id_productos, cantidad, precio, 
                descuento, especificaciones, duplex
            ) 
            VALUES 
                (?,?,?,?,?,?,?);
        ''', params, commit=commit)
    
    def actualizarMetodoPago(self, id_ventas: int, metodo: str, commit: bool = False):
        """ Actualiza método de pago de venta a parámetro.
        
            No hace `commit`, a menos que se indique lo contrario. """
        return self.execute('''
            UPDATE  Ventas
            SET     metodo_pago = ?
            WHERE   id_ventas = ?;
        ''', (metodo, id_ventas), commit=commit)
    
    def actualizarRecibido(self, id_ventas: int, pago: float, commit: bool = False):
        """ Actualizar pago recibido para esta venta, en tabla ventas. 
        
            No hace `commit`, a menos que se indique lo contrario."""
        return self.execute('''
            UPDATE  Ventas
            SET     recibido = ?
            WHERE   id_ventas = ?;
        ''', (pago, id_ventas), commit=commit)


class ManejadorUsuarios(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Usuarios. """
    
    def __init__(self, conn: fdb.Connection,
                 error_txt: str = None,
                 handle_exceptions: bool = True):
        super().__init__(conn, error_txt, handle_exceptions)
    
    def obtenerTablaPrincipal(self):
        """ Obtener tabla principal para el módulo de administrar usuarios. """
        return self.fetchall('''
            SELECT  usuario,
                    nombre,
                    permisos,
                    MAX(fecha_hora_creacion) AS ultimaVenta
            FROM    Usuarios AS U
                    LEFT JOIN Ventas AS V
                           ON U.id_usuarios = V.id_usuarios
            GROUP   BY 1, 2, 3
            ORDER   BY U.nombre ASC;
        ''')
    
    def obtenerUsuario(self, usuario: str):
        """ Obtener tupla de usuario dado el nombre de usuario. """
        return self.fetchone('''
            SELECT  *
            FROM    Usuarios
            WHERE   usuario = ?;
        ''', (usuario,))
    
    def crearUsuarioServidor(self, usuario: str, psswd: str, esAdmin: bool):
        """ Registrar usuario en servidor Firebird. Otorgar permisos
            de administrar usuarios, si se desea.
            
            No hace commit. """
        admin_role = 'GRANT ADMIN ROLE' if esAdmin else ''
        
        return self.execute(f"CREATE USER {usuario} PASSWORD '{psswd}' {admin_role};")
    
    def insertarUsuario(self, params: tuple):
        """ Insertar nuevo usuario en tabla de Usuarios. No hace commit. """
        return self.execute('''
            INSERT INTO Usuarios (
                usuario, nombre, permisos
            )
            VALUES
                (?,?,?);
        ''', params)
    
    def actualizarUsuario(self, usuario: str, params: tuple):
        """ Actualizar usuario, nombre y permisos de usuario dado. 
        
            No hace commit. """
        return self.execute('''
            UPDATE  Usuarios
            SET     usuario = ?,
                    nombre = ?,
                    permisos = ?
            WHERE   usuario = ?;
        ''', (*params, usuario))
    
    def eliminarUsuario(self, usuario: str):
        """ Dar de baja usuario del sistema. Se eliminan los permisos
            y se elimina del servidor Firebird. 
            
            Hace commit automáticamente. """
        if not self.execute('''
            UPDATE  Usuarios
            SET     permisos = NULL
            WHERE   usuario = ?;
        ''', (usuario,), commit=False):
            return False
        
        return self.execute(f'DROP USER {usuario};', commit=True)
    
    def otorgarRolVendedor(self, usuario: str):
        """ Otorgar rol de vendedor en servidor Firebird.
        
            Hace commit automáticamente, al ser última operación 
            del proceso de creación/modificación. """
        return self.execute(f'GRANT VENDEDOR TO {usuario};', commit=True)
    
    def otorgarRolAdministrador(self, usuario: str):
        """ Otorgar rol de vendedor y administrador en servidor Firebird, con
            permisos para otorgar y remover roles de otros usuarios.
        
            Hace commit automáticamente, al ser última operación 
            del proceso de creación/modificación. """
        return self.execute(f'GRANT ADMINISTRADOR, VENDEDOR TO {usuario} WITH ADMIN OPTION;',
                            commit=True)
    
    def retirarRoles(self, usuario: str):
        """ Retirar roles VENDEDOR, ADMINISTRADOR del usuario. 
        
            No hace commit. """
        return self.execute(f'REVOKE ADMINISTRADOR, VENDEDOR FROM {usuario};')
    
    def cambiarPsswd(self, usuario: str, psswd: str):
        """ Cambiar contraseña del usuario. No hace commit. """
        return self.execute(f"ALTER USER {usuario} PASSWORD '{psswd}';")
