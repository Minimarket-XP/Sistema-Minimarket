"""
HUI006 - Realizar devoluciones
Como cajero, quiero realizar devoluciones de productos para 
gestionar los reembolsos de manera adecuada.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QMessageBox, QFrame, QComboBox,
                             QAbstractItemView, QHeaderView, QSpinBox, QDoubleSpinBox,
                             QCompleter)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont
from core.config import *
from modules.ventas.service.devolucion_service import DevolucionService
from shared.helpers import formatear_precio
from modules.productos.view.inventario_view import TablaNoEditable
import pandas as pd

class DevolucionesFrame(QWidget):
    """Interfaz para gestionar devoluciones de productos."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.devolucion_service = DevolucionService()
        self.venta_actual = None
        self.productos_venta = pd.DataFrame()
        self.productos_a_devolver = []
        
        self.crearInterfaz()
        self.configurarAutocompletado()
        self.cargarHistorico()
    
    def crearInterfaz(self):
        """Crea la interfaz completa de devoluciones."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Gestión de Devoluciones")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 28px;
                font-weight: bold;
                font-family: Roboto;
                margin-bottom: 10px;
            }}
        """)
        main_layout.addWidget(titulo)
        
        # Panel superior - Búsqueda de venta
        busqueda_frame = self.crearPanelBusqueda()
        main_layout.addWidget(busqueda_frame)
        
        # Panel medio - Productos de la venta
        productos_frame = self.crearPanelProductos()
        main_layout.addWidget(productos_frame)
        
        # Panel de configuración - Motivo y acciones
        config_frame = self.crearPanelConfiguracion()
        main_layout.addWidget(config_frame)
        
        # Panel inferior - Histórico de devoluciones
        historico_frame = self.crearPanelHistorico()
        main_layout.addWidget(historico_frame)
    
    def crearPanelBusqueda(self):
        """Crea el panel de búsqueda de venta."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Título del panel
        titulo = QLabel("🔍 Buscar Venta")
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Layout horizontal para búsqueda
        search_layout = QHBoxLayout()
        
        label = QLabel("ID de Venta:")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        search_layout.addWidget(label)
        
        self.input_id_venta = QLineEdit()
        self.input_id_venta.setPlaceholderText("Ej: VTA0001")
        self.input_id_venta.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.input_id_venta.setFixedWidth(200)
        self.input_id_venta.returnPressed.connect(self.buscarVenta)
        search_layout.addWidget(self.input_id_venta)
        
        btn_buscar = QPushButton("Buscar Venta")
        btn_buscar.setStyleSheet(f"""
            QPushButton {{
                background-color: {INFO_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        btn_buscar.clicked.connect(self.buscarVenta)
        search_layout.addWidget(btn_buscar)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Label de información de venta
        self.label_info_venta = QLabel("")
        self.label_info_venta.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 5px;")
        layout.addWidget(self.label_info_venta)
        
        return frame
    
    def crearPanelProductos(self):
        """Crea el panel de productos de la venta."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        titulo = QLabel("📦 Productos de la Venta")
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Tabla de productos
        self.tabla_productos = TablaNoEditable()
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        columnas = ["ID Producto", "Nombre", "Cantidad Vendida", "Precio Unit.", 
                   "Subtotal", "Cant. a Devolver"]
        self.tabla_productos.setColumnCount(len(columnas))
        self.tabla_productos.setHorizontalHeaderLabels(columnas)
        
        # Configurar anchos
        header = self.tabla_productos.horizontalHeader()
        self.tabla_productos.setColumnWidth(0, 100)  # ID
        self.tabla_productos.setColumnWidth(1, 300)  # Nombre
        self.tabla_productos.setColumnWidth(2, 120)  # Cantidad
        self.tabla_productos.setColumnWidth(3, 100)  # Precio
        self.tabla_productos.setColumnWidth(4, 100)  # Subtotal
        header.setStretchLastSection(True)  # Cantidad a devolver
        
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_productos.setAlternatingRowColors(True)
        
        layout.addWidget(self.tabla_productos)
        
        return frame
    
    def crearPanelConfiguracion(self):
        """Crea el panel de configuración de la devolución."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Layout horizontal para motivo y total
        top_layout = QHBoxLayout()
        
        # Motivo de devolución
        motivo_layout = QVBoxLayout()
        label_motivo = QLabel("Motivo de Devolución:")
        label_motivo.setStyleSheet("font-size: 14px; font-weight: bold;")
        motivo_layout.addWidget(label_motivo)
        
        self.combo_motivo = QComboBox()
        self.combo_motivo.addItems([
            "Producto defectuoso",
            "Producto vencido",
            "Cliente insatisfecho",
            "Error en la venta",
            "Otro"
        ])
        self.combo_motivo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
        """)
        motivo_layout.addWidget(self.combo_motivo)
        top_layout.addLayout(motivo_layout)
        
        top_layout.addStretch()
        
        # Total a devolver
        total_layout = QVBoxLayout()
        label_total = QLabel("Total a Devolver:")
        label_total.setStyleSheet("font-size: 14px; font-weight: bold;")
        total_layout.addWidget(label_total)
        
        self.label_total_devolucion = QLabel("S/. 0.00")
        self.label_total_devolucion.setStyleSheet(f"""
            QLabel {{
                background-color: {THEME_COLOR};
                color: white;
                padding: 10px;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                min-width: 150px;
            }}
        """)
        self.label_total_devolucion.setAlignment(Qt.AlignCenter)
        total_layout.addWidget(self.label_total_devolucion)
        top_layout.addLayout(total_layout)
        
        layout.addLayout(top_layout)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_procesar = QPushButton("✓ Procesar Devolución")
        self.btn_procesar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
            }}
        """)
        self.btn_procesar.clicked.connect(self.procesarDevolucion)
        self.btn_procesar.setEnabled(False)
        btn_layout.addWidget(self.btn_procesar)
        
        btn_limpiar = QPushButton("🧹 Limpiar Formulario")
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
        """)
        btn_limpiar.clicked.connect(self.limpiarFormulario)
        btn_layout.addWidget(btn_limpiar)
        
        layout.addLayout(btn_layout)
        
        return frame
    
    def crearPanelHistorico(self):
        """Crea el panel de histórico de devoluciones."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        titulo = QLabel("📋 Histórico de Devoluciones")
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)
        
        # Tabla de histórico
        self.tabla_historico = TablaNoEditable()
        self.tabla_historico.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        columnas = ["ID Devolución", "ID Venta", "Fecha", "Motivo", 
                   "Monto Devuelto", "Tipo", "Estado"]
        self.tabla_historico.setColumnCount(len(columnas))
        self.tabla_historico.setHorizontalHeaderLabels(columnas)
        
        # Configurar anchos
        self.tabla_historico.setColumnWidth(0, 100)
        self.tabla_historico.setColumnWidth(1, 100)
        self.tabla_historico.setColumnWidth(2, 150)
        self.tabla_historico.setColumnWidth(3, 250)
        self.tabla_historico.setColumnWidth(4, 120)
        self.tabla_historico.setColumnWidth(5, 80)
        self.tabla_historico.setColumnWidth(6, 100)
        
        self.tabla_historico.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_historico.setAlternatingRowColors(True)
        self.tabla_historico.setMaximumHeight(250)
        
        layout.addWidget(self.tabla_historico)
        
        return frame
    
    def configurarAutocompletado(self):
        """Configura el autocompletado para el campo de ID de venta."""
        try:
            # Obtener todos los IDs de ventas disponibles
            from core.database import db
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            # Consultar IDs de ventas (solo ventas completadas que puedan tener devoluciones)
            cursor.execute('''
                SELECT DISTINCT id_venta 
                FROM ventas 
                WHERE estado_venta = 'completado'
                ORDER BY fecha_venta DESC
                LIMIT 100
            ''')
            
            ventas = cursor.fetchall()
            conexion.close()
            
            # Crear lista de IDs
            ids_ventas = [venta[0] for venta in ventas]
            
            # Configurar QCompleter
            if ids_ventas:
                completer = QCompleter(ids_ventas)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setMaxVisibleItems(10)
                
                # Aplicar al campo de entrada
                self.input_id_venta.setCompleter(completer)
            
        except Exception as e:
            print(f"Error configurando autocompletado: {e}")
    
    def buscarVenta(self):
        """Busca una venta por su ID y carga sus productos."""
        id_venta = self.input_id_venta.text().strip()
        
        if not id_venta:
            QMessageBox.warning(self, "Campo vacío", "Por favor ingrese un ID de venta")
            return
        
        # Buscar venta
        success, productos, mensaje = self.devolucion_service.obtener_productos_venta(id_venta)
        
        if not success:
            QMessageBox.warning(self, "Venta no encontrada", mensaje)
            self.limpiarTablaProductos()
            self.label_info_venta.setText("")
            return
        
        self.venta_actual = id_venta
        self.productos_venta = productos
        
        # Actualizar información
        total_venta = productos['subtotal_detalle'].sum()
        self.label_info_venta.setText(
            f"Venta encontrada - Total original: {formatear_precio(total_venta)} - "
            f"{len(productos)} productos"
        )
        self.label_info_venta.setStyleSheet("font-size: 12px; color: #27ae60; margin-top: 5px;")
        
        # Cargar productos en tabla
        self.cargarProductosVenta()
    
    def cargarProductosVenta(self):
        """Carga los productos de la venta en la tabla."""
        if self.productos_venta.empty:
            return
        
        self.tabla_productos.setRowCount(len(self.productos_venta))
        
        for idx, row in self.productos_venta.iterrows():
            # ID Producto
            self.tabla_productos.setItem(idx, 0, QTableWidgetItem(str(row['id_producto'])))
            
            # Nombre
            self.tabla_productos.setItem(idx, 1, QTableWidgetItem(str(row['producto_nombre'])))
            
            # Cantidad vendida
            cantidad = float(row['cantidad_detalle'])
            self.tabla_productos.setItem(idx, 2, QTableWidgetItem(f"{cantidad:.2f}"))
            
            # Precio unitario
            precio = float(row['precio_unitario_detalle'])
            self.tabla_productos.setItem(idx, 3, QTableWidgetItem(formatear_precio(precio)))
            
            # Subtotal
            subtotal = float(row['subtotal_detalle'])
            self.tabla_productos.setItem(idx, 4, QTableWidgetItem(formatear_precio(subtotal)))
            
            # Spinbox para cantidad a devolver
            spinbox = QDoubleSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(cantidad)
            spinbox.setValue(0)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.1)
            spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    padding: 4px;
                    border: 1px solid #3498db;
                    border-radius: 3px;
                    font-size: 12px;
                }
            """)
            spinbox.valueChanged.connect(self.actualizarTotalDevolucion)
            self.tabla_productos.setCellWidget(idx, 5, spinbox)
        
        self.btn_procesar.setEnabled(False)
    
    def limpiarTablaProductos(self):
        """Limpia la tabla de productos."""
        self.tabla_productos.setRowCount(0)
        self.venta_actual = None
        self.productos_venta = pd.DataFrame()
        self.label_total_devolucion.setText("S/. 0.00")
        self.btn_procesar.setEnabled(False)
    
    def actualizarTotalDevolucion(self):
        """Actualiza el total a devolver basándose en las cantidades seleccionadas."""
        total = 0.0
        tiene_productos = False
        
        for idx in range(self.tabla_productos.rowCount()):
            spinbox = self.tabla_productos.cellWidget(idx, 5)
            if spinbox and spinbox.value() > 0:
                cantidad_devolver = spinbox.value()
                precio_text = self.tabla_productos.item(idx, 3).text()
                # Extraer el número del precio (eliminar "S/. ")
                precio = float(precio_text.replace("S/. ", "").replace(",", ""))
                total += cantidad_devolver * precio
                tiene_productos = True
        
        self.label_total_devolucion.setText(formatear_precio(total))
        self.btn_procesar.setEnabled(tiene_productos and total > 0)
    
    def procesarDevolucion(self):
        """Procesa la devolución de los productos seleccionados."""
        if not self.venta_actual:
            QMessageBox.warning(self, "Sin venta", "Debe buscar una venta primero")
            return
        
        # Recopilar productos a devolver
        productos_devolver = []
        
        for idx in range(self.tabla_productos.rowCount()):
            spinbox = self.tabla_productos.cellWidget(idx, 5)
            cantidad_devolver = spinbox.value() if spinbox else 0
            
            if cantidad_devolver > 0:
                row_data = self.productos_venta.iloc[idx]
                
                productos_devolver.append({
                    'id_producto': row_data['id_producto'],
                    'id_detalle_venta': row_data['id_detalle_venta'],
                    'cantidad_devolver': cantidad_devolver,
                    'cantidad_original': float(row_data['cantidad_detalle']),
                    'precio_unitario': float(row_data['precio_unitario_detalle']),
                    'nombre_producto': row_data['producto_nombre']
                })
        
        if not productos_devolver:
            QMessageBox.warning(self, "Sin productos", 
                              "Debe seleccionar al menos un producto para devolver")
            return
        
        # Confirmar devolución
        motivo = self.combo_motivo.currentText()
        total = self.label_total_devolucion.text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar Devolución",
            f"¿Procesar devolución por {total}?\n\n"
            f"Venta: {self.venta_actual}\n"
            f"Motivo: {motivo}\n"
            f"Productos: {len(productos_devolver)}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Procesar devolución
        success, id_devolucion, mensaje = self.devolucion_service.procesar_devolucion(
            id_venta=self.venta_actual,
            productos_devolver=productos_devolver,
            motivo=motivo
        )
        
        if success:
            QMessageBox.information(
                self,
                "Devolución Exitosa",
                f"✅ {mensaje}\n\nEl stock ha sido actualizado automáticamente."
            )
            self.limpiarFormulario()
            self.cargarHistorico()
            self.configurarAutocompletado()  # Actualizar autocompletado
        else:
            QMessageBox.critical(
                self,
                "Error en Devolución",
                f"❌ {mensaje}"
            )
    
    def limpiarFormulario(self):
        """Limpia todos los campos del formulario."""
        self.input_id_venta.clear()
        self.limpiarTablaProductos()
        self.label_info_venta.setText("")
        self.combo_motivo.setCurrentIndex(0)
        self.label_total_devolucion.setText("S/. 0.00")
        self.btn_procesar.setEnabled(False)
    
    def cargarHistorico(self):
        """Carga el histórico de devoluciones."""
        devoluciones = self.devolucion_service.obtener_devoluciones_historicas(limite=50)
        
        if devoluciones.empty:
            self.tabla_historico.setRowCount(0)
            return
        
        self.tabla_historico.setRowCount(len(devoluciones))
        
        for idx, row in devoluciones.iterrows():
            # ID Devolución
            self.tabla_historico.setItem(idx, 0, QTableWidgetItem(str(row['id_devolucion'])))
            
            # ID Venta
            self.tabla_historico.setItem(idx, 1, QTableWidgetItem(str(row['id_venta'])))
            
            # Fecha
            self.tabla_historico.setItem(idx, 2, QTableWidgetItem(str(row['fecha_devolucion'])))
            
            # Motivo
            motivo = str(row['motivo_devolucion']) if pd.notna(row['motivo_devolucion']) else "N/A"
            self.tabla_historico.setItem(idx, 3, QTableWidgetItem(motivo))
            
            # Monto
            monto = formatear_precio(row['monto_devolucion'])
            self.tabla_historico.setItem(idx, 4, QTableWidgetItem(monto))
            
            # Tipo
            tipo = str(row['tipo_devolucion']).capitalize()
            self.tabla_historico.setItem(idx, 5, QTableWidgetItem(tipo))
            
            # Estado
            estado = str(row['estado_devolucion']).capitalize()
            self.tabla_historico.setItem(idx, 6, QTableWidgetItem(estado))