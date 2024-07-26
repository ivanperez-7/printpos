from unittest import TestCase, main

import PrintPOS
import sql.core


class ConnectionsMixin:  # cuentas válidas y existentes
    con_user = sql.core.conectar_firebird("pablo", "1", "vendedor")
    con_admin = sql.core.conectar_firebird("ivanperez", "123", "administrador")


class WidgetsTest(TestCase, ConnectionsMixin):
    def test_widgets_crear_venta(self):
        from backends.CrearVenta import App_SeleccionarCliente, App_AgregarProducto
        from utils.mydataclasses import BaseItem

        def check_list(selected):
            self.assertIsInstance(selected, list)
            print("noice")

        def check_item(item):
            self.assertIsInstance(item, BaseItem)
            print("noice")

        wdg = App_SeleccionarCliente(self.con_user, None)
        wdg.success.connect(check_list)
        wdg.ui.tabla_seleccionar.selectRow(0)
        wdg.ui.btAgregar.click()

        wdg2 = App_AgregarProducto(self.con_user, None)
        wdg2.success.connect(check_item)
        wdg2.ui.tabWidget.setCurrentIndex(0)  # productos simples
        wdg2.ui.tabla_seleccionar.selectRow(0)
        wdg2.ui.txtCantidad.setText("25")
        wdg2.ui.btAgregar.click()

        wdg3 = App_AgregarProducto(self.con_user, None)
        wdg3.success.connect(check_item)
        wdg3.ui.tabWidget.setCurrentIndex(1)  # productos gran formato
        wdg3.ui.tabla_granformato.selectRow(0)
        wdg3.ui.txtAlto.setText("1")
        wdg3.ui.txtAncho.setText("1")
        wdg3.ui.txtAltoMaterial.setText("1")
        wdg3.ui.txtAnchoMaterial.setText("1")
        wdg3.ui.btAgregar.click()

    def test_admin_decorator(self):
        from utils.mydecorators import requiere_admin

        @requiere_admin
        def func_with_no_args():
            pass

        @requiere_admin
        def func_with_conn_arg(conn):
            self.assertIsNotNone(conn)

        @requiere_admin
        def func_with_conn_arg_and_users(a, b, conn):
            self.assertIsNotNone(conn)
            self.assertEqual(2 + 3, 5)

        func_with_no_args()
        func_with_conn_arg()
        func_with_conn_arg_and_users(2, 5)


if __name__ == "__main__":
    main()
