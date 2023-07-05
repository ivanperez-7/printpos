""" Módulo con manejadores para tablas en la base de datos. """
import fdb

from mywidgets import WarningDialog


class DatabaseManager:
    """ Clase general de un administrador de bases de datos.
    Permite ejecutar consultas varias y manejar las excepciones."""
    def __init__(self, conn: fdb.Connection, error_txt: str = None):
        self.conn = conn
        self.crsr: fdb.Cursor = conn.cursor()
        self.error_txt = error_txt or '¡Acceso fallido a base de datos!'

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
            WarningDialog(self.error_txt, str(err))
            return None


class ManejadorCaja(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Caja. """
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
        super().__init__(conn, error_txt)
    
    def obtenerMovimientos(self):
        """ Obtener historial completo de movimientos de caja. """
        return self.fetchall('''
            SELECT 	fecha_hora,
                    monto,
                    descripcion,
                    metodo,
                    U.nombre
            FROM 	Caja AS C
                    LEFT JOIN Usuarios AS U
                           ON C.id_usuarios = U.id_usuarios
            ORDER   BY fecha_hora DESC;
        ''')
    
    def registrarMovimiento(self, params: tuple):
        """ Registra ingreso o egreso en tabla historial de movimientos. 
            Hace commit automáticamente. """
        return self.execute('''
            INSERT INTO Caja (
                fecha_hora, monto,
                descripcion, metodo, id_usuarios
            )
            VALUES
                (?,?,?,?,?);
        ''', params, commit=True)


class ManejadorClientes(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Clientes. """
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
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
    
    def obtenerCliente(self, idx):
        """ Sentencia para obtener un cliente. """
        return self.fetchone('''
            SELECT  * 
            FROM    Clientes 
            WHERE id_clientes = ?;
        ''', (idx,))
    
    def registrarCliente(self, datosCliente: tuple):
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
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
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
        """ Regresa información principal de un elemento. """
        return self.fetchone('''
            SELECT  nombre,
                    tamano_lote, 
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes
            FROM    Inventario 
            WHERE   id_inventario = ?;
        ''', (id_inventario,))
    
    def obtenerIdInventario(self, nombre: str):
        """ Obtener id_inventario dado nombre de un elemento de inventario. """
        return self.fetchone('''
            SELECT  id_inventario
            FROM    Inventario 
            WHERE   nombre = ?;
        ''', (nombre,))
    
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
    
    def registrarElemento(self, datos_elemento: tuple):
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
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
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
    
    def obtenerIdProducto(self, codigo: str):
        """ Obtener id_producto dado código de un producto. """
        return self.fetchone('''
            SELECT  id_productos
            FROM    Productos 
            WHERE   codigo = ?;
        ''', (codigo,))
        
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
    
    def obtenerGranFormato(self, id_productos: int):
        """ Obtener datos de un producto categoría gran formato. """
        return self.fetchone('''
            SELECT  min_ancho,
                    min_alto,
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
                id_productos, min_ancho, min_alto, precio_m2
            )
            VALUES
                (?,?,?,?);
        ''', (id_productos,) + params, commit=True)


class ManejadorVentas(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Ventas. """
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
        super().__init__(conn, error_txt)
    
    def tablaVentas(self, restrict: int = None):
        """ Sentencia para alimentar la tabla principal de ventas directas. 
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
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 6, 7, 8
            ORDER	BY Ventas.id_ventas DESC;
        ''')
    
    def tablaPedidos(self, restrict: int = None):
        """ Sentencia para alimentar la tabla principal de pedidos. 
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
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 5, 7, 8, 9
            ORDER	BY Ventas.id_ventas DESC;
        ''')
    
    def obtenerVenta(self, idx):
        """ Sentencia para obtener una venta. """
        return self.fetchone('''
            SELECT  * 
            FROM    Ventas 
            WHERE   id_ventas = ?;
        ''', (idx,))
    
    def insertarVenta(self, params: tuple):
        """ Insertar venta nueva en la tabla ventas e intenta 
            regresar tupla con índice de venta recién insertada.
            
            No hace commit. """
        return self.fetchone('''
            INSERT INTO Ventas (
                id_clientes, id_usuarios, fecha_hora_creacion, 
                fecha_hora_entrega, comentarios, metodo_pago, 
                requiere_factura, estado
            ) 
            VALUES 
                (?,?,?,?,?,?,?,?)
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
                descuento, especificaciones, duplex
            ) 
            VALUES 
                (?,?,?,?,?,?,?);
        ''', params, commit=True)
