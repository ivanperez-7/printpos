"""
ARCHIVO PRINCIPAL.
Inicia una QApplication y abre la ventana de iniciar sesión.
"""
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor

from Login import App_Login


def main():
    app = QApplication()
    app.setStyle(QStyleFactory.create('Fusion'))
    
    palette = app.palette()
    CR = QPalette.ColorRole
    palette.setColor(CR.Window, QColor(245, 245, 245))        # Set window background color to white
    palette.setColor(CR.WindowText, QColor(0, 0, 0))          # Set window text color to black
    palette.setColor(CR.Base, QColor(255, 255, 255))          # Set base color to white (FIJO)
    palette.setColor(CR.AlternateBase, QColor(255, 255, 255)) # Set alternate base color to light gray
    palette.setColor(CR.ToolTipBase, QColor(255, 255, 220))   # Set tooltip background color to light yellow
    palette.setColor(CR.ToolTipText, QColor(0, 0, 0))         # Set tooltip text color to black
    palette.setColor(CR.Text, QColor(0, 0, 0))                # Set text color to black
    palette.setColor(CR.Button, QColor(255, 255, 255))        # Set button background color to light gray
    palette.setColor(CR.ButtonText, QColor(0, 0, 0))          # Set button text color to black
    palette.setColor(CR.PlaceholderText, QColor(128, 128, 128))
    app.setPalette(palette)
    
    login = App_Login()
    app.exec()

if __name__ == '__main__':
    main()
