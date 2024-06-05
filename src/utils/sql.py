""" Módulo con manejadores para tablas en la base de datos. """
from datetime import datetime
from functools import partial, partialmethod
from typing import overload

import fdb
from PySide6.QtCore import QDate

from config import INI
from utils import Moneda


Connection = fdb.Connection
Cursor = fdb.Cursor
Error = fdb.Error


def conectar_db(usuario: str, psswd: str, rol: str = None) -> Connection:
    """ Crea conexión a base de datos y regresa objeto Connection.
        Regresa `None` al ocurrir un error. """
    try:
        return fdb.connect(
            dsn='{}/3050:PrintPOS.fdb'.format(INI.NOMBRE_SERVIDOR),
            user=usuario,
            password=psswd,
            charset='UTF8',
            role=rol)
    except Error as err:
        txt, sqlcode, gdscode = err.args
        print('\n{}'.format(sqlcode), gdscode, '\n'+txt)
        return None


def _WarningDialog(*args):
    from utils.mywidgets import WarningDialog
    return WarningDialog(*args)


class DatabaseManager:
    """ Clase general de un administrador de bases de datos.
        Permite ejecutar consultas varias y manejar las excepciones.
    
        Todas las operaciones realizadas en esta clase y en clases derivadas
        pueden regresar `False` o `None` al ocurrir un error, por lo que siempre se 
        debe verificar el resultado obtenido para asegurar una correcta funcionalidad. """
    
    def __init__(self, conn: Connection,
                       error_txt: str = None,
                       *, handle_exceptions: bool = True):
        if not isinstance(conn, Connection):
            raise Error("Conexión a DB no válida.")
        
        self._conn = conn
        self._error_txt = error_txt or '¡Acceso fallido a base de datos!'
        self._handle_exceptions = handle_exceptions
        
        crsr: Cursor = conn.cursor()
        
        self.execute = partial(self._partial_execute, crsr.execute)
        self.executemany = partial(self._partial_execute, crsr.executemany)
        self.fetchall: partial[list] = partial(self._partial_fetch, crsr.fetchall)
        self.fetchone: partial[tuple] = partial(self._partial_fetch, crsr.fetchone)
    
    def _partial_execute(self, func, query: str, parameters=None, commit=False):
        try:
            if parameters is None:
                func(query)
            else:
                func(query, parameters)
            if commit:
                self._conn.commit()
            return True
        except Error as err:
            if not self._handle_exceptions:
                raise err
            self._conn.rollback()
            _WarningDialog(self._error_txt, err.args[0])
            return False
    
    def _partial_fetch(self, func, query: str, parameters=None):
        try:
            if parameters is None:
                self.execute(query)
            else:
                self.execute(query, parameters)
            return func()
        except Error as err:
            if not self._handle_exceptions:
                raise err
            self._conn.rollback()
            _WarningDialog(self._error_txt, err.args[0])
            return None
    
    def commit(self):
        try:
            self._conn.commit()
            return True
        except Error as err:
            if not self._handle_exceptions:
                raise err
            self._conn.rollback()
            _WarningDialog(self._error_txt, err.args[0])
            return False
    
    def obtenerVista(self, vista: str):
        """ Atajo de sentencia SELECT para obtener una vista. """
        return self.fetchall(f'SELECT * FROM {vista};')
    
    @property
    def usuarioActivo(self) -> str:
        """ Obtiene nombre del usuario de la conexión activa. """
        result = self.fetchone('''
            SELECT  nombre
            FROM    usuarios
            WHERE   usuario = ?;
        ''', (self.identificadorUsuarioActivo,))
        if result:
            return result[0]
    
    @property
    def identificadorUsuarioActivo(self) -> str:
        """ Obtiene identificador de usuario de la conexión activa. """
        result = self.fetchone('SELECT USER FROM RDB$DATABASE;')
        if result:
            return result[0]
    
    @property
    def rolActivo(self) -> str:
        """ Obtiene rol de la conexión activa. """
        result = self.fetchone('SELECT CURRENT_ROLE FROM RDB$DATABASE;')
        if result:
            return result[0]


class ManejadorCaja(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Caja. """
    
    def obtenerMovimientos(self, inicio: QDate, final: QDate):
        """ Obtener historial completo de movimientos de caja.
            
            Requiere fechas de inicio y final, de tipo QDate. """
        return self.fetchall('''
            SELECT  fecha_hora,
                    monto, 
                    REPLACE(descripcion, '  ', ''), 
                    metodo, 
                    nombre
            FROM    movimientos_caja
            WHERE   CAST(fecha_hora AS DATE) BETWEEN ? AND ?;
        ''', (inicio.toPython(), final.toPython()))
    
    def obtenerFechaPrimerMov(self):
        """ Obtener fecha del movimiento más antiguo. """
        result = self.fetchone('SELECT MIN(fecha_hora) FROM movimientos_caja;')
        if result:
            return result[0]
    
    def insertarMovimiento(self, params: tuple, commit: bool = True):
        """ Registra ingreso o egreso en tabla historial de movimientos.
        
            Hace commit automáticamente, a menos que se indique lo contrario. """
        return self.execute('''
            INSERT INTO Caja (
                fecha_hora, monto, descripcion,
                id_metodo_pago, id_usuarios
            )
            VALUES
                (?,?,?,?,?);
        ''', params, commit=commit)


class ManejadorClientes(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Clientes. """
    
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
    
    @overload
    def obtenerCliente(self, id_cliente) -> tuple: ...
    @overload
    def obtenerCliente(self, nombre: str, telefono: str) -> tuple: ...
    
    def obtenerCliente(self, *args):
        """ Obtener todos los datos de un cliente. """
        if len(args) == 2 and all(isinstance(arg, str) for arg in args):
            query = ''' SELECT  * 
                        FROM    Clientes 
                        WHERE   nombre = ? 
                                AND telefono = ?; '''
        elif len(args) == 1:
            query = ''' SELECT  * 
                        FROM    Clientes 
                        WHERE   id_clientes = ?; '''
        else:
            raise ValueError('Argumentos inválidos: ninguna implementación.')
        return self.fetchone(query, args)
    
    @overload
    def obtenerDescuentosCliente(self, id_cliente: int) -> tuple: ...
    @overload
    def obtenerDescuentosCliente(self, nombre: str, telefono: str) -> tuple: ...
    
    def obtenerDescuentosCliente(self, *args, **kwargs):
        """ Obtener booleano de cliente especial y cadena de descuentos. """
        if len(args) == 2 and all(isinstance(arg, str) for arg in args):
            query = ''' SELECT  cliente_especial,
                                descuentos
                        FROM    Clientes
                        WHERE   nombre = ?
                                AND telefono = ?; '''
        elif len(args) == 1 and isinstance(args[0], int):
            query = ''' SELECT  cliente_especial,
                                descuentos
                        FROM    Clientes
                        WHERE   id_clientes = ?; '''
        else:
            raise ValueError('Argumentos inválidos: ninguna implementación.')
        return self.fetchone(query, args)
    
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


class ManejadorMetodosPago(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla metodos_pago. """
    
    def obtenerIdMetodo(self, metodo: str):
        """ Obtener ID del método de pago dado su nombre. """
        result = self.fetchone(''' SELECT  id_metodo_pago 
                                   FROM    metodos_pago 
                                   WHERE   metodo = ?; ''', (metodo,))
        if result:
            return result[0]


class ManejadorProductos(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Inventario. """
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar tabla principal de productos. """
        return self.fetchall('''
            WITH costo_produccion AS (
                SELECT
                    P.id_productos,
                    COALESCE(SUM(PUI.utiliza_inventario * I.precio_unidad), 0.0) AS costo
                FROM
                    Productos AS P
                    LEFT JOIN productos_utiliza_inventario AS PUI
                        ON P.id_productos = PUI.id_productos
                    LEFT JOIN inventario AS I
                        ON PUI.id_inventario = I.id_inventario
                GROUP BY
                    1
                ORDER BY
                    1 ASC
            )

            SELECT
                P.id_productos,
                P.codigo,
                P.descripcion 
                    || IIF(desde > 1, ', desde ' || ROUND(desde, 1) || ' unidades ', '')
                    || IIF(P_Inv.duplex, '[PRECIO DUPLEX]', '')                 AS descripcion,
                P.abreviado,
                COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva)                AS precio_con_iva, 
                COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) / 1.16         AS precio_sin_iva,
                C_Prod.costo,
                COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) - C_Prod.costo AS utilidad
            FROM
                productos AS P
                LEFT JOIN productos_intervalos AS P_Inv
                    ON P_Inv.id_productos = P.id_productos
                LEFT JOIN productos_gran_formato AS P_gran
                    ON P.id_productos = P_gran.id_productos
                JOIN costo_produccion AS C_Prod
                    ON P.id_productos = C_Prod.id_productos
            ORDER BY
                1, desde ASC;
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
            return result[0]
    
    def obtenerNombreParaTicket(self, codigo: str):
        """ Obtener nombre para mostrar en ticket dado código de un producto. """
        result = self.fetchone('''
            SELECT  abreviado
            FROM    Productos 
            WHERE   codigo = ?;
        ''', (codigo,))
        if result:
            return result[0]
    
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
            return result[0]
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


class ManejadorReportes(DatabaseManager):
    """ Clase con diversas consultas específicas para el módulo de reportes. """
    restr_ventas_terminadas = '''
        V.estado NOT LIKE 'Cancelada%'
        AND V.estado != 'No terminada'
    '''
    
    def obtenerIngresosBrutos(self):
        """ Obtiene ingresos brutos de ventas concretadas o pendientes.
            Devuelve: cantidad total, número de ventas. """
        return self.fetchone(f'''
            SELECT
                SUM(monto),
                COUNT(DISTINCT V.id_ventas)
            FROM
                ventas V
                JOIN ventas_pagos VP
                    ON VP.id_ventas = V.id_ventas
            WHERE
                {self.restr_ventas_terminadas};
        ''')
    
    def obtenerTopVendedor(self, count: int = 1):
        """ Consultar los primeros `count` vendedores con más ventas.
            Devuelve: nombre, suma de ingresos brutos. """
        return self.fetchone(f'''
            SELECT
                FIRST {count}
                U.NOMBRE,
                SUM(monto) AS ingreso_bruto
            FROM
                Ventas V
                JOIN ventas_pagos VP
                    ON VP.id_ventas = V.id_ventas
                JOIN Usuarios U
                    ON V.id_usuarios = U.ID_USUARIOS
            WHERE
                {self.restr_ventas_terminadas}
            GROUP BY
                U.nombre
            ORDER BY
                2 DESC;
        ''')
    
    def obtenerTopProducto(self, count: int = 1):
        """ Consultar los primeros `count` productos más vendidos.
            Devuelve: abreviado, código, número de unidades vendidas. """
        result = self.fetchall(f'''
            SELECT
                FIRST {count}
                P.abreviado,
                P.codigo,
                SUM(cantidad)
            FROM
                ventas_detallado VD
                JOIN ventas V
                    ON VD.id_ventas = V.id_ventas
                JOIN Productos P
                    ON VD.id_productos = P.id_productos
            WHERE
                {self.restr_ventas_terminadas}
            GROUP BY
                1, 2
            ORDER BY
                3 DESC;
        ''')
        if count <= 1:
            return result[0]
        return result
    
    def obtenerGraficaMetodos(self):
        return self.fetchall(f'''
            SELECT
                MP.metodo,
                COUNT(*) num_pagos
            FROM
                ventas_pagos VP
                JOIN ventas V
                    ON VP.id_ventas = V.id_ventas
                JOIN metodos_pago MP
                    ON VP.id_metodo_pago = MP.id_metodo_pago
            WHERE
                {self.restr_ventas_terminadas}
            GROUP BY
                1;
        ''')
    
    def obtenerGraficaVentas(self, year):
        """ Regresa lista de tuplas para la gráfica de barras de ventas:
            [(mes/año, suma, número de ventas)]. """
        return self.fetchall(f'''
            SELECT
                EXTRACT(YEAR FROM fecha_hora_creacion)
                    || '-'
                    || LPAD(EXTRACT(MONTH FROM fecha_hora_creacion), 2, '0') AS formatted_date,
                SUM(VP.monto)                                                AS total_sales,
                COUNT(DISTINCT V.id_ventas)                                  AS num_ventas
            FROM
                ventas_pagos VP
                JOIN ventas V
                    ON VP.id_ventas = V.id_ventas
            WHERE
                {self.restr_ventas_terminadas}
                AND EXTRACT(YEAR FROM fecha_hora_creacion) = ?
            GROUP BY
                EXTRACT(YEAR FROM fecha_hora_creacion),
                EXTRACT(MONTH FROM fecha_hora_creacion)
            ORDER BY
                1;
        ''', (year,))
        
    def obtenerReporteVendedores(self, fechaDesde: QDate, fechaHasta: QDate):
        return self.fetchall(f'''
            WITH ventas_canceladas AS (
                SELECT
                    U.id_usuarios,
                    COUNT(
                        DISTINCT CASE 
                            WHEN V.estado LIKE 'Cancelada%' OR V.estado = 'No terminada'
                                THEN V.id_ventas 
                        END) AS num_canceladas
                FROM
                    usuarios U
                    LEFT JOIN ventas V
                        ON V.id_usuarios = U.id_usuarios
                WHERE
                    CAST(V.fecha_hora_creacion AS DATE) BETWEEN ? AND ?
                GROUP BY
                    1
            )

            SELECT
                U.nombre,
                COUNT(DISTINCT V.id_ventas) || ' ventas'    AS ventas_concretadas,
                COALESCE(VC.num_canceladas, 0) || ' ventas' AS ventas_canceladas,
                SUM(monto)                                  AS ventas_brutas,
                SUM(monto) / COUNT(DISTINCT V.id_ventas)    AS ventas_promedio
            FROM
                usuarios U
                LEFT JOIN ventas V
                    ON V.id_usuarios = U.id_usuarios
                LEFT JOIN ventas_pagos VP
                    ON VP.id_ventas = V.id_ventas
                JOIN ventas_canceladas VC
                    ON VC.id_usuarios = U.id_usuarios
            WHERE
                {self.restr_ventas_terminadas}
                AND CAST(V.fecha_hora_creacion AS DATE) BETWEEN ? AND ?
            GROUP BY
                1, 3
            ORDER BY
                4 DESC;
    ''', (fechaDesde.toPython(), fechaHasta.toPython())*2)
    
    def obtenerGraficaVentasVendedor(self, vendedor: str, year: int):
        return self.fetchall(f'''
            SELECT
                EXTRACT(YEAR FROM fecha_hora_creacion)
                    || '-'
                    || LPAD(EXTRACT(MONTH FROM fecha_hora_creacion), 2, '0') AS formatted_date,
                SUM(monto)                                                   AS total_sales
            FROM
                ventas_pagos VP
                LEFT JOIN ventas V
                    ON VP.id_ventas = V.id_ventas
                LEFT JOIN Usuarios U
                    ON V.id_usuarios = U.ID_USUARIOS
            WHERE
                {self.restr_ventas_terminadas}
                AND EXTRACT(YEAR FROM fecha_hora_creacion) = ?
                AND U.nombre = ?
            GROUP BY
                EXTRACT(YEAR FROM fecha_hora_creacion),
                EXTRACT(MONTH FROM fecha_hora_creacion)
            ORDER BY
                1;
        ''', (year, vendedor))
    
    def obtenerReporteClientes(self, fechaDesde: QDate, fechaHasta: QDate):
        restr = (self.restr_ventas_terminadas
            + "AND CAST(V.fecha_hora_creacion AS DATE) BETWEEN ? AND ?")
        
        return self.fetchall(f'''
            WITH prod_mas_comprados AS (
                SELECT
                    V.id_clientes,
                    P.abreviado || ' (' || P.codigo || ')' AS prod_mas_comprado,
                    ROW_NUMBER() OVER (
                        PARTITION BY
                            V.id_clientes
                        ORDER BY
                            COUNT(*) DESC
                    )                                      AS rn
                FROM
                    ventas V
                    JOIN ventas_detallado VD
                        ON V.id_ventas = VD.id_ventas
                    JOIN productos P
                        ON VD.ID_PRODUCTOS = P.ID_PRODUCTOS
                WHERE
                    {restr}
                GROUP BY
                    1, 2
            )
            
            SELECT
                nombre,
                MIN(V.fecha_hora_creacion)                AS primera_compra,
                MAX(V.fecha_hora_creacion)                AS ultima_compra,
                COUNT(DISTINCT V.id_ventas) || ' compras' AS num_concretadas,
                SUM(monto)                                AS compras_brutas,
                SUM(monto) / COUNT(DISTINCT V.id_ventas)  AS compra_promedio,
                PMC.prod_mas_comprado
            FROM
                clientes C
                LEFT JOIN ventas V
                    ON C.id_clientes = V.id_clientes
                LEFT JOIN ventas_pagos VP
                    ON V.id_ventas = VP.id_ventas
                JOIN prod_mas_comprados PMC
                    ON C.id_clientes = PMC.id_clientes
                       AND PMC.rn = 1
            WHERE
                {restr}
            GROUP BY
                1, 7
            ORDER BY
                5 DESC;
        ''', (fechaDesde.toPython(), fechaHasta.toPython())*2)
    
    def obtenerReporteProductos(self, fechaDesde: QDate, fechaHasta: QDate):
        return self.fetchall(f'''
            SELECT
                abreviado,
                codigo,
                MAX(V.fecha_hora_creacion)          AS ultima_compra,
                SUM(cantidad) || ' unidades'        AS num_vendidos,
                ROUND(AVG(cantidad)) || ' unidades' AS promedio_vendidos,
                SUM(importe)                        AS ingresos_brutos
            FROM
                productos P
                LEFT JOIN ventas_detallado VD
                    ON P.id_productos = VD.id_productos
                LEFT JOIN ventas V
                    ON VD.id_ventas = V.id_ventas
            WHERE
                {self.restr_ventas_terminadas}
                AND CAST(V.fecha_hora_creacion AS DATE) BETWEEN ? AND ?
            GROUP BY
                1, 2
            ORDER BY
                SUM(cantidad) DESC;
        ''', (fechaDesde.toPython(), fechaHasta.toPython())*2)
    
    def obtenerGraficaVentasProducto(self, codigo: str, year: int):
        return self.fetchall(f'''
            SELECT
                EXTRACT(YEAR FROM fecha_hora_creacion)
                    || '-'
                    || LPAD(EXTRACT(MONTH FROM fecha_hora_creacion), 2, '0') AS formatted_date,
                SUM(importe)                                                 AS total_sales
            FROM
                ventas_detallado VD
                LEFT JOIN ventas V
                    ON VD.id_ventas = V.id_ventas
                LEFT JOIN productos P
                    ON P.id_productos = VD.id_productos
            WHERE
                {self.restr_ventas_terminadas}
                AND EXTRACT(YEAR FROM fecha_hora_creacion) = ?
                AND P.codigo = ?
            GROUP BY
                EXTRACT(YEAR FROM fecha_hora_creacion),
                EXTRACT(MONTH FROM fecha_hora_creacion)
            ORDER BY
                1;
        ''', (year, codigo))
    
    def obtenerVentasIntervalos(self, codigo: str):
        return self.fetchall('''
            SELECT
                P_Inv.desde,
                CASE P_Inv.duplex
                    WHEN true THEN 'Sí'
                    ELSE 'No'
                END,
                SUM(VD.cantidad) AS unit_vendidas
            FROM
                ventas_detallado VD
                JOIN productos_intervalos P_Inv
                    ON VD.id_productos = P_Inv.id_productos
                       AND VD.duplex = P_Inv.duplex
                       AND VD.cantidad >= P_Inv.desde
                LEFT JOIN productos P
                    ON VD.id_productos = P.id_productos
            WHERE
                P.codigo = ?
            GROUP BY
                1, 2;
        ''', (codigo,))


class ManejadorVentas(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Ventas. """
    
    def _tablaParcial(self, fecha_entrega: bool,
                      inicio: QDate = QDate.currentDate(),
                      final: QDate = QDate.currentDate(),
                      restrict: int = None):
        restrict = f'AND U.id_usuarios = {restrict}' if restrict else ''
        col_fecha_entrega = 'fecha_hora_entrega,' if fecha_entrega else ''
        clausula_where = 'fecha_hora_entrega {} fecha_hora_creacion'.format(
            '!=' if fecha_entrega else '=')
        clausula_group = '1, 2, 3, 4, 5, 7, 8' if fecha_entrega else '1, 2, 3, 4, 6, 7'
        
        return self.fetchall(f'''
            SELECT
                V.id_ventas,
                U.nombre             AS nombre_vendedor,
                C.nombre             AS nombre_cliente,
                fecha_hora_creacion,
                {col_fecha_entrega}
                SUM(importe)         AS total,
                estado,
                comentarios
            FROM
                ventas V
                LEFT JOIN usuarios U
                    ON V.id_usuarios = U.id_usuarios
                LEFT JOIN clientes C
                    ON V.id_clientes = C.id_clientes
                LEFT JOIN ventas_detallado VD
                    ON V.id_ventas = VD.id_ventas
			WHERE
                {clausula_where}
                AND (CAST(fecha_hora_creacion AS DATE) BETWEEN ? AND ?
                     OR estado LIKE 'Recibido%')
                {restrict}
            GROUP BY
                {clausula_group}
            ORDER BY
                1 DESC;
        ''', (inicio.toPython(), final.toPython()))
    
    tablaVentas = partialmethod(_tablaParcial, False) # <- fecha_entrega
    
    tablaPedidos = partialmethod(_tablaParcial, True) # <- fecha_entrega
    
    def obtenerFechas(self, id_venta: int):
        """ Obtener fechas de creación y entrega de la venta dada. """
        return self.fetchone('''
            SELECT  fecha_hora_creacion,
                    fecha_hora_entrega
            FROM    ventas
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
        
            Cantidad | Producto | Precio | Descuento | Importe
            
            Es el único método que regresa objetos ItemVenta ya que se
            necesita calcular el total de descuento para los tickets. """
        from backends.CrearVenta import ItemVenta, ItemGranFormato
        
        id_, abrev, precio, desc, cant, duplex, categoria = range(7)
        manejador = ManejadorProductos(self._conn)
        
        for p in self.fetchall('''
            SELECT	P.id_productos,
                    abreviado,
                    precio,
                    descuento,
                    cantidad,
                    VD.duplex,
                    P.categoria
            FROM	ventas_detallado VD
                    LEFT JOIN productos P
                           ON VD.id_productos = P.id_productos
            WHERE	id_ventas = ?;
        ''', (id_venta,)):
            data = (0, '', p[abrev], p[precio], p[desc], p[cant], '')
            if p[categoria] == 'S':
                item = ItemVenta(*data, p[duplex])
            else:
                min_m2, _ = manejador.obtenerGranFormato(p[id_])
                item = ItemGranFormato(*data, min_m2)
            yield item
    
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
    
    def obtenerVendedorAsociado(self, id_venta: int):
        """ Obtener nombre de vendedor asociado a la venta. """
        result = self.fetchone('''
            SELECT	U.nombre
            FROM	Ventas AS V
                    LEFT JOIN Usuarios AS U
                           ON V.id_usuarios = U.id_usuarios
            WHERE	V.id_ventas = ?;
        ''', (id_venta,))
        if result:
            return result[0]
    
    def obtenerImporteTotal(self, id_venta: int) -> Moneda:
        """ Obtiene el importe total de una venta. """
        result = self.fetchone('''
            SELECT  SUM(importe)
            FROM    Ventas_Detallado
            WHERE   id_ventas = ?;
        ''', (id_venta,))
        
        try:
            return Moneda(result[0])
        except ValueError:
            return None
    
    def obtenerAnticipo(self, id_venta: int) -> Moneda:
        """ Obtiene el anticipo recibido de una orden pendiente.
            Si no es una orden pendiente, regresa None. """
        result = self.fetchone('''
            SELECT  estado
            FROM    Ventas
            WHERE   id_ventas = ?;
        ''', (id_venta,))
        
        try:
            estado = result[0]
            return Moneda(estado.split()[1])
        except (ValueError, IndexError):
            return None
    
    def obtenerSaldoRestante(self, id_venta: int):
        """ Residuo del importe total menos anticipos. """
        return self.obtenerImporteTotal(id_venta) - self.obtenerAnticipo(id_venta)
        
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
            return result[0]
    
    def obtenerPagosVenta(self, id_venta: int):
        """ Obtener listado de pagos realizados en esta venta.
            
            Acepta parámetro para obtener un pago específico. """
        return self.fetchall(f'''
            SELECT  fecha_hora,
                    metodo,
                    monto,
                    recibido
            FROM    ventas_pagos VP
                    LEFT JOIN metodos_pago MP
                        ON VP.id_metodo_pago = MP.id_metodo_pago
            WHERE   id_ventas = ?
            ORDER   BY fecha_hora ASC;
        ''', (id_venta,))
            
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
            VALUES (?,?,?,?,?,?,?,?);
        ''', params, commit=True)
    
    def insertarPago(self, id_ventas: int, metodo: str,
                           monto: Moneda, recibido: Moneda,
                           commit: bool = False):
        """ Inserta pago de venta a tabla ventas_pagos.
        
            No hace `commit`, a menos que se indique lo contrario. """
        id_metodo = ManejadorMetodosPago(self._conn).obtenerIdMetodo(metodo)
        
        return self.execute('''
            INSERT INTO ventas_pagos (
                id_ventas, id_metodo_pago, fecha_hora, monto, recibido
            )
            VALUES (?,?,?,?,?);
        ''', (id_ventas, id_metodo, datetime.now(), monto, recibido), commit=commit)
    
    def anularPagos(self, id_venta: int, commit: bool = False):
        """ Anula pagos en tabla ventas_pagos. No hace `commit` automáticamente. """
        for fecha, metodo, monto, recibido in self.obtenerPagosVenta(id_venta):
            if not self.insertarPago(id_venta, metodo, -monto, 0.):
                return False
        return True
    
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
        
        manejador = ManejadorProductos(self._conn)
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


class ManejadorUsuarios(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Usuarios. """
    
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
            ORDER   BY UPPER(U.nombre) ASC;
        ''')
    
    def obtenerUsuario(self, usuario: str):
        """ Obtener tupla de usuario dado el identificador de usuario. """
        return self.fetchone('''
            SELECT  *
            FROM    Usuarios
            WHERE   usuario = ?;
        ''', (usuario,))
    
    def crearUsuarioServidor(self, usuario: str, psswd: str):
        """ Registrar usuario en servidor Firebird.
            
            No hace commit. """
        return self.execute(f"CREATE USER {usuario} PASSWORD '{psswd}';")
    
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
        """ Dar de baja usuario del sistema y eliminar del servidor Firebird. 
            
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
        if self.execute(f'GRANT ADMINISTRADOR, VENDEDOR TO {usuario} WITH ADMIN OPTION;'):
            return self.execute(f'ALTER USER {usuario} GRANT ADMIN ROLE;', commit=True)
        else:
            return False
    
    def retirarRoles(self, usuario: str):
        """ Retirar roles VENDEDOR, ADMINISTRADOR del usuario. 
        
            No hace commit. """
        if self.execute(f'REVOKE ADMINISTRADOR, VENDEDOR FROM {usuario};'):
            return self.execute(f'ALTER USER {usuario} REVOKE ADMIN ROLE;')
        else:
            return False
    
    def cambiarPsswd(self, usuario: str, psswd: str):
        """ Cambiar contraseña del usuario. No hace commit. """
        return self.execute(f"ALTER USER {usuario} PASSWORD '{psswd}';")
