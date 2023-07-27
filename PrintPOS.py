""" ARCHIVO PRINCIPAL.
    Inicia una QApplication y abre la ventana de iniciar sesión. """
import os

from PySide6.QtWidgets import QApplication

from Login import App_Login


def configurarEstilo(app: QApplication):
    from PySide6.QtWidgets import QStyleFactory
    from PySide6.QtGui import QPalette, QColor
    
    BLANCO = QColor(255, 255, 255)
    NEGRO = QColor(0, 0, 0)
    GRIS = QColor(128, 128, 128)
    
    palette = app.palette()
    CR = QPalette.ColorRole
    
    palette.setColor(CR.Window, QColor(245, 245, 245))  # color de ventana -> gris claro
    palette.setColor(CR.WindowText, NEGRO)              # texto de ventana -> negro
    palette.setColor(CR.Base, BLANCO)                   # color base -> blanco
    palette.setColor(CR.AlternateBase, BLANCO)          # color alternativo base -> blanco
    palette.setColor(CR.Text, NEGRO)                # color de texto -> negro
    palette.setColor(CR.Button, BLANCO)             # botones -> blanco
    palette.setColor(CR.ButtonText, NEGRO)          # texto de botones -> negro
    palette.setColor(CR.PlaceholderText, GRIS)      # texto placeholder -> gris
    
    app.setPalette(palette)
    app.setStyle(QStyleFactory.create('Fusion'))

def main():
    app = QApplication()
    configurarEstilo(app)
    login = App_Login()
    app.exec()


if __name__ == '__main__':
    main()
