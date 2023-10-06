""" ARCHIVO PRINCIPAL.
    Inicia una QApplication y abre la ventana de iniciar sesión. """
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator
from PySide6.QtGui import QPalette, Qt

from backends.Login import App_Login


class PrintPOS(QApplication):
    """ Subclase de QApplication que configura varios elementos como corresponde.
        Invocar método iniciar() para crear ventana de iniciar sesión. """

    def __init__(self):
        super().__init__()
        
        self.setStyle('Fusion')
        
        self.configurarPaleta()
        self.instalarTraductor()
    
    def iniciar(self):
        """ Crea ventana de iniciar sesión e invoca método exec(). """
        login = App_Login()
        return self.exec()
    
    def configurarPaleta(self):
        """ Configura paleta y estilo de la aplicación. """
        palette = self.palette()
        CR = QPalette.ColorRole
        
        palette.setColor(CR.Window, 0xF5F5F5)  # color de ventana -> gris claro
        palette.setColor(CR.WindowText, Qt.black)  # texto de ventana -> negro
        palette.setColor(CR.Base, Qt.white)  # color base -> blanco
        palette.setColor(CR.AlternateBase, Qt.white)  # color alternativo base -> blanco
        palette.setColor(CR.Text, Qt.black)  # color de texto -> negro
        palette.setColor(CR.Button, Qt.white)  # botones -> blanco
        palette.setColor(CR.ButtonText, Qt.black)  # texto de botones -> negro
        palette.setColor(CR.PlaceholderText, 0x808080)  # texto placeholder -> gris
        
        self.setPalette(palette)
    
    def instalarTraductor(self):
        """ Instala traductor para idioma español. """
        tr = QTranslator(self)
        tr.load('qtbase_es.qm', directory='resources/translations')
        return self.installTranslator(tr)
    
    def __call__(self):
        return self.iniciar()

    def __repr__(self):
        return 'QApplication afitriona de PrintPOS.'


app = PrintPOS()

if __name__ == '__main__':
    app.iniciar()
