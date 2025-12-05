"""
Dialogo para procesar pagos con Yape/Plin mediante QR
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.config import THEME_COLOR, SUCCESS_COLOR
from shared.helpers import formatear_precio
import qrcode
from io import BytesIO
from PIL import Image

# → Dialogo de pago con QR (Yape/Plin)
class DialogoPagoQR(QDialog):    
    def __init__(self, parent=None, monto_total=0, metodo='yape'):
        super().__init__(parent)
        self.monto_total = monto_total
        self.metodo = metodo.upper()
        self.pago_confirmado = False
        
        self.setWindowTitle(f"Pago con {self.metodo}")
        self.setModal(True)
        self.setFixedSize(450, 600)
        self.initUI()
    
# → Inicializar interfaz
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Titulo
        titulo = QLabel(f"Pago con {self.metodo}")
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Monto a pagar
        monto_label = QLabel(f"MONTO A PAGAR: {formatear_precio(self.monto_total)}")
        monto_label.setStyleSheet(f"""
            QLabel {{
                background-color: {SUCCESS_COLOR};
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        monto_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(monto_label)
        
        # Informacion del metodo
        color_metodo = '#9b26af' if self.metodo == 'YAPE' else '#00d4aa'
        info_label = QLabel(
            f"Escanea el codigo QR con tu app {self.metodo}\n"
            f"y realiza el pago de {formatear_precio(self.monto_total)}"
        )
        info_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color_metodo};
                color: white;
                font-size: 14px;
                padding: 12px;
                border-radius: 5px;
            }}
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Generar y mostrar QR
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        
        # Generar QR con datos de pago (en produccion seria el link de pago)
        qr_data = self.generar_datos_qr()
        qr_image = self.generar_qr(qr_data)
        qr_label.setPixmap(qr_image)
        
        layout.addWidget(qr_label)
        
        # Numero de operacion
        self.input_operacion = QLineEdit()
        self.input_operacion.setPlaceholderText("Numero de operacion (opcional)")
        self.input_operacion.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(QLabel("Numero de operacion:"))
        layout.addWidget(self.input_operacion)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_confirmar = QPushButton("Confirmar Pago")
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        btn_confirmar.clicked.connect(self.confirmarPago)
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_confirmar)
        
        layout.addLayout(botones_layout)
    
# → Generar datos para el codigo QR
    def generar_datos_qr(self):
        # En TEST: Generar URL de pago simulada que se puede escanear
        comercio_id = "MINIMARKET_TEST"
        monto_centavos = int(self.monto_total * 100)
        
        if self.metodo == 'YAPE':
            # URL simulada de Yape (en produccion vendria de su API)
            # Yape usa formato: yape://payment?recipient=XXX&amount=XXX&message=XXX
            return f"yape://payment?recipient={comercio_id}&amount={monto_centavos}&message=Compra+Minimarket"
        else:
            # URL simulada de Plin (en produccion vendria de su API)
            # Plin usa formato similar
            return f"plin://payment?merchant={comercio_id}&amount={monto_centavos}&description=Compra+Minimarket"
    
# → Generar imagen QR    
    def generar_qr(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a QPixmap
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        
        # Redimensionar
        return pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
# → Confirmar que el pago fue realizado    
    def confirmarPago(self):
        respuesta = QMessageBox.question(
            self,
            "Confirmar Pago",
            f"¿Confirmas que realizaste el pago de {formatear_precio(self.monto_total)} via {self.metodo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.pago_confirmado = True
            QMessageBox.information(
                self,
                "Pago Confirmado",
                f"Pago via {self.metodo} confirmado exitosamente\n"
                f"Monto: {formatear_precio(self.monto_total)}\n"
                f"Operacion: {self.input_operacion.text() or 'No especificado'}"
            )
            self.accept()
    
# → Obtener resultado del pago    
    def get_resultado_pago(self):
        if self.pago_confirmado:
            return {
                'success': True,
                'metodo': self.metodo.lower(),
                'monto': self.monto_total,
                'numero_operacion': self.input_operacion.text() or 'No especificado',
                'estado': 'confirmado'
            }
        return None
