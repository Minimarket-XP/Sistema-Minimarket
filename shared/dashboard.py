## Dashboard principal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt
from core.config import *

class Dashboard(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.usuario_rol = self.obtener_rol_usuario()
        self.setWindowTitle(f"{APP_NAME} - {usuario}")
        self.setWindowIcon(QIcon(APP_ICON))
        self.showMaximized()
    
        self.interfaz_principal()
    
    def obtener_rol_usuario(self): # → Obtener el rol de usuario activo
        try:
            from modules.seguridad.services.auth_service import AuthService
            auth_service = AuthService()
            usuario_data = auth_service.obtener_usuario_autenticado(self.usuario)
            return usuario_data['nombre_rol'] if usuario_data else 'empleado'
        except Exception as e:
            print(f"Error obteniendo rol de usuario: {e}")
            return 'empleado'
    
    def centrar_ventana(self):
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def interfaz_principal(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.crear_header()
        main_layout.addWidget(header)
        
        # Contenido
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Menú lateral
        menu = self.menu_lateral()
        content_layout.addWidget(menu)
        
        # Área principal
        self.main_content = QStackedWidget()
        self.main_content.setStyleSheet("background-color: white;")
        content_layout.addWidget(self.main_content, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        self.bienvenida_sistema()
    
    def crear_header(self): # → Cabecero
        header = QFrame()
        header.setStyleSheet(f"background-color: {THEME_COLOR}; color: white;")
        header.setFixedHeight(102)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Título con ícono
        titulo_layout = QHBoxLayout()
        
        # Ícono de la aplicación
        icono_label = QLabel()
        pixmap = QIcon(APP_ICON).pixmap(54, 54)  # Tamaño del ícono
        icono_label.setPixmap(pixmap)
        titulo_layout.addWidget(icono_label)
        
        # Nombre de la aplicación
        titulo = QLabel(APP_NAME)
        titulo.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-left: 10px;")
        titulo_layout.addWidget(titulo)
        
        titulo_widget = QWidget()
        titulo_widget.setLayout(titulo_layout)
        layout.addWidget(titulo_widget)
        
        layout.addStretch()
        
        # Usuario
        usuario = QLabel(f"👤 {self.usuario}")
        usuario.setStyleSheet("color: white; font-family: Roboto; font-size: 20px;")
        layout.addWidget(usuario)

        return header
    
    def menu_lateral(self):
        menu = QFrame()
        menu.setStyleSheet("background-color: #b9c2c4;")
        menu.setFixedWidth(230)
        
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(20, 20, 10, 10) # →, ↓, ←, ↑
        
        # Botones principales
        botones = [
            ("Ventas", self.mostrar_ventas),
            ("Inventario", self.mostrar_inventario),
            ("Promociones", self.mostrar_promociones),
            ("Alertas", self.mostrar_alertas),
            ("Devoluciones", self.mostrar_devoluciones),
            ("Reportes", self.mostrar_reportes),
            ("⚙️ Configuración", self.mostrar_configuracion)
        ]
        
        # Agregar gestión de empleados solo para administradores
        if self.usuario_rol in ['administrador', 'admin']:
            botones.insert(3, ("Empleados", self.mostrar_empleados))

        for texto, comando in botones:
            btn = QPushButton(texto)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #b9c2c4;
                    color: {NIGHT_COLOR};
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 16px;
                    font-family: 'Roboto';
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #9ba5a7;
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(comando)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Botón salir
        btn_salir = QPushButton("Cerrar Sesión")
        btn_salir.setStyleSheet(f"""
            QPushButton {{
                background-color: {ERROR_COLOR};
                color: white;
                border: 2 px solid;
                padding: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_salir)
        
        return menu
    
    def bienvenida_sistema(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        titulo = QLabel("🏪 Bienvenido al Sistema")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 54px; font-weight: bold; color: #2c3e50; margin: 20px;")

        subtitulo = QLabel("Selecciona un módulo del menú para comenzar")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size: 20px; color: #7f8c8d;")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        self.main_content.addWidget(widget)
        self.main_content.setCurrentWidget(widget)
    
    def limpiar_contenido(self):
        while self.main_content.count():
            child = self.main_content.widget(0)
            self.main_content.removeWidget(child)
            child.setParent(None)
    
    def mostrar_inventario(self):
        self.limpiar_contenido()
        try:
            from modules.productos.view.inventario_view import InventarioFrame
            inventario = InventarioFrame(self)
            self.main_content.addWidget(inventario)
            self.main_content.setCurrentWidget(inventario)
        except Exception as e:
            self.mostrar_error("Inventario", str(e))
    
    def mostrar_ventas(self):
        self.limpiar_contenido()
        try:
            from modules.ventas.view.venta_view import VentasFrame
            ventas = VentasFrame(self)
            self.main_content.addWidget(ventas)
            self.main_content.setCurrentWidget(ventas)
        except Exception as e:
            self.mostrar_error("Ventas", f"Error al cargar módulo: {str(e)}")
    
    def mostrar_reportes(self):
        self.limpiar_contenido()
<<<<<<< HEAD
<<<<<<< HEAD:views/dashboard.py
        try:
            from views.reportes_view import ReportesFrame
=======
        try:
            from modules.reportes.reportes_view import ReportesFrame
>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)
            reportes = ReportesFrame(self)
            self.main_content.addWidget(reportes)
            self.main_content.setCurrentWidget(reportes)
        except Exception as e:
<<<<<<< HEAD
            self.mostrar_error("📊 Reportes", f"Error al cargar módulo: {str(e)}")
=======
        self.mostrar_error("Reportes", "Próximamente en Sprint 2")
>>>>>>> 51bcbc5 (feat: Preparación de la estructura para el Sprint 2 XP - archivos base):shared/dashboard.py
    
=======
            print("ERROR aquí", e)
            self.mostrar_error("Reportes", str(e))

>>>>>>> a690a5d (Fix: Significant improvements were made to modules and sharedfolder.)
    def mostrar_empleados(self):
        self.limpiar_contenido()
        try:
            from modules.seguridad.view.empleado_view import EmpleadosWidget
            empleados_widget = EmpleadosWidget(self.usuario_rol)
            self.main_content.addWidget(empleados_widget)
            self.main_content.setCurrentWidget(empleados_widget)
        except Exception as e:
            self.mostrar_error("Empleados", f"Error al cargar módulo: {str(e)}")
    
    def mostrar_promociones(self): # → Adriel + Choncen
        self.limpiar_contenido()
        self.mostrar_error("Compras", "Próximamente en Sprint 2")

    def mostrar_alertas(self): # → Arif + Hugo
        self.limpiar_contenido()
        self.mostrar_error("Alertas", "Próximamente en Sprint 2")

    def mostrar_devoluciones(self): # → Rodrigo + Gian
        self.limpiar_contenido()
        self.mostrar_error("Devoluciones", "Próximamente en Sprint 2")
    
    def mostrar_configuracion(self): # → Sorteo → Semana 14
        self.limpiar_contenido()
        self.mostrar_error("⚙️ Configuración", "Próximamente en Sprint 2")
    
    def mostrar_error(self, titulo, mensaje):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        emoji = QLabel("🚧")
        emoji.setAlignment(Qt.AlignCenter)
        emoji.setStyleSheet("font-size: 48px; margin: 20px;")
        
        title_label = QLabel(titulo)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; color: #95a5a6; margin: 10px;")
        
        msg_label = QLabel(mensaje)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        layout.addWidget(emoji)
        layout.addWidget(title_label)
        layout.addWidget(msg_label)
        
        self.main_content.addWidget(widget)
        self.main_content.setCurrentWidget(widget)
    
    def cerrar_sesion(self):
        """Cierra sesión y vuelve al login"""
        self.hide()
        from modules.seguridad.view.login import LoginVentana
        self.login_window = LoginVentana()
        self.login_window.show()
    
    def closeEvent(self, event):
        """Cerrar toda la aplicación cuando se cierra el dashboard con la X"""
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()
        event.accept()