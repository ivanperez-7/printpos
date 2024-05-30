""" ARCHIVO PRINCIPAL.
    Inicia una QApplication y abre la ventana de iniciar sesión. """
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator
from PySide6.QtGui import QPalette, Qt


class PrintPOS(QApplication):
    """ Subclase de QApplication que configura varios elementos como corresponde.
        Invocar método iniciar() para crear ventana de iniciar sesión. """

    def __init__(self):
        super().__init__()
        
        self.licencia_validada = False
        
        self.setStyle('Fusion')
        self.configurarPaleta()
        self.instalarTraductor()
    
    def iniciar(self):
        """ Crea ventana de iniciar sesión e invoca método exec(). """
        from backends.Login import App_Login
        login = App_Login()
        return self.exec()
    
    def configurarPaleta(self):
        """ Configura paleta y estilo de la aplicación. """
        palette = self.palette()
        CR = QPalette.ColorRole
        
        palette.setColor(CR.Window, Qt.white)  # color de ventana -> gris claro
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


if QApplication.instance() is None:
    app = PrintPOS()
else:
    app = QApplication.instance()


if __name__ == '__main__':
    # este módulo genera mucho tiempo de espera, por alguna razón
    from pdf.generadores import *
    app.iniciar()
