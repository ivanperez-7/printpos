from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

from utils.sql import ManejadorUsuarios
from utils.mydecorators import fondo_oscuro
from utils.myinterfaces import InterfazFiltro
from utils.myutils import *
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal


#####################
# VENTANA PRINCIPAL #
#####################

class App_AdministrarUsuarios(QtWidgets.QWidget):
    """ Backend para la ventana de administración de usuarios.
        TODO:
            - mecanismo de reseteo de contraseña (sin permisos de admin)
            - registros de acciones: inicios de sesión, modificación de ajustes y usuarios, acciones en general
            - personalización: foto de perfil y colores del UI """

    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_AdministrarUsuarios import Ui_AdministrarUsuarios

        super().__init__()

        self.ui = Ui_AdministrarUsuarios()
        self.ui.setupUi(self)

        LabelAdvertencia(self.ui.tabla_usuarios, '¡No se encontró ningún usuario!')

        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, [
            ('Nombre', 'nombre', 1),
            ('Usuario', 'nombre de usuario', 0)
        ])
        self.filtro.filtroCambiado.connect(
            lambda txt: (self.ui.searchBar.setPlaceholderText(f'Busque usuario por {txt}...'),
                         self.update_display()))

        # añade eventos para los botones
        self.ui.btAgregar.clicked.connect(self.registrarUsuario)
        self.ui.btEditar.clicked.connect(self.editarUsuario)
        self.ui.btEliminar.clicked.connect(self.quitarUsuario)
        self.ui.btRegresar.clicked.connect(self.goHome)

        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        self.ui.mostrarCheck.stateChanged.connect(lambda: self.update_display())

        self.ui.tabla_usuarios.configurarCabecera(lambda col: col in {0, 2})

    def showEvent(self, event):
        self.update_display(rescan=True)

    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_usuarios.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de usuarios.
            Acepta una cadena de texto para la búsqueda de usuarios.
            También lee de nuevo la tabla de usuarios, si se desea. """
        if rescan:
            manejador = ManejadorUsuarios(self.conn)
            self.all = manejador.obtenerVista('view_all_usuarios')

        if txt_busqueda := self.ui.searchBar.text().strip():
            found = [c for c in self.all
                     if c[self.filtro.filtro]
                     if son_similar(txt_busqueda, c[self.filtro.filtro])]
        else:
            found = self.all
        if not self.ui.mostrarCheck.isChecked():
            found = [c for c in found if c[2]]

        self.ui.lbContador.setText(
            f'{len(found)} usuarios en la base de datos.')

        tabla = self.ui.tabla_usuarios
        tabla.modelo = tabla.Modelos.RESALTAR_SEGUNDA
        tabla.llenar(found)
        tabla.resizeRowsToContents()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarUsuario(self):
        """ Abre ventana para registrar un usuario."""
        widget = App_RegistrarUsuario(self)
        widget.success.connect(
            lambda: self.update_display(rescan=True))

    def editarUsuario(self):
        """ Abre ventana para editar un usuario seleccionado. """
        if selected := self.ui.tabla_usuarios.selectedItems():
            widget = App_EditarUsuario(self, selected[0].text())
            widget.success.connect(
                lambda: self.update_display(rescan=True))

    def quitarUsuario(self):
        """ Pide confirmación para eliminar usuarios de la base de datos. """
        if (
                not (selected := self.ui.tabla_usuarios.selectedItems())
                or (usuario := selected[0].text()) in ['SYSDBA', self.user.usuario]
                or not selected[2].text()
        ):
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        manejador = ManejadorUsuarios(self.conn)

        ret = qm.question(self, 'Atención',
                          'Los usuarios seleccionados se darán '
                          'de baja del sistema. ¿Desea continuar?')

        if ret == qm.Yes and manejador.eliminarUsuario(usuario):
            qm.information(self, 'Éxito', 'Se dieron de baja los usuarios seleccionados.')
            self.update_display(rescan=True)

    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#################################
# VENTANAS PARA EDITAR USUARIOS #
#################################
@fondo_oscuro
class Base_EditarUsuario(QtWidgets.QWidget):
    """ Clase base para la ventana de registrar o editar usuario. """
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str

    success = Signal()

    def __init__(self, first: App_AdministrarUsuarios):
        from ui.Ui_EditarUsuario import Ui_EditarUsuario

        super().__init__(first)

        self.ui = Ui_EditarUsuario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # guardar conexión y usuario como atributos
        self.conn = first.conn
        self.user = first.user

        # validador para nombre de usuario
        self.ui.txtUsuario.setValidator(FabricaValidadores.IdFirebird)

        # deshabilita eventos del mouse para los textos en los botones
        for name, item in vars(self.ui).items():
            if 'label_' in name:
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btRegistrar.clicked.connect(self.editar)

        self.show()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def cambioContrasena(self) -> bool:
        """ Cada clase tiene su manera de decidir si hay cambio de contraseña. """
        raise NotImplementedError('BEIS CLASSSSSSS')

    def editar(self):
        """ Intenta editar datos de la tabla Usuarios y
            se notifica al usuario del resultado de la operación. """
        if self.cambioContrasena:
            psswd = self.ui.txtPsswd.text()
            psswd_conf = self.ui.txtPsswdConf.text()

            # contraseñas vacías o no iguales
            if not (psswd and psswd_conf):
                return
            if psswd != psswd_conf:
                QtWidgets.QMessageBox.warning(self, 'Atención',
                                              '¡Las contraseñas no coinciden!')
                return

        usuario = self.ui.txtUsuario.text().upper()
        permisos = self.ui.boxPermisos.currentText()

        usuarios_db_parametros = tuple(v or None for v in (
            usuario,
            self.ui.txtNombre.text().strip(),
            permisos
        ))

        if not self.insertar_o_modificar(usuarios_db_parametros):
            return

        manejador = ManejadorUsuarios(self.conn)

        if permisos == 'Administrador':
            result = manejador.otorgarRolAdministrador(usuario)
        else:
            result = manejador.otorgarRolVendedor(usuario)

        if result:
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)
            self.success.emit()
            self.close()

    def insertar_o_modificar(self, params: tuple) -> bool:
        """ Método que insertará o modificará usuario. """
        raise NotImplementedError('BEIS CLASSSSSSS')


class App_RegistrarUsuario(Base_EditarUsuario):
    """ Backend para la ventana de registrar usuario. """
    MENSAJE_EXITO = '¡Se registró el usuario!'
    MENSAJE_ERROR = '¡No se pudo registrar el usuario!'

    def __init__(self, first: App_AdministrarUsuarios):
        super().__init__(first)

        self.ui.cambiarPsswd.hide()
        self.ui.groupPsswd.setEnabled(True)
        self.ui.groupPsswdConf.setEnabled(True)

        self.ui.lbTitulo.setText('Registrar usuario')
        self.ui.label_aceptar.setText('Registrar')
        self.ui.label_icono.setPixmap(QPixmap(':/img/resources/images/plus.png'))

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def cambioContrasena(self):
        """ Siempre hay cambio de contraseña. """
        return True

    def insertar_o_modificar(self, params):
        """ Insertar en DB y crear en Firebird. """
        manejador = ManejadorUsuarios(self.conn)
        usuario = params[0]
        psswd = self.ui.txtPsswd.text()

        return (manejador.insertarUsuario(params)
                and manejador.crearUsuarioServidor(usuario, psswd))


class App_EditarUsuario(Base_EditarUsuario):
    """ Backend para la ventana de editar usuario. """
    MENSAJE_EXITO = '¡Se editó el usuario!'
    MENSAJE_ERROR = '¡No se pudo editar el usuario!'

    def __init__(self, first: App_AdministrarUsuarios, usuario_: str):
        super().__init__(first)

        manejador = ManejadorUsuarios(self.conn)
        id, usuario, nombre, permisos, *_ = manejador.obtenerUsuario(usuario_)

        self.usuario = usuario  # usuario a editar
        self.permisos = permisos

        if not permisos:  # usuario existente pero dado de baja
            self.ui.cambiarPsswd.setChecked(True)
            self.ui.cambiarPsswd.setEnabled(False)
            self.cambiarTrigger(True)
        if usuario in ['SYSDBA', self.user.usuario]:
            self.ui.boxPermisos.setEnabled(False)
        self.ui.txtUsuario.setText(usuario)
        self.ui.txtNombre.setText(nombre)
        self.ui.boxPermisos.setCurrentText(permisos)
        self.ui.txtUsuario.setReadOnly(True)

        self.ui.cambiarPsswd.toggled.connect(self.cambiarTrigger)

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def cambioContrasena(self):
        """ Hay cambio de contraseña si se solicita o si el usuario
            no tiene permisos en la DB (fue dado de baja). """
        return self.ui.cambiarPsswd.isChecked() or not self.permisos

    def cambiarTrigger(self, state):
        """ Indica si se desea cambiar la contraseña en la operación. """
        self.ui.groupPsswd.setEnabled(state)
        self.ui.groupPsswdConf.setEnabled(state)

    def insertar_o_modificar(self, params):
        """ Modifica datos del usuario y cambia contraseña y/o permisos.
            1. Actualiza usuario en tabla usuarios
            2. Al haberse dado de baja, intenta crear usuario
            3. Si no, y si se desea, cambiar contraseña en servidor Firebird
            4. Si se desea, retirar roles ADMINISTRADOR y VENDEDOR para cambiar de rol """
        manejador = ManejadorUsuarios(self.conn)
        psswd = self.ui.txtPsswd.text()

        actualizarUsuario = lambda: manejador.actualizarUsuario(self.usuario, params)
        actualizarFirebird = lambda: True  # crear usuario o actualizar contraseña
        retirarRoles = lambda: True

        if not self.permisos:
            actualizarFirebird = lambda: manejador.crearUsuarioServidor(self.usuario, psswd)
        elif self.ui.cambiarPsswd.isChecked():
            actualizarFirebird = lambda: manejador.cambiarPsswd(self.usuario, psswd)

        if self.ui.boxPermisos.isEnabled():
            retirarRoles = lambda: manejador.retirarRoles(self.usuario)

        return actualizarUsuario() and actualizarFirebird() and retirarRoles()
