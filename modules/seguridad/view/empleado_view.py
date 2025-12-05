## Vista para gestión de empleados

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QAbstractItemView,
                             QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from shared.styles import TITULO, TablaNoEditableCSS
from modules.seguridad.services.empleado_service import EmpleadoService
from core.config import *
from modules.productos.view.inventario_view import TablaNoEditable

class EmpleadosWidget(QWidget):
    def __init__(self, usuario_rol='empleado'):
        super().__init__()
        self.empleado_service = EmpleadoService()  # Usar Service en vez de Model
        self.usuario_rol = usuario_rol
        self.init_ui()
        self.cargar_empleados()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Gestión de Empleados")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITULO)
        layout.addWidget(titulo)
        
        # Botón para crear empleado (solo para admin)
        if self.usuario_rol and 'admin' in self.usuario_rol.lower():
            btn_crear = QPushButton("Crear Empleado")
            btn_crear.setStyleSheet(f"""
                QPushButton {{
                    background-color: {THEME_COLOR};
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    margin-bottom: 15px;
                }}
                QPushButton:hover {{
                    background-color: {THEME_COLOR_HOVER};
                }}
            """)
            btn_crear.clicked.connect(self.crear_empleado)
            layout.addWidget(btn_crear)
        
        # Tabla de empleados
        self.tabla_empleados = TablaNoEditable()
        self.tabla_empleados.setStyleSheet(TablaNoEditableCSS)
        # Configurar columnas
        columnas_empleados = ["ID", "Nombre", "Apellido", "Usuario", "Rol", "Activo", "Acciones"]
        self.tabla_empleados.setColumnCount(len(columnas_empleados))
        self.tabla_empleados.setHorizontalHeaderLabels(columnas_empleados)
        
        # Configurar Selección - igual que inventario_view.py
        self.tabla_empleados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_empleados.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_empleados.setAlternatingRowColors(True)
        self.tabla_empleados.setFocusPolicy(Qt.NoFocus)

        # Ajustar anchos de columnas
        header = self.tabla_empleados.horizontalHeader()
        header.setStretchLastSection(True)
        anchos = [50, 150, 220, 200, 200, 120, 280]  # Anchos de columnas
        for i, ancho in enumerate(anchos):
            self.tabla_empleados.setColumnWidth(i, ancho)
        
        layout.addWidget(self.tabla_empleados)
    
    def cargar_empleados(self):
        try:
            empleados = self.empleado_service.obtener_todos_empleados()
            self.tabla_empleados.setRowCount(len(empleados))
            
            for row, empleado in enumerate(empleados):
                # ID
                self.tabla_empleados.setItem(row, 0, QTableWidgetItem(str(empleado['id_empleado'])))
                # Nombre
                self.tabla_empleados.setItem(row, 1, QTableWidgetItem(empleado['nombre_empleado']))
                # Apellido
                self.tabla_empleados.setItem(row, 2, QTableWidgetItem(empleado['apellido_empleado']))
                # Usuario
                username = empleado.get('username', 'Sin usuario')
                self.tabla_empleados.setItem(row, 3, QTableWidgetItem(username))
                # Rol
                rol_nombre = empleado.get('nombre_rol', 'Sin rol')
                rol_item = QTableWidgetItem(rol_nombre.title())
                if 'admin' in rol_nombre.lower():
                    rol_item.setForeground(Qt.red)
                    rol_item.setFont(QFont("Arial", 9, QFont.Bold))
                else:
                    rol_item.setForeground(Qt.darkGreen)
                    rol_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.tabla_empleados.setItem(row, 4, rol_item)
                
                # Estado
                estado_activo = empleado['estado_empleado'] == 'activo'
                estado_item = QTableWidgetItem("Activo" if estado_activo else "Inactivo")
                if estado_activo:
                    estado_item.setForeground(Qt.darkGreen)
                    estado_item.setFont(QFont("Arial", 9, QFont.Bold))
                else:
                    estado_item.setForeground(Qt.red)
                    estado_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.tabla_empleados.setItem(row, 5, estado_item)
                
                # Botones de acción
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(5, 2, 5, 2)
                btn_layout.setSpacing(5)
                
                # Botón Editar
                btn_editar = QPushButton("Editar")
                btn_editar.setToolTip("Editar empleado")
                btn_editar.setFixedHeight(20)
                btn_editar.setMinimumWidth(80)
                btn_editar.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                """)
                btn_editar.clicked.connect(lambda checked, emp_id=empleado['id_empleado']: self.editar_empleado(emp_id))

                # Botón Cambiar Contraseña
                btn_password = QPushButton("Contraseña")
                btn_password.setToolTip("Cambiar contraseña")
                btn_password.setFixedHeight(20)
                btn_password.setMinimumWidth(100)
                btn_password.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                btn_password.clicked.connect(lambda checked, emp_id=empleado['id_empleado']: self.cambiar_contraseña(emp_id))
                
                # Boton Activar/Desactivar segun estado
                if empleado.get("username") != "admin":
                    if empleado['estado_empleado'] == 'activo':
                        btn_estado = QPushButton("Desactivar")
                        btn_estado.setToolTip("Desactivar empleado")
                        btn_estado.setStyleSheet("""
                            QPushButton {
                                background-color: #e74c3c;
                                color: white;
                                border: none;
                                padding: 4px 8px;
                                border-radius: 4px;
                                font-weight: bold;
                                font-size: 12px;
                            }
                            QPushButton:hover {
                                background-color: #c0392b;
                            }
                        """)
                        btn_estado.clicked.connect(lambda checked, emp_id=empleado['id_empleado']: self.desactivar_empleado(emp_id))
                    else:
                        btn_estado = QPushButton("Activar")
                        btn_estado.setToolTip("Activar empleado")
                        btn_estado.setStyleSheet("""
                            QPushButton {
                                background-color: #27ae60;
                                color: white;
                                border: none;
                                padding: 4px 8px;
                                border-radius: 4px;
                                font-weight: bold;
                                font-size: 12px;
                            }
                            QPushButton:hover {
                                background-color: #219150;
                            }
                        """)
                        btn_estado.clicked.connect(lambda checked, emp_id=empleado['id_empleado']: self.activar_empleado(emp_id))
                
                    btn_estado.setFixedHeight(20)
                    btn_estado.setMinimumWidth(90)
                else:
                    btn_estado = QLabel("") 
                btn_layout.addWidget(btn_editar)
                btn_layout.addWidget(btn_password)
                btn_layout.addWidget(btn_estado)
                
                # Boton Eliminar solo si NO es admin
                if empleado['id_empleado'] != 1:
                    btn_eliminar = QPushButton("Eliminar")
                    btn_eliminar.setToolTip("Eliminar empleado")
                    btn_eliminar.setFixedHeight(20)
                    btn_eliminar.setMinimumWidth(80)
                    btn_eliminar.setStyleSheet("""
                        QPushButton {
                            background-color: #c0392b;
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #922b21;
                        }
                    """)
                    btn_eliminar.clicked.connect(lambda checked, emp_id=empleado['id_empleado']: self.eliminar_empleado(emp_id))
                    btn_layout.addWidget(btn_eliminar)
                
                btn_layout.addStretch()
                
                self.tabla_empleados.setCellWidget(row, 6, btn_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar empleados: {str(e)}")

    def crear_empleado(self):
        dialog = CrearEmpleadoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.cargar_empleados()
    
    def editar_empleado(self, empleado_id):
        try:
            empleado = self.empleado_service.obtener_empleado_por_id(empleado_id)
            if empleado:
                dialog = CrearEmpleadoDialog(self, empleado)
                if dialog.exec_() == QDialog.Accepted:
                    self.cargar_empleados()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al editar empleado: {str(e)}")
    
    def desactivar_empleado(self, empleado_id):
        try:
            reply = QMessageBox.question(
                self, 
                "Confirmar", 
                "¿Está seguro de que desea desactivar este empleado?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, mensaje = self.empleado_service.desactivar_empleado(empleado_id)
                if success:
                    QMessageBox.information(self, "Éxito", mensaje)
                    self.cargar_empleados()
                else:
                    QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al desactivar empleado: {str(e)}")
    
    def activar_empleado(self, empleado_id):
        try:
            reply = QMessageBox.question(
                self, 
                "Confirmar", 
                "¿Está seguro de que desea activar este empleado?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, mensaje = self.empleado_service.activar_empleado(empleado_id)
                if success:
                    QMessageBox.information(self, "Éxito", mensaje)
                    self.cargar_empleados()
                else:
                    QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al activar empleado: {str(e)}")
    
    def eliminar_empleado(self, empleado_id):
        try:
            if empleado_id == 1:
                QMessageBox.warning(self, "Error", "No se puede eliminar al administrador principal.")
                return
            
            reply = QMessageBox.question(
                self, 
                "Confirmar Eliminacion", 
                "¿Está SEGURO de que desea ELIMINAR permanentemente este empleado?\nEsta accion NO se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, mensaje = self.empleado_service.eliminar_empleado_permanente(empleado_id)
                if success:
                    QMessageBox.information(self, "Exito", mensaje)
                    self.cargar_empleados()
                else:
                    QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar empleado: {str(e)}")

    def cambiar_contraseña(self, empleado_id):
        try:
            empleado = self.empleado_service.obtener_empleado_por_id(empleado_id)
            if empleado:
                dialog = CambiarContrasenaDialog(self, empleado)
                if dialog.exec_() == QDialog.Accepted:
                    QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar contraseña: {str(e)}")


class CambiarContrasenaDialog(QDialog):
    def __init__(self, parent=None, empleado=None):
        super().__init__(parent)
        self.empleado = empleado
        self.empleado_service = EmpleadoService()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Cambiar Contraseña")
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        titulo = QLabel("🔑 Cambiar Contraseña")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(titulo)
        
        # Información del empleado - Simplificado sin mostrar nombres con caracteres especiales
        usuario = self.empleado.get('username', 'N/A')
        info_text = "Usuario: " + str(usuario) + "\n(Haga click en Cambiar para continuar)"
        
        info_empleado = QLabel(info_text)
        info_empleado.setAlignment(Qt.AlignCenter)
        info_empleado.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 15px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(info_empleado)
        
        # Campo nueva contraseña
        password_layout = QHBoxLayout()
        password_label = QLabel("Nueva Contraseña:")
        password_label.setFixedWidth(120)
        password_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                font-size: 14px;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Campo confirmar contraseña
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("Confirmar:")
        confirm_label.setFixedWidth(120)
        confirm_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                font-size: 14px;
            }
        """)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_guardar = QPushButton("Cambiar")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_guardar.clicked.connect(self.cambiar_contraseña)
        
        button_layout.addWidget(btn_cancelar)
        button_layout.addWidget(btn_guardar)
        layout.addLayout(button_layout)
        
        # Focus en el primer campo
        self.password_input.setFocus()
    
    def cambiar_contraseña(self):
        nueva_password = self.password_input.text().strip()
        confirmar_password = self.confirm_input.text().strip()
        
        # Validaciones
        if not nueva_password:
            QMessageBox.warning(self, "Error", "La contraseña no puede estar vacía.")
            return
        
        if len(nueva_password) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres.")
            return
        
        if nueva_password != confirmar_password:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return
        
        try:
            # Actualizar contraseña en la base de datos usando service
            success, mensaje = self.empleado_service.actualizar_usuario(
                self.empleado['id_empleado'], 
                password=nueva_password
            )
            if success:
                QMessageBox.information(self, "Éxito", mensaje)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar contraseña: {str(e)}")


class CrearEmpleadoDialog(QDialog):
    def __init__(self, parent=None, empleado_data=None):
        super().__init__(parent)
        self.empleado_service = EmpleadoService()
        self.empleado_data = empleado_data
        self.es_edicion = empleado_data is not None
        
        self.setWindowTitle("Editar Empleado" if self.es_edicion else "Crear Nuevo Empleado")
        self.setModal(True)
        self.setFixedSize(520, 450)
        
        self.crear_interfaz()
        
        if self.es_edicion:
            self.cargar_datos_empleado()
    
    def crear_interfaz(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        titulo = "Modificar Empleado" if self.es_edicion else "Registrar Empleado"
        titulo_label = QLabel(titulo)
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(titulo_label)
        
        # Campos de entrada
        campos = [("Nombre", ""), ("Apellido", ""), ("Usuario", ""), ("Contraseña", "")]
        self.entries = {}
        
        for label, default in campos:
            campo_layout = QHBoxLayout()
            
            # Label
            label_widget = QLabel(f"{label}:")
            label_widget.setFixedWidth(100)
            label_widget.setStyleSheet(self.get_label_style())
            
            # Input
            if label == "Contraseña":
                input_widget = QLineEdit()
                input_widget.setEchoMode(QLineEdit.Password)
            else:
                input_widget = QLineEdit()
            
            input_widget.setStyleSheet(self.get_input_style())
            input_widget.setText(default)
            
            self.entries[label] = input_widget
            
            campo_layout.addWidget(label_widget)
            campo_layout.addWidget(input_widget)
            layout.addLayout(campo_layout)
        
        # Campo de rol
        rol_layout = QHBoxLayout()
        rol_label = QLabel("Rol:")
        rol_label.setFixedWidth(100)
        rol_label.setStyleSheet(self.get_label_style())
        
        self.rol_combo = QComboBox()
        # Cargar roles desde la base de datos
        roles = self.empleado_service.obtener_roles_disponibles()
        for rol in roles:
            self.rol_combo.addItem(rol['nombre_rol'], rol['id_rol'])
        self.rol_combo.setStyleSheet(self.get_input_style())
        
        rol_layout.addWidget(rol_label)
        rol_layout.addWidget(self.rol_combo)
        layout.addLayout(rol_layout)
        
        # Guardar referencia al campo de contraseña
        self.password_input = self.entries["Contraseña"]
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_guardar = QPushButton("Actualizar" if self.es_edicion else "Crear")
        btn_guardar.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLOR_HOVER};
            }}
        """)
        btn_guardar.clicked.connect(self.guardar_empleado)
        
        button_layout.addWidget(btn_cancelar)
        button_layout.addWidget(btn_guardar)
        layout.addLayout(button_layout)
    
    def get_input_style(self):
        return """
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4285F4;
            }
        """
    
    def get_label_style(self):
        return """
            QLabel {
                font-weight: bold;
                color: #333;
                font-size: 14px;
            }
        """
    
    def cargar_datos_empleado(self):
        if self.empleado_data:
            self.entries["Nombre"].setText(self.empleado_data.get('nombre_empleado', ''))
            self.entries["Apellido"].setText(self.empleado_data.get('apellido_empleado', ''))
            self.entries["Usuario"].setText(self.empleado_data.get('username', ''))
            self.password_input.setText("")  # No mostrar contraseña por seguridad
            
            # Configurar rol
            id_rol_actual = self.empleado_data.get('id_rol')
            if id_rol_actual:
                for i in range(self.rol_combo.count()):
                    if self.rol_combo.itemData(i) == id_rol_actual:
                        self.rol_combo.setCurrentIndex(i)
                        break
    
    def validar_datos(self):
        from core.database import db
        
        # Validar campos obligatorios
        for campo, entry in self.entries.items():
            if not entry.text().strip():
                if campo == "Contraseña" and self.es_edicion:
                    continue  # En edición, la contraseña es opcional
                QMessageBox.warning(self, "Error", f"El campo {campo} es obligatorio.")
                entry.setFocus()
                return False
        
        # Validar usuario único
        username = self.entries["Usuario"].text().strip()
        query = "SELECT id_usuario FROM usuarios WHERE usuario = ?"
        params = [username]
        
        if self.es_edicion:
            # Excluir el usuario actual de la búsqueda
            query += " AND id_empleado != ?"
            params.append(self.empleado_data['id_empleado'])
        
        usuario_existente = db.fetchone(query, tuple(params))
        if usuario_existente:
            QMessageBox.warning(
                self, 
                "Usuario Duplicado", 
                f"El nombre de usuario '{username}' ya está en uso.\nPor favor, elige otro nombre de usuario."
            )
            self.entries["Usuario"].setFocus()
            return False
        
        # Validar contraseña solo si es nuevo empleado o se está cambiando
        password = self.password_input.text().strip()
        if not self.es_edicion and not password:
            QMessageBox.warning(self, "Error", "La contraseña es obligatoria para nuevos usuarios.")
            self.password_input.setFocus()
            return False
        
        # Si hay contraseña, validar longitud
        if password and len(password) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres.")
            self.password_input.setFocus()
            return False
        
        return True
    
    def guardar_empleado(self):
        if not self.validar_datos():
            return
        
        try:
            nombre = self.entries["Nombre"].text().strip()
            apellido = self.entries["Apellido"].text().strip()
            username = self.entries["Usuario"].text().strip()
            password = self.password_input.text().strip()
            id_rol = self.rol_combo.currentData()
            
            if self.es_edicion:
                # Actualizar datos del empleado
                success_emp, mensaje_emp = self.empleado_service.actualizar_empleado(
                    self.empleado_data['id_empleado'],
                    nombre=nombre,
                    apellido=apellido,
                    id_rol=id_rol
                )
                
                # Actualizar credenciales si se cambió usuario o contraseña
                if success_emp and (username != self.empleado_data.get('username') or password):
                    success_usr, mensaje_usr = self.empleado_service.actualizar_usuario(
                        self.empleado_data['id_empleado'],
                        username=username if username != self.empleado_data.get('username') else None,
                        password=password if password else None
                    )
                    if not success_usr:
                        QMessageBox.warning(self, "Advertencia", f"Empleado actualizado pero: {mensaje_usr}")
                
                if success_emp:
                    QMessageBox.information(self, "Éxito", mensaje_emp)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", mensaje_emp)
            else:
                # Crear nuevo empleado con usuario
                success, empleado_id, mensaje = self.empleado_service.crear_empleado_con_usuario(
                    nombre, apellido, username, password, id_rol
                )
                
                if success:
                    QMessageBox.information(self, "Éxito", mensaje)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", mensaje)
                    
        except ValueError as ve:
            QMessageBox.warning(self, "Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")