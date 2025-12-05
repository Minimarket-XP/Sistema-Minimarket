"""Dialogo para procesar pagos con tarjeta mediante Culqi"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QGroupBox, QMessageBox, QProgressDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from PyQt5.QtCore import QRegExp
from core.config import THEME_COLOR, SUCCESS_COLOR, ERROR_COLOR
from modules.ventas.service.culqi_service import CulqiService
from shared.helpers import formatear_precio

# Dialogo para capturar datos de tarjeta y procesar pago con Culqi
class DialogoPagoTarjeta(QDialog):
    def __init__(self, parent=None, monto_total=0):
        super().__init__(parent)
        self.monto_total = monto_total
        self.culqi_service = CulqiService()
        self.resultado_pago = None
        
        self.setWindowTitle("Pago con Tarjeta - Culqi TEST")
        self.setModal(True)
        self.setFixedSize(500, 800)
        self.initUI()
    
# → Crear interfaz del dialogo    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Titulo
        titulo = QLabel("Pago con Tarjeta de Credito/Debito")
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
        monto_label = QLabel(f"TOTAL A PAGAR: {formatear_precio(self.monto_total)}")
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
        
        # Advertencia de modo TEST
        warning_label = QLabel("MODO TEST - Use tarjetas de prueba de Culqi")
        warning_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ERROR_COLOR};
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px;
                border-radius: 3px;
            }}
        """)
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)
        
        # Grupo: Datos de la Tarjeta
        grupo_tarjeta = QGroupBox("Datos de la Tarjeta")
        grupo_tarjeta.setStyleSheet("""
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
        tarjeta_layout = QVBoxLayout()
        
        # Numero de tarjeta
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Numero de tarjeta (16 digitos)")
        self.input_numero.setMaxLength(16)
        validator_numero = QRegExpValidator(QRegExp("[0-9]{16}"))
        self.input_numero.setValidator(validator_numero)
        tarjeta_layout.addWidget(QLabel("Numero de Tarjeta:"))
        tarjeta_layout.addWidget(self.input_numero)
        
        # CVV
        self.input_cvv = QLineEdit()
        self.input_cvv.setPlaceholderText("CVV (3 o 4 digitos)")
        self.input_cvv.setMaxLength(4)
        self.input_cvv.setEchoMode(QLineEdit.Password)
        validator_cvv = QRegExpValidator(QRegExp("[0-9]{3,4}"))
        self.input_cvv.setValidator(validator_cvv)
        tarjeta_layout.addWidget(QLabel("CVV:"))
        tarjeta_layout.addWidget(self.input_cvv)
        
        # Fecha de expiracion
        exp_layout = QHBoxLayout()
        
        self.input_mes = QLineEdit()
        self.input_mes.setPlaceholderText("MM")
        self.input_mes.setMaxLength(2)
        validator_mes = QIntValidator(1, 12)
        self.input_mes.setValidator(validator_mes)
        
        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("YYYY")
        self.input_anio.setMaxLength(4)
        validator_anio = QIntValidator(2024, 2050)
        self.input_anio.setValidator(validator_anio)
        
        exp_layout.addWidget(self.input_mes)
        exp_layout.addWidget(QLabel("/"))
        exp_layout.addWidget(self.input_anio)
        
        tarjeta_layout.addWidget(QLabel("Fecha de Expiracion (MM/YYYY):"))
        tarjeta_layout.addLayout(exp_layout)
        
        grupo_tarjeta.setLayout(tarjeta_layout)
        layout.addWidget(grupo_tarjeta)
        
        # Grupo: Datos del Titular
        grupo_titular = QGroupBox("Datos del Titular")
        grupo_titular.setStyleSheet("""
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
        titular_layout = QVBoxLayout()
        
        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("correo@ejemplo.com")
        titular_layout.addWidget(QLabel("Email:"))
        titular_layout.addWidget(self.input_email)
        
        grupo_titular.setLayout(titular_layout)
        layout.addWidget(grupo_titular)
        
        # Informacion de tarjetas de prueba
        info_test = QLabel(
            "Tarjetas de prueba Culqi:\n"
            "• Visa exitosa: 4111111111111111\n"
            "• Mastercard exitosa: 5111111111111118\n"
            "• CVV: 123 | Exp: 09/2025"
        )
        info_test.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                font-size: 11px;
                color: #34495e;
            }
        """)
        layout.addWidget(info_test)
        
        # Botones de accion
        botones_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: #95a5a6;
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #7f8c8d;
            }}
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_procesar = QPushButton("Procesar Pago")
        self.btn_procesar.setStyleSheet(f"""
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
        self.btn_procesar.clicked.connect(self.procesarPago)
        
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addWidget(self.btn_procesar)
        
        layout.addLayout(botones_layout)
        
        # Aplicar estilos a los inputs
        input_style = """
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """
        self.input_numero.setStyleSheet(input_style)
        self.input_cvv.setStyleSheet(input_style)
        self.input_mes.setStyleSheet(input_style)
        self.input_anio.setStyleSheet(input_style)
        self.input_email.setStyleSheet(input_style)
    
# → Validar datos de la tarjeta que esten completos    
    def validar_datos(self):
        # Validar numero de tarjeta
        if len(self.input_numero.text()) != 16:
            QMessageBox.warning(self, "Datos Incompletos",
                              "El numero de tarjeta debe tener 16 digitos")
            self.input_numero.setFocus()
            return False
        
        # Validar CVV
        if len(self.input_cvv.text()) not in [3, 4]:
            QMessageBox.warning(self, "Datos Incompletos",
                              "El CVV debe tener 3 o 4 digitos")
            self.input_cvv.setFocus()
            return False
        
        # Validar mes
        if not self.input_mes.text() or not (1 <= int(self.input_mes.text()) <= 12):
            QMessageBox.warning(self, "Datos Incompletos",
                              "Ingrese un mes valido (01-12)")
            self.input_mes.setFocus()
            return False
        
        # Validar año
        if len(self.input_anio.text()) != 4 or int(self.input_anio.text()) < 2024:
            QMessageBox.warning(self, "Datos Incompletos",
                              "Ingrese un año valido (YYYY)")
            self.input_anio.setFocus()
            return False
        
        # Validar email
        email = self.input_email.text().strip()
        if not email or '@' not in email:
            QMessageBox.warning(self, "Datos Incompletos",
                              "Ingrese un email valido")
            self.input_email.setFocus()
            return False
        
        return True
    
# → Procesar el pago con Culqui    
    def procesarPago(self):
        # Validar datos
        if not self.validar_datos():
            return
        
        # Confirmar procesamiento
        respuesta = QMessageBox.question(
            self,
            "Confirmar Pago",
            f"¿Procesar pago de {formatear_precio(self.monto_total)} con tarjeta?\n\n"
            f"Tarjeta: **** **** **** {self.input_numero.text()[-4:]}\n"
            f"Email: {self.input_email.text()}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta != QMessageBox.Yes:
            return
        
        # Mostrar dialogo de progreso
        progress = QProgressDialog("Procesando pago con Culqi...", None, 0, 0, self)
        progress.setWindowTitle("Procesando")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            # Paso 1: Crear token de tarjeta
            token_resultado = self.culqi_service.crear_token_test(
                card_number=self.input_numero.text(),
                cvv=self.input_cvv.text(),
                expiration_month=self.input_mes.text().zfill(2),
                expiration_year=self.input_anio.text(),
                email=self.input_email.text().strip()
            )
            
            if not token_resultado.get('success'):
                progress.close()
                QMessageBox.critical(self, "Error en Tarjeta",
                                   token_resultado.get('mensaje', 'Error al validar tarjeta'))
                return
            
            token_id = token_resultado.get('token_id')
            
            # Paso 2: Crear cargo
            cargo_resultado = self.culqi_service.crear_cargo(
                token_id=token_id,
                monto=self.monto_total,
                email=self.input_email.text().strip(),
                descripcion=f"Venta Minimarket - {formatear_precio(self.monto_total)}"
            )
            
            progress.close()
            
            if cargo_resultado.get('success'):
                # Pago exitoso
                self.resultado_pago = cargo_resultado
                
                QMessageBox.information(
                    self,
                    "Pago Exitoso",
                    f"Transaccion aprobada\n\n"
                    f"Monto: {formatear_precio(cargo_resultado.get('amount'))}\n"
                    f"ID: {cargo_resultado.get('charge_id')}\n"
                    f"Referencia: {cargo_resultado.get('reference_code', 'N/A')}"
                )
                
                self.accept()
            else:
                # Pago rechazado
                QMessageBox.critical(
                    self,
                    "Pago Rechazado",
                    cargo_resultado.get('mensaje', 'Transaccion rechazada')
                )
        
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error",
                               f"Error al procesar pago: {str(e)}")
    
# → Obtener resultado del pago procesado
    def get_resultado_pago(self):
        return self.resultado_pago
