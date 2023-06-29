"""
ARCHIVO PRINCIPAL.
Inicia una QApplication y abre la ventana de iniciar sesión.
"""
from PyQt5.QtWidgets import QApplication, QStyleFactory
from Login import App_Login

def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('fusion'))
    login = App_Login()
    app.exec()

if __name__ == '__main__':
    main()
