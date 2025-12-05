""" Dialogo para procesar pagos por Transferencia Bancaria"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QMessageBox, QLineEdit, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt
from core.config import THEME_COLOR, SUCCESS_COLOR
from shared.helpers import formatear_precio

# → Dialogo para mostrar datos bancarios y confirmar transferencia
class DialogoPagoTransferencia(QDialog):
    def __init__(self, parent=None, monto_total=0):
        super().__init__(parent)
        self.monto_total = monto_total
        self.pago_confirmado = False
        
        self.setWindowTitle("Pago por Transferencia Bancaria")
        self.setModal(True)
        self.setFixedSize(500, 800)
        self.initUI()
    
# → Crear interfaz del dialogo    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titulo
        titulo = QLabel("Pago por Transferencia Bancaria")
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
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }}
        """)
        monto_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(monto_label)
        
        # Datos bancarios
        grupo_datos = QGroupBox("Datos para Transferencia")
        grupo_datos.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        datos_layout = QVBoxLayout()
        
        # BCP
        bcp_label = QLabel(
            "BANCO BCP\n"
            "Cuenta Corriente: 194-12345678-0-99\n"
            "CCI: 002-194-001234567899-12\n"
            "Titular: Minimarket S.A.C.\n"
            "RUC: 20123456789"
        )
        bcp_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                padding: 12px;
                border-radius: 5px;
                font-size: 12px;
                font-family: 'Courier New';
            }
        """)
        datos_layout.addWidget(bcp_label)
        
        # BBVA
        bbva_label = QLabel(
            "BANCO BBVA\n"
            "Cuenta Corriente: 0011-0234-56-78901234\n"
            "CCI: 011-234-000234567890-45\n"
            "Titular: Minimarket S.A.C.\n"
            "RUC: 20123456789"
        )
        bbva_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                padding: 12px;
                border-radius: 5px;
                font-size: 12px;
                font-family: 'Courier New';
            }
        """)
        datos_layout.addWidget(bbva_label)
        
        grupo_datos.setLayout(datos_layout)
        layout.addWidget(grupo_datos)
        
        # Numero de operacion
        self.input_operacion = QLineEdit()
        self.input_operacion.setPlaceholderText("Numero de operacion (requerido)")
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
        
        # Banco origen
        self.input_banco = QLineEdit()
        self.input_banco.setPlaceholderText("Banco de origen (opcional)")
        self.input_banco.setStyleSheet("""
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
        layout.addWidget(QLabel("Banco de origen:"))
        layout.addWidget(self.input_banco)
        
        # Observaciones
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales (opcional)")
        self.input_observaciones.setMaximumHeight(80)
        self.input_observaciones.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(QLabel("Observaciones:"))
        layout.addWidget(self.input_observaciones)
        
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
    
# → Confirmar que la transferencia fue realizada
    def confirmarPago(self):
        # Validar numero de operacion
        if not self.input_operacion.text().strip():
            QMessageBox.warning(
                self,
                "Datos Incompletos",
                "Debes ingresar el numero de operacion"
            )
            self.input_operacion.setFocus()
            return
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Pago",
            f"¿Confirmas que realizaste la transferencia de {formatear_precio(self.monto_total)}?\n\n"
            f"Operacion: {self.input_operacion.text()}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.pago_confirmado = True
            QMessageBox.information(
                self,
                "Pago Confirmado",
                f"Transferencia confirmada exitosamente\n"
                f"Monto: {formatear_precio(self.monto_total)}\n"
                f"Operacion: {self.input_operacion.text()}\n"
                f"Banco: {self.input_banco.text() or 'No especificado'}"
            )
            self.accept()
    
# → Obtener resultado del pago
    def get_resultado_pago(self):
        if self.pago_confirmado:
            return {
                'success': True,
                'metodo': 'transferencia',
                'monto': self.monto_total,
                'numero_operacion': self.input_operacion.text(),
                'banco_origen': self.input_banco.text() or 'No especificado',
                'observaciones': self.input_observaciones.toPlainText() or '',
                'estado': 'confirmado'
            }
        return None
