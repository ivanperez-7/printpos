""" ARCHIVO PRINCIPAL.
    Inicia una QApplication y abre la ventana de iniciar sesión. """
import os

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide6.QtGui import QPalette, QColor

from Login import App_Login


class PrintPOS(QApplication):
    def __init__(self):
        super().__init__()
        
        self.configurarEstilo()
        self.instalarTraductor()
        
        login = App_Login()
        self.exec()
    
    def configurarEstilo(self):
        BLANCO = QColor(255, 255, 255)
        NEGRO = QColor(0, 0, 0)
        GRIS = QColor(128, 128, 128)
        
        palette = self.palette()
        CR = QPalette.ColorRole
        
        palette.setColor(CR.Window, QColor(245, 245, 245))  # color de ventana -> gris claro
        palette.setColor(CR.WindowText, NEGRO)  # texto de ventana -> negro
        palette.setColor(CR.Base, BLANCO)  # color base -> blanco
        palette.setColor(CR.AlternateBase, BLANCO)  # color alternativo base -> blanco
        palette.setColor(CR.Text, NEGRO)  # color de texto -> negro
        palette.setColor(CR.Button, BLANCO)  # botones -> blanco
        palette.setColor(CR.ButtonText, NEGRO)  # texto de botones -> negro
        palette.setColor(CR.PlaceholderText, GRIS)  # texto placeholder -> gris
        
        self.setPalette(palette)
        self.setStyle(QStyleFactory.create('Fusion'))
    
    def instalarTraductor(self):
        self._translator = QTranslator()
        self._translator.load('qtbase_es.qm', directory='resources/translations')
        return self.installTranslator(self._translator)


if __name__ == '__main__':
    app = PrintPOS()
