## Diálogo para captura de datos del cliente y generación de comprobantes

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QComboBox, QGroupBox, QRadioButton, QButtonGroup,
                             QMessageBox)
from PyQt5.QtCore import Qt
from core.config import THEME_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR
from shared.helpers import validar_dni, validar_ruc

# → Diálogo para captura de datos del cliente y generación de comprobantes
class DialogoComprobante(QDialog):
    
    def __init__(self, parent=None, comprobante_service=None):
        super().__init__(parent)
        self.comprobante_service = comprobante_service
        self.datos_cliente = None
        self.metodo_pago = 'efectivo'
        self.datos_pago_tarjeta = None
        self.setWindowTitle("Generar Comprobante")
        self.setModal(True)
        self.setFixedSize(500, 485)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Título
        titulo = QLabel("Generación de Comprobante")
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }}
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Sección: Tipo de Cliente
        grupo_cliente = QGroupBox("Datos del Cliente")
        grupo_cliente.setStyleSheet("""
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
                padding: 0 5px 0 5px;
            }
        """)
        
        cliente_layout = QVBoxLayout()
        
        # Opciones de tipo de cliente
        tipo_layout = QHBoxLayout()
        self.btn_group_tipo = QButtonGroup()
        
        self.rb_generico = QRadioButton("Cliente Genérico")
        self.rb_dni = QRadioButton("DNI")
        self.rb_ruc = QRadioButton("RUC")
        
        self.rb_generico.setChecked(True)
        
        self.btn_group_tipo.addButton(self.rb_generico, 0)
        self.btn_group_tipo.addButton(self.rb_dni, 1)
        self.btn_group_tipo.addButton(self.rb_ruc, 2)
        
        tipo_layout.addWidget(self.rb_generico)
        tipo_layout.addWidget(self.rb_dni)
        tipo_layout.addWidget(self.rb_ruc)
        cliente_layout.addLayout(tipo_layout)
        
        # Campo de número de documento
        doc_layout = QHBoxLayout()
        self.num_doc_input = QLineEdit()
        self.num_doc_input.setPlaceholderText("Ingrese DNI o RUC...")
        self.num_doc_input.setEnabled(False)
        self.num_doc_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:disabled {
                background-color: #f0f0f0;
            }
        """)
        
        self.btn_consultar = QPushButton("Consultar")
        self.btn_consultar.setEnabled(False)
        self.btn_consultar.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
            }}
        """)
        self.btn_consultar.clicked.connect(self.consultarDocumento)
        
        doc_layout.addWidget(self.num_doc_input, 3)
        doc_layout.addWidget(self.btn_consultar, 1)
        cliente_layout.addLayout(doc_layout)
        
        # Label de resultado
        self.resultado_label = QLabel("")
        self.resultado_label.setWordWrap(True)
        self.resultado_label.setStyleSheet("padding: 5px; font-size: 12px;")
        cliente_layout.addWidget(self.resultado_label)
        
        grupo_cliente.setLayout(cliente_layout)
        layout.addWidget(grupo_cliente)
        
        # Conectar señales de radio buttons
        self.rb_generico.toggled.connect(self.tipoClienteCambiado)
        self.rb_dni.toggled.connect(self.tipoClienteCambiado)
        self.rb_ruc.toggled.connect(self.tipoClienteCambiado)
        
        # Sección: Método de Pago
        grupo_pago = QGroupBox("Método de Pago")
        grupo_pago.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        pago_layout = QVBoxLayout()
        
        self.btn_group_pago = QButtonGroup()
        
        self.rb_efectivo = QRadioButton("Efectivo")
        self.rb_tarjeta = QRadioButton("Tarjeta (Culqi)")
        self.rb_yape = QRadioButton("Yape")
        self.rb_plin = QRadioButton("Plin")
        self.rb_transferencia = QRadioButton("Transferencia")
        
        self.rb_efectivo.setChecked(True)
        
        self.btn_group_pago.addButton(self.rb_efectivo, 0)
        self.btn_group_pago.addButton(self.rb_tarjeta, 1)
        self.btn_group_pago.addButton(self.rb_yape, 2)
        self.btn_group_pago.addButton(self.rb_plin, 3)
        self.btn_group_pago.addButton(self.rb_transferencia, 4)
        
        pago_layout.addWidget(self.rb_efectivo)
        pago_layout.addWidget(self.rb_tarjeta)
        pago_layout.addWidget(self.rb_yape)
        pago_layout.addWidget(self.rb_plin)
        pago_layout.addWidget(self.rb_transferencia)
        
        grupo_pago.setLayout(pago_layout)
        layout.addWidget(grupo_pago)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {ERROR_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_generar = QPushButton("✓ Generar Comprobante")
        self.btn_generar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        self.btn_generar.clicked.connect(self.generarComprobante)
        
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addWidget(self.btn_generar)
        
        layout.addLayout(botones_layout)
    
# → Habilitada o Deshabilita campos según el tipo de cliente seleccionado
    def tipoClienteCambiado(self):
        if self.rb_generico.isChecked():
            self.num_doc_input.setEnabled(False)
            self.btn_consultar.setEnabled(False)
            self.num_doc_input.clear()
            self.resultado_label.clear()
            self.datos_cliente = {
                'tipo': 'boleta',
                'num_documento': '00000000',
                'nombre_completo': 'Cliente Genérico'
            }
        else:
            self.num_doc_input.setEnabled(True)
            self.btn_consultar.setEnabled(True)
            self.num_doc_input.clear()
            self.resultado_label.clear()
            self.datos_cliente = None
            
            if self.rb_dni.isChecked():
                self.num_doc_input.setPlaceholderText("Ingrese DNI (8 dígitos)...")
                self.num_doc_input.setMaxLength(8)
            else:  # RUC
                self.num_doc_input.setPlaceholderText("Ingrese RUC (11 dígitos)...")
                self.num_doc_input.setMaxLength(11)

# → Consulta DNI o RUC usando la API
    def consultarDocumento(self):
        if not self.comprobante_service:
            QMessageBox.warning(self, "Error", "API no configurada")
            return
        
        tipo = 'DNI' if self.rb_dni.isChecked() else 'RUC'
        numero = self.num_doc_input.text().strip()
        
        # Validar
        if tipo == 'DNI':
            valido, mensaje = validar_dni(numero)
        else:
            valido, mensaje = validar_ruc(numero)
        
        if not valido:
            self.resultado_label.setText(f"{mensaje}")
            self.resultado_label.setStyleSheet(
                "background-color: #fadbd8; color: #e74c3c; padding: 8px; border-radius: 4px; font-size: 12px;"
            )
            return
        
        # Consultar API
        self.resultado_label.setText("Consultando...")
        self.resultado_label.setStyleSheet(
            "background-color: #d6eaf8; color: #2980b9; padding: 8px; border-radius: 4px; font-size: 12px;"
        )
        self.btn_consultar.setEnabled(False)
        
        try:
            resultado = self.comprobante_service.obtener_datos_documento(numero, tipo)
            
            if resultado.get('success'):
                origen = resultado.get('origen', 'api')
                cache_info = " (Cache)" if origen == 'cache' else ""
                
                if tipo == 'DNI':
                    nombre = resultado.get('nombre_completo', '')
                    self.resultado_label.setText(f"✓ {nombre}{cache_info}")
                    self.datos_cliente = {
                        'tipo': 'boleta',
                        'num_documento': numero,
                        'nombre_completo': nombre
                    }
                else:  # RUC
                    razon = resultado.get('razon_social', '')
                    direccion = resultado.get('direccion', '')
                    self.resultado_label.setText(f"✓ {razon}{cache_info}")
                    self.datos_cliente = {
                        'tipo': 'factura',
                        'ruc': numero,
                        'razon_social': razon,
                        'direccion': direccion
                    }
                
                self.resultado_label.setStyleSheet(
                    "background-color: #d5f4e6; color: #27ae60; padding: 8px; border-radius: 4px; font-size: 12px;"
                )
            else:
                error = resultado.get('error', 'Error desconocido')
                self.resultado_label.setText(f"❌ {error}")
                self.resultado_label.setStyleSheet(
                    "background-color: #fadbd8; color: #e74c3c; padding: 8px; border-radius: 4px; font-size: 12px;"
                )
                self.datos_cliente = None
        except Exception as e:
            self.resultado_label.setText(f"❌ Error: {str(e)}")
            self.resultado_label.setStyleSheet(
                "background-color: #fadbd8; color: #e74c3c; padding: 8px; border-radius: 4px; font-size: 12px;"
            )
            self.datos_cliente = None
        finally:
            self.btn_consultar.setEnabled(True)
    
# → Valida y confirma la generación del comprobante
    def generarComprobante(self):
        # Obtener método de pago seleccionado
        if self.rb_tarjeta.isChecked():
            self.metodo_pago = 'tarjeta'
        elif self.rb_yape.isChecked():
            self.metodo_pago = 'yape'
        elif self.rb_plin.isChecked():
            self.metodo_pago = 'plin'
        elif self.rb_transferencia.isChecked():
            self.metodo_pago = 'transferencia'
        else:
            self.metodo_pago = 'efectivo'
        
        # Si es pago con tarjeta, procesar primero el pago
        if self.metodo_pago == 'tarjeta':
            if not self.procesarPagoTarjeta():
                return  # Si el pago falla o se cancela, no continuar
        
        # Si es pago con Yape o Plin, mostrar QR
        elif self.metodo_pago in ['yape', 'plin']:
            if not self.procesarPagoQR():
                return  # Si el pago se cancela, no continuar
        
        # Si es pago con transferencia, mostrar datos bancarios
        elif self.metodo_pago == 'transferencia':
            if not self.procesarPagoTransferencia():
                return  # Si el pago se cancela, no continuar
        
        # Validar que se tengan datos del cliente SOLO para DNI/RUC
        if not self.rb_generico.isChecked() and not self.datos_cliente:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Por favor consulte el documento antes de continuar"
            )
            return

        # Confirmar - determinar tipo según datos del cliente
        if self.datos_cliente:
            tipo_comp = "Boleta" if self.datos_cliente.get('tipo') == 'boleta' else "Factura"
            if tipo_comp == "Boleta":
                cliente_info = self.datos_cliente.get('nombre_completo', 'Cliente Genérico')
            else:
                cliente_info = self.datos_cliente.get('razon_social', '')
        else:
            # Fallback si no hay datos (no debería llegar aquí)
            tipo_comp = "Boleta"
            cliente_info = "Cliente Genérico"

        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Generar {tipo_comp} para:\n{cliente_info}\n\nMétodo de pago: {self.metodo_pago.upper()}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.accept()

# → Retorna los datos capturados
    def obtenerDatos(self):
        return {
            'datos_cliente': self.datos_cliente,
            'metodo_pago': self.metodo_pago,
            'datos_pago_tarjeta': self.datos_pago_tarjeta
        }
    
# → Abrir dialogo de pago con tarjeta y procesar transaccion
    def procesarPagoTarjeta(self):
        from modules.ventas.view.dialogo_pago_tarjeta import DialogoPagoTarjeta        
        # Obtener el total desde el parent (VentasFrame)
        try:
            total_venta = self.parent().total
        except:
            QMessageBox.warning(self, "Error", "No se pudo obtener el total de la venta")
            return False
        
        # Abrir dialogo de pago con tarjeta
        dialogo_tarjeta = DialogoPagoTarjeta(self, total_venta)
        
        if dialogo_tarjeta.exec_() == QDialog.Accepted:
            # Pago exitoso - guardar datos
            self.datos_pago_tarjeta = dialogo_tarjeta.get_resultado_pago()
            return True
        else:
            # Pago cancelado o fallido
            return False
    
# → Abrir dialogo de pago con Yape/Plin (QR)
    def procesarPagoQR(self):
        from modules.ventas.view.dialogo_pago_qr import DialogoPagoQR        
        # Obtener el total desde el parent (VentasFrame)
        try:
            total_venta = self.parent().total
        except:
            QMessageBox.warning(self, "Error", "No se pudo obtener el total de la venta")
            return False
        
        # Abrir dialogo de pago QR
        dialogo_qr = DialogoPagoQR(self, total_venta, self.metodo_pago)
        
        if dialogo_qr.exec_() == QDialog.Accepted:
            # Pago confirmado - guardar datos
            self.datos_pago_tarjeta = dialogo_qr.get_resultado_pago()
            return True
        else:
            # Pago cancelado
            return False
    
# → Procesar pago por transferencia bancaria, abriendo el dialogo correspondiente
    def procesarPagoTransferencia(self):
        from modules.ventas.view.dialogo_pago_transferencia import DialogoPagoTransferencia
        
        # Obtener el total desde el parent (VentasFrame)
        try:
            total_venta = self.parent().total
        except:
            QMessageBox.warning(self, "Error", "No se pudo obtener el total de la venta")
            return False
        
        # Abrir dialogo de transferencia
        dialogo_transf = DialogoPagoTransferencia(self, total_venta)
        
        if dialogo_transf.exec_() == QDialog.Accepted:
            # Pago confirmado - guardar datos
            self.datos_pago_tarjeta = dialogo_transf.get_resultado_pago()
            return True
        else:
            # Pago cancelado
            return False
            self.datos_pago_tarjeta = dialogo_tarjeta.get_resultado_pago()
