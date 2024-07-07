from datetime import datetime
import random
from unittest import TestCase, main, mock

from PySide6.QtCore import QDateTime, QDate, QTime, Qt
from PySide6.QtTest import QTest

from core import Moneda
import PrintPOS
import sql


class ConnectionsMixin:  # cuentas válidas y existentes
    con_user = sql.conectar_firebird('pablo', '1', 'vendedor')
    con_admin = sql.conectar_firebird('ivanperez', '123', 'administrador')


class RandomTests(TestCase, ConnectionsMixin):
    def test_utils_moneda(self):
        total = Moneda('$450.0')
        self.assertEqual(total / 2, 450. / 2)
        
        dodgy = Moneda(457.7)
        self.assertEqual(dodgy - 1.1, 457.7 - 1.1)
        self.assertEqual(dodgy * Moneda('$25.0'), 457.7 * 25.)
        self.assertEqual(float(dodgy), 457.7)
        self.assertTrue(dodgy)
        self.assertFalse(dodgy - 457.7)
        
        with self.assertRaises(TypeError):
            self.assertIsNone(dodgy + '45.0')


    def test_create_credentials(self):
        from utils.mydataclasses import Usuario
        
        con = self.con_user
        user = Usuario.generarUsuarioActivo(sql.ManejadorUsuarios(con))
        
        self.assertTrue(isinstance(con, sql.Connection) and isinstance(user, Usuario))
        self.assertFalse(user.administrador)
        self.assertEqual(user.usuario, 'PABLO')
        
        with self.assertRaises(sql.Error):
            nah = sql.conectar_firebird('pablo', '123', 'vendedor')  # cuenta no existente
            self.assertIsNone(nah)
    
    def test_db_handlers(self):
        con = self.con_admin   # conexión válida
        man = sql.DatabaseManager(con, handle_exceptions=False)
        self.assertIsNotNone(man.fetchall('SELECT * FROM clientes;'))
        
        with self.assertRaises(AssertionError) as cm:   # conexión válida pero con rol inválido
            nah = sql.conectar_firebird('pablo', '1', 'administrador')
            man2 = sql.DatabaseManager(nah, handle_exceptions=False)
            self.assertIsNone(man2.nombreUsuarioActivo)
        
        with self.assertRaises(AssertionError) as cm:   # manejador con argumento inválido
            man2 = sql.DatabaseManager(None)
            self.assertIsNone(man2)
    
    def test_manejador_usuarios_ximeno(self):
        con = self.con_admin   # conexión válida
        man = sql.ManejadorUsuarios(con, handle_exceptions=False)
        
        self.assertIsNotNone(man.obtenerUsuario(x := 'XIMENO'))
        self.assertTrue(    # operaciones sobre usuario existente
            man.actualizarUsuario(x, (x, 'pablo antonio', 'Vendedor'))
            and man.cambiarPsswd(x, '1')
            and man.retirarRoles(x)
            and man.otorgarRolVendedor(x, commit=False)
        )
        self.assertTrue(    # operaciones sobre usuario nuevo
            man.crearUsuarioServidor(p := 'PABLO2', '1')
            and man.insertarUsuario((p, 'pablo dos', 'Vendedor'))
            and man.otorgarRolVendedor(p, commit=False)
            and man.eliminarUsuario(p, commit=False)
        )
        # usar un usuario modificado con una conexión existente
        # de dicho usuario al parecer no funciona.
    
    def test_manejador_caja(self):
        con = self.con_admin   # conexión válida
        man = sql.ManejadorCaja(con, handle_exceptions=False)
        
        self.assertIsInstance(man.obtenerFechaPrimerMov(), datetime)
        self.assertIsNotNone(man.obtenerMovimientos())
        
        res1 = man.insertarMovimiento((450., 'abono venta no sé', 1, 1), commit=False)
        res2 = man.insertarMovimiento((-35., 'pago renta xd', 1, 2), commit=False)
        self.assertTrue(res1 and res2)
    
    def test_manejador_ventas(self):
        con = self.con_admin
        man = sql.ManejadorVentas(con)
        
        self.assertIsNotNone(man.tablaVentas())
        self.assertIsNotNone(man.tablaPedidos())
        
    def test_dataclass_venta_and_item(self):
        from utils.mydataclasses import Venta, ItemVenta, ItemGranFormato
        
        venta = Venta()
        venta.agregarProducto(
            ItemVenta(1, 'IMP B/N 1', 'Impresión ByN', 0.7, 0.1, random.randint(1, 99), '', False))
        venta.fechaEntrega = QDateTime(QDate(2024, 6, 29), QTime(13, 27, 2))
        venta.id_cliente = 1
        
        self.assertFalse(venta.ventaVacia or venta.esVentaDirecta)
        
        venta.agregarProducto(
            ItemVenta(1, 'IMP B/N 1', 'Impresión ByN', 0.7, 0.1, random.randint(10, 200), '', False))
        venta.reajustarPrecios(sql.ManejadorProductos(self.con_user))
        
        self.assertFalse(venta[1].precio_unit == 0.7)
        self.assertGreater(venta.total_descuentos, 0.)
        
        venta.agregarProducto(
            p1 := ItemGranFormato(4, 'METRO2', 'Metro lona', 90., 0., 2, '', 1.))
        self.assertEqual(p1.importe, p1.precio_unit*p1.cantidad)
        venta.agregarProducto(
            p2 := ItemGranFormato(4, 'METRO3', 'Metro algo', 110., 0., 1.5, '', 2.))
        self.assertEqual(p2.importe, p2.precio_unit*p2.min_m2)
    
    def test_registrar_venta_detalles_y_pagos(self):
        con = self.con_user
        man = sql.ManejadorVentas(con)
        
        idx = man.insertarVenta((1, man.idUsuarioActivo, n := datetime.now(), n,
                                 None, False, 'Terminada'))
        self.assertIsInstance(idx, int)
        
        res1 = man.insertarDetallesVenta(idx, [(1, 151, 0.7, 0., '', False, tot := 151*0.7)],
                                         commit=False)
        self.assertTrue(res1)
        
        res2 = man.insertarPago(idx, 'Tarjeta de débito', 50., None, man.idUsuarioActivo)
        res3 = man.insertarPago(idx, 'Efectivo', tot-50., 150., man.idUsuarioActivo)
        self.assertTrue(res2 and res3)
        
        self.assertIsNotNone(man.obtenerDatosGeneralesVenta(idx))
        self.assertIsNotNone(man.obtenerTablaProductosVenta(idx))
        self.assertTrue(len(man.obtenerPagosVenta(idx)) == 2)
        self.assertIsNone(man.obtenerAnticipo(idx))   # <- no es venta por pedido !!!
        self.assertIsNone(man.obtenerSaldoRestante(idx))
        self.assertTrue(man.anularPagos(idx, 1))
        self.assertIsInstance(man.verificarPagos(idx), int)
    
    def test_registrar_pedido_detalles_y_pagos(self):
        con = self.con_user
        man = sql.ManejadorVentas(con, handle_exceptions=False)
        
        pago = Moneda(100)
        idx = man.insertarVenta((1, man.idUsuarioActivo, n := datetime.now(), n.replace(month=8),
                                 None, False, f'Recibido ${pago}'))
        self.assertIsInstance(idx, int)
        
        res1 = man.insertarDetallesVenta(idx, [(1, 200, 0.7, 0., '', False, tot := 200*0.7)],
                                         commit=False)
        self.assertTrue(res1)
        
        res2 = man.insertarPago(idx, 'Tarjeta de crédito', tot, pago, man.idUsuarioActivo)
        self.assertTrue(res2)
        
        self.assertIsNotNone(man.obtenerDatosGeneralesVenta(idx))
        self.assertIsNotNone(man.obtenerTablaProductosVenta(idx))
        self.assertIsNotNone(man.obtenerPagosVenta(idx))
        self.assertIsNotNone(man.obtenerAnticipo(idx))   # <- es venta por pedido
        self.assertIsNotNone(man.obtenerSaldoRestante(idx))
        self.assertIsInstance(man.verificarPagos(idx), int)
    
    def test_stack_pagos(self):
        from utils.mywidgets import StackPagos
        
        stack = StackPagos()
        stack.total = 250.
        
        wdg = stack.agregarPago()   # pago por transferencia, $150
        QTest.mouseClick(wdg.ui.btTransferencia, Qt.LeftButton)
        QTest.keyClicks(wdg.ui.txtPago, "150")
        
        wdg2 = stack.agregarPago()  # pago por tarjeta de débito, $100
        QTest.mouseClick(wdg2.ui.btDebito, Qt.LeftButton)
        QTest.keyClicks(wdg2.ui.txtPago, "100")
        
        self.assertTrue(stack.pagosValidos)
        
        stack.total = 0.

        stack.removeWidget(wdg2)
        stack.setCurrentWidget(wdg)
        QTest.mouseClick(wdg.ui.btEfectivo, Qt.LeftButton)
        wdg.ui.txtPago.clear()
        QTest.keyClicks(wdg.ui.txtPago, "0.0")
        
        self.assertFalse(stack.pagosValidos)   # no hemos permitido pagos de cero
        
        stack.permitir_nulo = True
        self.assertTrue(stack.pagosValidos)


if __name__ == '__main__':
    main()
