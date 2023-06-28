"""
Módulo con widgets personalizados varios.
"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QTextBrowser, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPolygon, QFont, QPainterPath, QIcon, QPixmap
from PyQt5.QtCore import Qt, QRectF, QPoint


class VentanaPrincipal(QMainWindow):
    def __init__(self, session, modulo):
        super().__init__()
        
        self.resize(1540, 800)
        self.setWindowTitle('PrintPOS')
        
        self.session = session
        self.en_venta = False
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        
        central_widget = modulo(self)
        self.setCentralWidget(central_widget)
        
        from Home import App_ConsultarPrecios
        self.consultarPrecios = App_ConsultarPrecios(self)
        
        self.show()
    
    def closeEvent(self, event):
        """
        En eventos específicos, restringimos el cerrado del sistema.
        """
        if self.en_venta and not self.session['user'].administrador:
            event.ignore()
        else:
            import os
            import shutil
            
            if os.path.exists('./tmp/'):
                shutil.rmtree('./tmp/')
            
            self.session['conn'].close()
            self.consultarPrecios.close()
            event.accept()


class SpeechBubble(QWidget):
    def __init__(self, parent, text = ''):
        super().__init__(parent)

        # Create the layout and QTextBrowser
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 17, 17, 17)

        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("""
            QTextBrowser { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: 0px solid;
                background: #c0c0c0;
                width:10px;    
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {         
        
                min-height: 0px;
                border: 0px solid red;
                border-radius: 4px;
                background-color: #1e3085;
            }
            QScrollBar::add-line:vertical {       
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:vertical {
            background: none;
            }
        """)
        self.text_browser.setPlainText(text)
        self.text_browser.setFont(QFont("Arial", 11))
        self.text_browser.setLineWrapMode(QTextBrowser.LineWrapMode.FixedPixelWidth)
        self.text_browser.setLineWrapColumnOrWidth(295)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.text_browser)
    
    def setText(self, txt):
        self.text_browser.setPlainText(txt)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the speech bubble background
        bubble_rect = self.rect().adjusted(10, 10, -10, -10)  # Add padding to the bubble

        # Draw the bubble shape
        bubble_path = QPainterPath()
        bubble_path.addRoundedRect(QRectF(bubble_rect), 10, 10)

        # Draw the triangle at the top middle
        triangle_path = QPolygon()
        triangle_center = bubble_rect.center().y()
        triangle_path << QPoint(bubble_rect.left(), triangle_center - 10)
        triangle_path << QPoint(bubble_rect.left(), triangle_center + 10)
        triangle_path << QPoint(bubble_rect.left() - 10, triangle_center)

        # Set the painter properties
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 255))

        # Draw the bubble and triangle
        painter.drawPath(bubble_path.simplified())
        painter.drawPolygon(triangle_path)


class WarningDialog(QMessageBox):
    """
    Crea un widget simple con un ícono de advertencia.
    """
    def __init__(self, parent, body, error):
        super().__init__(parent)

        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.setWindowTitle('Atención')
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(QMessageBox.Ok)
        self.setText(body)
        self.setDetailedText(error)

        self.exec()
