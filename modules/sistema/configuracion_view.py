## Vista para gestión de configuraciones del sistema

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QMessageBox, QGroupBox,
                             QFormLayout, QScrollArea, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt
from modules.sistema.models.configuracion_model import ConfiguracionModel
from core.config import *

class ConfiguracionWidget(QWidget):
    def __init__(self, usuario_rol='empleado'):
        super().__init__()
        self.config_model = ConfiguracionModel()
        self.usuario_rol = usuario_rol
        self.campos = {}  # Diccionario para almacenar los widgets de entrada
        self.init_ui()
        self.cargar_configuraciones()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título
        titulo = QLabel("Configuración del Sistema")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 24px;
                font-weight: bold;
                font-family: Roboto;
                margin-bottom: 20px;
            }}
        """)
        main_layout.addWidget(titulo)

        # Verificar permisos de administrador
        if not self.usuario_rol or 'admin' not in self.usuario_rol.lower():
            mensaje = QLabel("Acceso Denegado")
            mensaje.setAlignment(Qt.AlignCenter)
            mensaje.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 18px;
                    font-weight: bold;
                    margin: 50px;
                }
            """)
            main_layout.addWidget(mensaje)

            descripcion = QLabel("Solo los administradores pueden acceder a esta sección")
            descripcion.setAlignment(Qt.AlignCenter)
            descripcion.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-size: 14px;
                }
            """)
            main_layout.addWidget(descripcion)
            return

        # Crear área scrollable para los grupos de configuración
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)

        # Crear grupos de configuración
        self.crear_grupo_empresa(scroll_layout)
        self.crear_grupo_ventas(scroll_layout)
        self.crear_grupo_inventario(scroll_layout)
        self.crear_grupo_sistema(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        btn_guardar.clicked.connect(self.guardar_configuraciones)

        btn_recargar = QPushButton("Recargar")
        btn_recargar.setStyleSheet(f"""
            QPushButton {{
                background-color: {INFO_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        btn_recargar.clicked.connect(self.cargar_configuraciones)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_recargar)
        botones_layout.addWidget(btn_guardar)

        main_layout.addLayout(botones_layout)

    def crear_grupo(self, layout_padre, titulo, configs):
        """Crea un grupo de configuraciones con estilo consistente"""
        group_box = QGroupBox(titulo)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {THEME_COLOR};
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)

        for config in configs:
            clave = config['clave']
            descripcion = config['descripcion']

            # Crear widget de entrada según el tipo
            if clave == 'igv':
                widget = QSpinBox()
                widget.setRange(0, 100)
                widget.setSuffix("%")
            elif clave in ['stock_minimo_global', 'dias_alerta_vencimiento', 'dias_retencion_auditoria', 'tiempo_sesion']:
                widget = QSpinBox()
                widget.setRange(0, 9999)
                if 'dias' in clave or 'tiempo' in clave:
                    widget.setSuffix(" días" if 'dias' in clave else " min")
            elif clave == 'moneda':
                widget = QComboBox()
                widget.addItems(['PEN', 'USD', 'EUR'])
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(f"Ingrese {descripcion.lower()}")

            # Estilo común para todos los widgets
            widget.setStyleSheet("""
                QLineEdit, QSpinBox, QComboBox {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 13px;
                    background-color: white;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border: 2px solid #3498db;
                }
            """)

            self.campos[clave] = widget

            label = QLabel(descripcion + ":")
            label.setStyleSheet("font-weight: normal; color: #2c3e50;")
            form_layout.addRow(label, widget)

        group_box.setLayout(form_layout)
        layout_padre.addWidget(group_box)

    def crear_grupo_empresa(self, layout):
        """Crea el grupo de datos de la empresa"""
        configs = [
            {'clave': 'nombre_empresa', 'descripcion': 'Nombre de la Empresa'},
            {'clave': 'ruc_empresa', 'descripcion': 'RUC'},
            {'clave': 'direccion_empresa', 'descripcion': 'Dirección'},
            {'clave': 'telefono_empresa', 'descripcion': 'Teléfono'},
            {'clave': 'email_empresa', 'descripcion': 'Email'}
        ]
        self.crear_grupo(layout, "Datos de la Empresa", configs)

    def crear_grupo_ventas(self, layout):
        """Crea el grupo de configuración de ventas"""
        configs = [
            {'clave': 'igv', 'descripcion': 'IGV (%)'},
            {'clave': 'moneda', 'descripcion': 'Moneda'},
            {'clave': 'serie_boleta', 'descripcion': 'Serie Boleta'},
            {'clave': 'serie_factura', 'descripcion': 'Serie Factura'}
        ]
        self.crear_grupo(layout, "Configuración de Ventas", configs)

    def crear_grupo_inventario(self, layout):
        """Crea el grupo de configuración de inventario"""
        configs = [
            {'clave': 'stock_minimo_global', 'descripcion': 'Stock Mínimo Global'},
            {'clave': 'dias_alerta_vencimiento', 'descripcion': 'Días para Alerta de Vencimiento'}
        ]
        self.crear_grupo(layout, "Configuración de Inventario", configs)

    def crear_grupo_sistema(self, layout):
        """Crea el grupo de configuración del sistema"""
        configs = [
            {'clave': 'ruta_backups', 'descripcion': 'Ruta de Backups'},
            {'clave': 'dias_retencion_auditoria', 'descripcion': 'Días de Retención de Auditoría'},
            {'clave': 'tiempo_sesion', 'descripcion': 'Tiempo de Sesión (minutos)'}
        ]
        self.crear_grupo(layout, "Configuración del Sistema", configs)

    def cargar_configuraciones(self):
        """Carga las configuraciones desde la base de datos"""
        try:
            configs = self.config_model.obtener_todas_configuraciones()

            for config in configs:
                clave = config['clave']
                valor = config['valor']

                if clave in self.campos:
                    widget = self.campos[clave]

                    if isinstance(widget, QLineEdit):
                        widget.setText(valor)
                    elif isinstance(widget, QSpinBox):
                        widget.setValue(int(valor))
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(valor)
                        if index >= 0:
                            widget.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar configuraciones: {str(e)}")

    def guardar_configuraciones(self):
        """Guarda las configuraciones en la base de datos"""
        try:
            # Validaciones básicas
            if 'nombre_empresa' in self.campos and not self.campos['nombre_empresa'].text().strip():
                QMessageBox.warning(self, "Advertencia", "El nombre de la empresa es obligatorio")
                return

            if 'ruc_empresa' in self.campos:
                ruc = self.campos['ruc_empresa'].text().strip()
                if ruc and len(ruc) != 11:
                    QMessageBox.warning(self, "Advertencia", "El RUC debe tener 11 dígitos")
                    return

            # Guardar cada configuración
            for clave, widget in self.campos.items():
                if isinstance(widget, QLineEdit):
                    valor = widget.text().strip()
                elif isinstance(widget, QSpinBox):
                    valor = str(widget.value())
                elif isinstance(widget, QComboBox):
                    valor = widget.currentText()
                else:
                    continue

                # Verificar si la configuración existe
                config_actual = self.config_model.obtener_configuracion(clave)

                if config_actual is not None:
                    # Actualizar configuración existente
                    self.config_model.actualizar_configuracion(clave, valor)
                else:
                    # Crear nueva configuración
                    descripcion = self.obtener_descripcion_campo(clave)
                    self.config_model.crear_configuracion(clave, valor, descripcion)

            QMessageBox.information(self, "Éxito", "Configuraciones guardadas correctamente")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar configuraciones: {str(e)}")

    def obtener_descripcion_campo(self, clave):
        """Obtiene la descripción de un campo basándose en su clave"""
        descripciones = {
            'nombre_empresa': 'Nombre de la Empresa',
            'ruc_empresa': 'RUC de la empresa',
            'direccion_empresa': 'Dirección de la empresa',
            'telefono_empresa': 'Teléfono de la empresa',
            'email_empresa': 'Email de la empresa',
            'igv': 'Porcentaje de IGV',
            'moneda': 'Moneda utilizada',
            'serie_boleta': 'Serie para boletas',
            'serie_factura': 'Serie para facturas',
            'stock_minimo_global': 'Stock mínimo por defecto',
            'dias_alerta_vencimiento': 'Días para alertar vencimiento',
            'ruta_backups': 'Ruta para almacenar backups',
            'dias_retencion_auditoria': 'Días de retención de auditoría',
            'tiempo_sesion': 'Tiempo de sesión en minutos'
        }
        return descripciones.get(clave, clave)

