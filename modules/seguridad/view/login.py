## Pantalla de logueo

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont
from core.config import *
from PIL import Image

class LoginVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Iniciar Sesión")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setFixedSize(1024, 576)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
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
        # LADO IZQUIERDO - Imagen del minimarket
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #f8f9fa;")
        left_frame.setMinimumWidth(620)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            # Cargar imagen con PIL y convertir para PyQt
            imagen_original = Image.open("C:/Users/LENOVO LOQ/Desktop/VI - 2025 - 20/Agile Development/PROYECTO/Sistema-Minimarket-wa/temp_minimarket.jpg")
            imagen_redimensionada = imagen_original.crop((0, 0, 620, 576))
            imagen_redimensionada.save("temp_minimarket.jpg")
            
            imagen_label = QLabel()
            pixmap = QPixmap("temp_minimarket.jpg")
            # Verificar que el pixmap no sea nulo
            if not pixmap.isNull():
                imagen_label.setPixmap(pixmap)
                imagen_label.setScaledContents(True)
            left_layout.addWidget(imagen_label)
        except:
            # Si no hay imagen, mostrar placeholder elegante
            placeholder_label = QLabel("🏪\nMINIMARKET")
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
        
        # LADO DERECHO - Formulario de login
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: white;")
        right_frame.setFixedWidth(400)
        
        # Layout del formulario
        form_layout = QVBoxLayout(right_frame)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(50, 50, 50, 50)
        form_layout.setSpacing(20)
        
        # Logo y título
        self.crearSeccionLogo(form_layout)
        
        # Campos del formulario
        self.crearCamposFormularios(form_layout)
        
        # Añadir frames al layout principal
        main_layout.addWidget(left_frame, 3)  # 60% del espacio
        main_layout.addWidget(right_frame, 2)  # 40% del espacio
    
    def crearSeccionLogo(self, form_layout):
        try:
            # Cargar logo
            logo_label = QLabel()
            logo_path = os.path.join(IMG_DIR, "LOGOT.png")
            pixmap = QPixmap(logo_path)
            # Verificar que el pixmap no sea nulo antes de escalar
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(240, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            form_layout.addWidget(logo_label)
        except:
            logo_text = QLabel("🏪 DON MANUELITO")
            logo_text.setAlignment(Qt.AlignCenter)
            logo_text.setStyleSheet("""
                QLabel {
                    color: #4285F4;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
            form_layout.addWidget(logo_text)
        
        # Título principal
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
        
        # Subtítulo
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
        # Campo Usuario
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
        
        # Campo Contraseña
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
        
        # Botón de login
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
        
        # Link olvidé contraseña
        forgot_label = QLabel("¿Olvidó su contraseña?")
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
        form_layout.addWidget(forgot_label)
        
        # Conectar Enter para navegación
        self.usuario_entry.returnPressed.connect(self.password_entry.setFocus)
        self.password_entry.returnPressed.connect(self.LOGIN)
        
        # Foco inicial
        self.usuario_entry.setFocus()
    
    def LOGIN(self):
        usuario = self.usuario_entry.text().strip()
        password = self.password_entry.text().strip()
        
        if not usuario or not password:
            QMessageBox.critical(self, "Error", "Por favor ingrese usuario y contraseña.")
            return
        
        # Validar credenciales
        if self.validarCredenciales(usuario, password):
            self.usuario_logueado = usuario
            self.abrirDashboard()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")
            self.password_entry.clear()
            self.password_entry.setFocus()
    
    def validarCredenciales(self, usuario, password):
        try:
            from modules.empleados.empleado_model import EmpleadoModel
            empleado_model = EmpleadoModel()
            return empleado_model.validar_credenciales(usuario, password)
        except Exception as e:
            print(f"Error validando credenciales: {e}")
            # Credenciales por defecto si hay error
            return usuario == "admin" and password == "admin"
    
    def abrirDashboard(self):
        self.hide()
        from shared.dashboard import Dashboard
        
        self.dashboard = Dashboard(self.usuario_logueado)
        self.dashboard.show()
        
        # No necesitamos conectar señales ya que el Dashboard cierra toda la aplicación
    
    def volverLogin(self):
        self.show()
        self.usuario_entry.clear()
        self.password_entry.clear()
        self.usuario_entry.setFocus()
    
    def closeEvent(self, event):
        # Cerrar toda la aplicación cuando se cierre el login
        QApplication.quit()
        event.accept()