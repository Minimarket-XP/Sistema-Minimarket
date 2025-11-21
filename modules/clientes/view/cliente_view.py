from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.config import *
from modules.clientes.models.cliente_model import ClienteModel
from shared.components.forms import ClienteForm
from modules.productos.view.inventario_view import TablaNoEditable

class ClientesWidget(QWidget):
    def __init__(self, usuario_rol=None):
        super().__init__()
        self.usuario_rol = usuario_rol
        self.cliente_model = ClienteModel()
        self._interfaz()
        self.cargar_clientes()

    def _interfaz(self):
        layout = QVBoxLayout(self)
        header = QLabel("Gestión de Clientes")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"color: {THEME_COLOR}; font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        acciones = QHBoxLayout()
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar por nombre o documento...")
        self.buscar_input.setStyleSheet("""
            QLineEdit { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            QLineEdit:focus { border: 2px solid #4285F4; }
        """)
        self.buscar_input.textChanged.connect(self.filtrar_clientes)
        btn_agregar = QPushButton("Agregar")
        btn_agregar.setStyleSheet(f"""
            QPushButton {{ background-color: {THEME_COLOR}; color: white; border: none; border-radius: 4px; padding: 10px 16px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {THEME_COLOR_HOVER}; }}
        """)
        btn_agregar.clicked.connect(self.agregar_cliente)
        acciones.addWidget(self.buscar_input)
        acciones.addWidget(btn_agregar)
        layout.addLayout(acciones)
        self.tabla = TablaNoEditable()
        columnas = ["ID", "Tipo Doc", "Número", "Nombre", "Dirección", "Teléfono", "Email", "Activo", "Acciones"]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla)

    def cargar_clientes(self):
        activos = self.cliente_model.get_all('activo = 1')
        inactivos = self.cliente_model.get_all('activo = 0')
        clientes = activos + inactivos
        self._llenar_tabla(clientes)

    def _llenar_tabla(self, clientes):
        self.tabla.setRowCount(len(clientes))
        for row, c in enumerate(clientes):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(c.get('id'))))
            self.tabla.setItem(row, 1, QTableWidgetItem(str(c.get('tipo_documento', ''))))
            self.tabla.setItem(row, 2, QTableWidgetItem(str(c.get('num_documento', ''))))
            self.tabla.setItem(row, 3, QTableWidgetItem(str(c.get('nombre', ''))))
            self.tabla.setItem(row, 4, QTableWidgetItem(str(c.get('direccion', ''))))
            self.tabla.setItem(row, 5, QTableWidgetItem(str(c.get('telefono', ''))))
            self.tabla.setItem(row, 6, QTableWidgetItem(str(c.get('email', ''))))
            estado_item = QTableWidgetItem("Activo" if c.get('activo') else "Inactivo")
            if c.get('activo'):
                estado_item.setForeground(Qt.darkGreen)
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))
            else:
                estado_item.setForeground(Qt.red)
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))
            self.tabla.setItem(row, 7, estado_item)
            contenedor = QWidget()
            h = QHBoxLayout(contenedor)
            h.setContentsMargins(5, 2, 5, 2)
            h.setSpacing(5)
            btn_editar = QPushButton("Editar")
            btn_editar.setFixedHeight(22)
            btn_editar.setStyleSheet("""
                QPushButton { background-color: #3498db; color: white; border: none; border-radius: 4px; padding: 4px 8px; }
                QPushButton:hover { background-color: #2980b9; }
            """)
            btn_editar.clicked.connect(lambda checked, cliente=c: self.editar_cliente(cliente))
            if c.get('activo'):
                btn_estado = QPushButton("Desactivar")
                btn_estado.setStyleSheet("""
                    QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 4px 8px; }
                    QPushButton:hover { background-color: #c0392b; }
                """)
                btn_estado.clicked.connect(lambda checked, cid=c.get('id'): self.desactivar_cliente(cid))
            else:
                btn_estado = QPushButton("Activar")
                btn_estado.setStyleSheet("""
                    QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 4px; padding: 4px 8px; }
                    QPushButton:hover { background-color: #27ae60; }
                """)
                btn_estado.clicked.connect(lambda checked, cid=c.get('id'): self.activar_cliente(cid))
            h.addWidget(btn_editar)
            h.addWidget(btn_estado)
            contenedor.setLayout(h)
            self.tabla.setCellWidget(row, 8, contenedor)

    def filtrar_clientes(self, texto):
        termino = texto or ''
        clientes = self.cliente_model.buscar_clientes(termino)
        self._llenar_tabla(clientes)

    def agregar_cliente(self):
        dialog = AgregarClienteForm(self)
        dialog.exec_()

    def editar_cliente(self, cliente):
        dialog = EditarClienteForm(self, cliente)
        dialog.exec_()

    def desactivar_cliente(self, cliente_id):
        reply = QMessageBox.question(self, "Confirmar", "¿Desactivar cliente?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.cliente_model.desactivar_cliente(cliente_id):
                self.cargar_clientes()
            else:
                QMessageBox.critical(self, "Error", "No se pudo desactivar el cliente")

    def activar_cliente(self, cliente_id):
        if self.cliente_model.actualizar_cliente(cliente_id, {'activo': 1}):
            self.cargar_clientes()
        else:
            QMessageBox.critical(self, "Error", "No se pudo activar el cliente")

class AgregarClienteForm(ClienteForm):
    def __init__(self, parent):
        self.parent_frame = parent
        super().__init__(parent, "Registrar Cliente")
        self.cliente_model = ClienteModel()

    def validarYGuardar(self):
        datos = self.validarDatos()
        if datos is None:
            return
        try:
            self.cliente_model.crear_cliente(
                datos['tipo_documento'], datos['num_documento'], datos['nombre'], datos['direccion'], datos['telefono'], datos['email']
            )
            QMessageBox.information(self, "Éxito", "Cliente registrado correctamente.")
            self.parent_frame.cargar_clientes()
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")

class EditarClienteForm(ClienteForm):
    def __init__(self, parent, cliente):
        self.parent_frame = parent
        self.cliente_id = cliente.get('id')
        super().__init__(parent, "Modificar Cliente", cliente)
        self.cliente_model = ClienteModel()

    def validarYGuardar(self):
        datos = self.validarDatos()
        if datos is None:
            return
        try:
            ok = self.cliente_model.actualizar_cliente(self.cliente_id, datos)
            if ok:
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
                self.parent_frame.cargar_clientes()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el cliente.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")