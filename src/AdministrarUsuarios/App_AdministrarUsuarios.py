import fdb

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QPixmap, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp

from mydecorators import con_fondo
from myutils import formatDate, son_similar
from mywidgets import LabelAdvertencia, WarningDialog


#####################
# VENTANA PRINCIPAL #
#####################

class App_AdministrarUsuarios(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de usuarios.
    TODO:
        - mecanismo de reseteo de contraseña (sin permisos de admin)
        - registros de acciones: inicios de sesión, modificación de ajustes y usuarios, acciones en general
        - personalización: foto de perfil y colores del UI
        - reportes de actividad de usuario: inicios de sesión, # de ventas realizadas, ganancias generadas
    """
    def __init__(self, parent=None):
        from AdministrarUsuarios.Ui_AdministrarUsuarios import Ui_AdministrarUsuarios
        
        super().__init__()

        self.ui = Ui_AdministrarUsuarios()
        self.ui.setupUi(self)

        self.session = parent.session  # conexión y usuario actual
        self.filtro = 0
        
        LabelAdvertencia(self.ui.tabla_usuarios, '¡No se encontró ningún usuario!')

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu()

        default = popup.addAction(
            'Usuario', lambda: self.cambiarFiltro('usuario'))
        popup.addAction(
            'Nombre', lambda: self.cambiarFiltro('nombre'))
        popup.addAction(
            'Permisos', lambda: self.cambiarFiltro('permisos'))
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiarFiltro('nombre'))

        # dar formato a la tabla principal
        header = self.ui.tabla_usuarios.horizontalHeader()

        for col in range(self.ui.tabla_usuarios.columnCount()):
            if col in {0, 2}:
                header.setSectionResizeMode(
                    col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # añade eventos para los botones
        self.ui.lbAgregar.mousePressEvent = self.registrarUsuario
        self.ui.lbEditar.mousePressEvent = self.editarUsuario
        self.ui.lbQuitar.mousePressEvent = self.quitarUsuario
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        self.ui.mostrarCheck.stateChanged.connect(self.mostrarTrigger)

    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_usuarios.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def mostrarTrigger(self, state):
        self.update_display(rescan=True)

    def cambiarFiltro(self, filtro):
        """
        Modifica el filtro de búsqueda.
        """
        self.filtro = [
            'usuario',
            'nombre',
            'permisos',
            'ultima'
        ].index(filtro)
                
        self.ui.searchBar.setPlaceholderText(f'Busque usuario por {filtro}...')
        
        if self.ui.searchBar.text():
            self.update_display()

    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de usuarios.
        Acepta una cadena de texto para la búsqueda de usuarios.
        También lee de nuevo la tabla de usuarios, si se desea.
        """
        if rescan:
            filtrar = 'WHERE permisos IS NOT NULL' \
                      if not self.ui.mostrarCheck.isChecked() else ''

            crsr = self.session['conn'].cursor()
            crsr.execute(f'''
            SELECT  usuario,
                    nombre,
                    permisos,
                    MAX(fecha_hora_creacion) AS ultimaVenta
            FROM    Usuarios AS U
                    LEFT JOIN Ventas AS V
                           ON U.id_usuarios = V.id_usuarios
            {filtrar}
            GROUP   BY 1, 2, 3
            ORDER   BY U.nombre ASC;
            ''')

            self.all = crsr.fetchall()
            self.ui.lbContador.setText(
                f'{len(self.all)} usuarios en la base de datos.')

        tabla = self.ui.tabla_usuarios
        tabla.setRowCount(0)
        
        bold = QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        found = self.all if not txt_busqueda else \
                filter(
                    lambda c: c[self.filtro] 
                              and son_similar(txt_busqueda, c[self.filtro]), 
                    self.all)

        for row, usuario in enumerate(found):
            tabla.insertRow(row)

            for col, dato in enumerate(usuario):
                if isinstance(dato, int):
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 1).setFont(bold)

        tabla.resizeRowsToContents()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarUsuario(self, _):
        """
        Abre ventana para registrar un usuario.
        """
        self.new = App_RegistrarUsuario(self)

    def editarUsuario(self, _):
        """
        Abre ventana para editar un usuario seleccionado.
        """
        selected = self.ui.tabla_usuarios.selectedItems()

        if selected:
            self.new = App_EditarUsuario(self, selected[0].text())

    def quitarUsuario(self, _):
        """
        Pide confirmación para eliminar usuarios de la base de datos.
        """
        selected = self.ui.tabla_usuarios.selectedItems()

        if not selected:
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Los usuarios seleccionados se darán '
                          'de baja del sistema. ¿Desea continuar?',
                          qm.Yes | qm.No)

        if ret != qm.Yes:
            return
        
        values = selected[0].text()

        conn = self.session['conn']
        crsr = conn.cursor()

        # crea un cuadro que notifica el resultado de la operación
        try:
            crsr.execute('''
            UPDATE  Usuarios
            SET     permisos = NULL
            WHERE   usuario = ?;
            ''', (values,))
            
            crsr.execute(f'DROP USER {values};')

            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, '¡Hubo un error!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se dieron de baja los usuarios seleccionados.')
        self.update_display(rescan=True)

    def goHome(self, _):
        """
        Cierra la ventana y regresa al inicio.
        """
        from Home import App_Home

        parent = self.parentWidget()       # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)


#################################
# VENTANAS PARA EDITAR USUARIOS #
#################################
@con_fondo
class Base_EditarUsuario(QtWidgets.QMainWindow):
    """Clase base para la ventana de registrar o editar usuario."""
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str
    
    def __init__(self, first: App_AdministrarUsuarios):
        from AdministrarUsuarios.Ui_EditarUsuario import Ui_EditarUsuario
        
        super().__init__(first)

        self.ui = Ui_EditarUsuario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first: App_AdministrarUsuarios = first 
        self.session = first.session  # conexión a la base de datos y usuario actual
            
        # validador para nombre de usuario
        regexp = QRegExp(r'[a-zA-Z0-9_$]+')
        validador = QRegExpValidator(regexp)
        self.ui.txtUsuario.setValidator(validador)

        # deshabilita eventos del mouse para los textos en los botones
        items = vars(self.ui)
        items = [items[name] for name in items if 'label_' in name]

        for w in items:
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # crear eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btRegistrar.clicked.connect(self.editar)

        self.show()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def cambioContrasena(self) -> bool:
        """Cada clase tiene su manera de decidir si hay cambio de contraseña."""
        pass
    
    def editar(self):
        """
        Intenta editar datos de la tabla Usuarios y
        se notifica al usuario del resultado de la operación.
        """
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
        
        conn = self.session['conn']
        crsr = conn.cursor()

        try:            
            self.ejecutarConsulta(crsr, usuarios_db_parametros)
            
            if permisos == 'Administrador':
                crsr.execute(f'GRANT ADMINISTRADOR, VENDEDOR TO {usuario} WITH ADMIN OPTION;')
            else:
                crsr.execute(f'GRANT VENDEDOR TO {usuario};')

            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, self.MENSAJE_ERROR, str(err))
            return
        
        QtWidgets.QMessageBox.information(
            self, 'Éxito', self.MENSAJE_EXITO)
        
        self.first.update_display(rescan=True)
        self.close()
    
    def ejecutarConsulta(self, crsr: fdb.Cursor, params: tuple):
        """Método que insertará o modificará usuario."""
        pass


class App_RegistrarUsuario(Base_EditarUsuario):
    """Backend para la ventana de registrar usuario."""
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
    def cambioContrasena(self) -> bool:
        """Siempre hay cambio de contraseña."""
        return True
    
    def ejecutarConsulta(self, crsr, params):
        crsr.execute('''
        INSERT INTO Usuarios (
            usuario, nombre, permisos
        )
        VALUES
            (?,?,?);
        ''', params)
        
        usuario, _, permisos = params
        psswd = self.ui.txtPsswd.text()
        
        admin_role = 'GRANT ADMIN ROLE' if permisos == 'Administrador' else ''
        
        crsr.execute(f'''CREATE USER {usuario} PASSWORD '{psswd}' {admin_role};''')


class App_EditarUsuario(Base_EditarUsuario):
    """Backend para la ventana de editar usuario."""
    MENSAJE_EXITO = '¡Se editó el usuario!'
    MENSAJE_ERROR = '¡No se pudo editar el usuario!'
    
    def __init__(self, first: App_AdministrarUsuarios, usuario: str):
        super().__init__(first)

        crsr = self.session['conn'].cursor()
        
        crsr.execute('''
        SELECT  usuario,
                nombre,
                permisos
        FROM    Usuarios
        WHERE   usuario = ?;
        ''', (usuario,))
        
        usuario, nombre, permisos = crsr.fetchone()

        self.ui.txtUsuario.setText(usuario)
        self.ui.txtNombre.setText(nombre)
        self.ui.boxPermisos.setCurrentText(permisos)        
        self.ui.txtUsuario.setReadOnly(True)
        
        self.ui.cambiarPsswd.toggled.connect(self.cambiarTrigger)

        self.usuario = usuario  # usuario a editar

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def cambioContrasena(self) -> bool:
        """Hay cambio de contraseña si se solicita."""
        return self.ui.cambiarPsswd.isChecked()
    
    def cambiarTrigger(self, state):
        """
        Indica si se desea cambiar la contraseña en la operación.
        """
        enable = bool(state)

        self.ui.groupPsswd.setEnabled(enable)
        self.ui.groupPsswdConf.setEnabled(enable)
    
    def ejecutarConsulta(self, crsr, params):
        crsr.execute('''
        UPDATE  Usuarios
        SET     usuario = ?,
                nombre = ?,
                permisos = ?
        WHERE   usuario = ?;
        ''', (*params, self.usuario))
        
        crsr.execute(f'REVOKE ADMINISTRADOR, VENDEDOR FROM {self.usuario};')
        
        if self.cambioContrasena:
            psswd = self.ui.txtPsswd.text()
            crsr.execute(f'''ALTER USER {self.usuario} PASSWORD '{psswd}';''')
