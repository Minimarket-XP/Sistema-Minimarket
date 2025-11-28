## Pantalla de logueo

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QFrame, QDialog, QComboBox, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont
from core.config import *
from PIL import Image

class LoginVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Iniciar Sesion")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setFixedSize(1024, 576)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.usuario_logueado = None
        self.crearRobotofaz(main_layout)
        self.centrarVentana()
    
    def centrarVentana(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def crearRobotofaz(self, main_layout):
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #f8f9fa;")
        left_frame.setMinimumWidth(620)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            imagen_original = Image.open("C:/Users/LENOVO LOQ/Desktop/VI - 2025 - 20/Agile Development/PROYECTO/Sistema-Minimarket-wa/temp_minimarket.jpg")
            imagen_redimensionada = imagen_original.crop((0, 0, 620, 576))
            imagen_redimensionada.save("temp_minimarket.jpg")
            
            imagen_label = QLabel()
            pixmap = QPixmap("temp_minimarket.jpg")
            if not pixmap.isNull():
                imagen_label.setPixmap(pixmap)
                imagen_label.setScaledContents(True)
            left_layout.addWidget(imagen_label)
        except:
            placeholder_label = QLabel("🏪 MINIMARKET")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("""
                QLabel {
                    background-color: #e9ecef;
                    color: #6c757d;
                    font-size: 60px;
                    font-weight: bold;
                }
            """)
            left_layout.addWidget(placeholder_label)
        
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: white;")
        right_frame.setFixedWidth(400)
        
        form_layout = QVBoxLayout(right_frame)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(50, 50, 50, 50)
        form_layout.setSpacing(20)
        
        self.crearSeccionLogo(form_layout)
        self.crearCamposFormularios(form_layout)
        
        main_layout.addWidget(left_frame, 3)
        main_layout.addWidget(right_frame, 2)
    
    def crearSeccionLogo(self, form_layout):
        try:
            logo_label = QLabel()
            logo_path = os.path.join(IMG_DIR, "LOGOT.png")
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(240, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            form_layout.addWidget(logo_label)
        except:
            logo_text = QLabel("DON MANUELITO")
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet("""
                QLabel {
                    color: #4285F4;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
            form_layout.addWidget(logo_text)
        
        titulo_label = QLabel("Iniciar sesión")
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 25px;
                font-weight: bold;
                font-family: 'Roboto';
            }
        """)
        form_layout.addWidget(titulo_label)
        
        subtitulo_label = QLabel("Acceder")
        subtitulo_label.setAlignment(Qt.AlignCenter)
        subtitulo_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16px;
                font-family: 'Roboto';
                margin-bottom: 20px;
            }
        """)
        form_layout.addWidget(subtitulo_label)
    
    def crearCamposFormularios(self, form_layout):
        usuario_label = QLabel("Nombre de usuario")
        usuario_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 18px;
                font-family: 'Roboto';
                margin-bottom: 5px;
                font-weight: bold;
            }
        """)
        form_layout.addWidget(usuario_label)
        
        self.usuario_entry = QLineEdit()
        self.usuario_entry.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Roboto';
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        self.usuario_entry.setFixedHeight(40)
        form_layout.addWidget(self.usuario_entry)
        
        password_label = QLabel("Contraseña")
        password_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 18px;
                font-family: 'Roboto';
                margin-bottom: 5px;
                font-weight: bold;
            }
        """)
        form_layout.addWidget(password_label)
        
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        self.password_entry.setFixedHeight(40)
        form_layout.addWidget(self.password_entry)
        
        login_btn = QPushButton("Iniciar sesión")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Roboto';
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
            QPushButton:pressed {
                background-color: #2B5CE6;
            }
        """)
        login_btn.setFixedHeight(45)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.LOGIN)
        form_layout.addWidget(login_btn)
        
        forgot_label = QLabel("Olvido su contraseña?")
        forgot_label.setAlignment(Qt.AlignCenter)
        forgot_label.setStyleSheet("""
            QLabel {
                color: #4285F4;
                font-size: 13px;
                text-decoration: underline;
            }
            QLabel:hover {
                color: #3367D6;
            }
        """)
        forgot_label.setCursor(Qt.PointingHandCursor)
        forgot_label.mousePressEvent = lambda event: self.recuperar_contraseña()
        form_layout.addWidget(forgot_label)
        
        self.usuario_entry.returnPressed.connect(self.password_entry.setFocus)
        self.password_entry.returnPressed.connect(self.LOGIN)
        self.usuario_entry.setFocus()
    
    def recuperar_contraseña(self):
        """Dialogo para que admin recupere contraseñas"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Recuperar Contraseña - Solo Admin")
        dialog.setModal(True)
        dialog.setFixedSize(450, 400)
        
        dialog.setStyleSheet("QDialog { background-color: white; }")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        titulo = QLabel("Recuperar Contraseña")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Roboto';
            }
        """)
        layout.addWidget(titulo)
        
        subtitulo = QLabel("Solo el administrador puede resetear contraseñas")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 13px;
                font-family: 'Roboto';
            }
        """)
        layout.addWidget(subtitulo)
        
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        admin_user_label = QLabel("Usuario Admin:")
        admin_user_label.setStyleSheet("font-weight: bold; color: #495057;")
        admin_user_input = QLineEdit()
        admin_user_input.setPlaceholderText("Ingrese usuario admin")
        admin_user_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        form_layout.addRow(admin_user_label, admin_user_input)
        
        admin_pass_label = QLabel("Contraseña Admin:")
        admin_pass_label.setStyleSheet("font-weight: bold; color: #495057;")
        admin_pass_input = QLineEdit()
        admin_pass_input.setEchoMode(QLineEdit.Password)
        admin_pass_input.setPlaceholderText("Ingrese contraseña admin")
        admin_pass_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        form_layout.addRow(admin_pass_label, admin_pass_input)
        
        empleado_label = QLabel("Empleado a resetear:")
        empleado_label.setStyleSheet("font-weight: bold; color: #495057;")
        empleado_combo = QComboBox()
        empleado_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        try:
            from modules.empleados.empleado_model import EmpleadoModel
            empleado_model = EmpleadoModel()
            empleados = empleado_model.obtenerEmpleadosActivos()
            for emp in empleados:
                empleado_combo.addItem(f"{emp['nombre']} {emp['apellido']} ({emp['usuario']})", emp['id'])
        except:
            empleado_combo.addItem("Error cargando empleados", None)
        
        form_layout.addRow(empleado_label, empleado_combo)
        
        nueva_pass_label = QLabel("Nueva Contraseña:")
        nueva_pass_label.setStyleSheet("font-weight: bold; color: #495057;")
        nueva_pass_input = QLineEdit()
        nueva_pass_input.setEchoMode(QLineEdit.Password)
        nueva_pass_input.setPlaceholderText("Nueva contraseña")
        nueva_pass_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        form_layout.addRow(nueva_pass_label, nueva_pass_input)
        
        layout.addWidget(form_container)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(dialog.reject)
        
        btn_resetear = QPushButton("Resetear Contraseña")
        btn_resetear.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        btn_resetear.setCursor(Qt.PointingHandCursor)
        
        def resetear_password():
            admin_user = admin_user_input.text().strip()
            admin_pass = admin_pass_input.text().strip()
            nueva_pass = nueva_pass_input.text().strip()
            empleado_id = empleado_combo.currentData()
            
            if not admin_user or not admin_pass:
                QMessageBox.warning(dialog, "Error", "Ingrese credenciales de admin")
                return
            
            if not self.validarCredenciales(admin_user, admin_pass):
                QMessageBox.critical(dialog, "Error", "Credenciales de admin incorrectas")
                return
            
            try:
                from modules.empleados.empleado_model import EmpleadoModel
                empleado_model = EmpleadoModel()
                empleado = empleado_model.get_by_id(empleado_id)
                
                if not empleado or empleado.get('rol') != 'administrador':
                    QMessageBox.critical(dialog, "Error", "Usuario no es administrador")
                    return
            except:
                QMessageBox.critical(dialog, "Error", "No se pudo validar rol de admin")
                return
            
            if not nueva_pass:
                QMessageBox.warning(dialog, "Error", "Ingrese nueva contraseña")
                return
            
            if len(nueva_pass) < 4:
                QMessageBox.warning(dialog, "Error", "Contrasena debe tener al menos 4 caracteres")
                return
            
            if not empleado_id:
                QMessageBox.warning(dialog, "Error", "Seleccione un empleado")
                return
            
            try:
                from modules.empleados.empleado_model import EmpleadoModel
                empleado_model = EmpleadoModel()
                
                if empleado_model.actualizarEmpleado(empleado_id, {'contrasena': nueva_pass}):
                    QMessageBox.information(dialog, "Exito", "Contrasena actualizada correctamente")
                    dialog.accept()
                else:
                    QMessageBox.critical(dialog, "Error", "No se pudo actualizar la contrasena")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Error: {str(e)}")
        
        btn_resetear.clicked.connect(resetear_password)
        
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_resetear)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def LOGIN(self):
        usuario = self.usuario_entry.text().strip()
        password = self.password_entry.text().strip()
        
        if not usuario or not password:
            QMessageBox.critical(self, "Error", "Por favor ingrese usuario y contrasena.")
            return
        
        if self.validarCredenciales(usuario, password):
            self.usuario_logueado = usuario
            self.abrirDashboard()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contrasena incorrectos.")
            self.password_entry.clear()
            self.password_entry.setFocus()
    
    def validarCredenciales(self, usuario, password):
        try:
            from modules.empleados.empleado_model import EmpleadoModel
            empleado_model = EmpleadoModel()
            return empleado_model.validar_credenciales(usuario, password)
        except Exception as e:
            print(f"Error validando credenciales: {e}")
            return usuario == "admin" and password == "admin"
    
    def abrirDashboard(self):
        self.hide()
        from shared.dashboard import Dashboard
        
        self.dashboard = Dashboard(self.usuario_logueado)
        self.dashboard.show()
    
    def volverLogin(self):
        self.show()
        self.usuario_entry.clear()
        self.password_entry.clear()
        self.usuario_entry.setFocus()
    
    def closeEvent(self, event):
        QApplication.quit()
        event.accept()