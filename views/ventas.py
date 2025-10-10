## Módulo de Ventas - Sistema Minimarket

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QSpinBox, QMessageBox, QFrame, 
                             QAbstractItemView, QHeaderView)
from PyQt5.QtCore import Qt
from views.settings import *
from models.producto import ProductoModel
from models.venta import VentaModel
from models.helpers import formatear_precio
from views.inventario import TablaNoEditable
import pandas as pd

class VentasFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.venta_model = VentaModel()
        self.carrito = []  # Lista de productos en el carrito
        self.total = 0.0
        
        self.crearInterfaz()
        self.cargarProductos()
    
    def crearInterfaz(self):
        # Layout principal vertical para incluir título arriba
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Título centrado arriba
        titulo = QLabel("Registro de Ventas")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 22px;
                font-weight: bold;
                font-family: Arial;
                margin-bottom: 10px;
            }}
        """)
        main_layout.addWidget(titulo)
        
        # Layout horizontal para los paneles
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(15)

        # Panel izquierdo - Productos disponibles (SIN QFrame envolvente)
        left_layout = QVBoxLayout()
        
        # Info del día
        info_frame = self.crearInfoDia()
        left_layout.addWidget(info_frame)
        
        # Búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar producto...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 15px;
            }
        """)
        self.search_input.textChanged.connect(self.buscarProducto)
        
        btn_limpiar = QPushButton("🗑️")
        btn_limpiar.setFixedSize(45, 45)
        btn_limpiar.clicked.connect(self.limpiarBusqueda)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_limpiar)
        left_layout.addLayout(search_layout)
        
        # Tabla de productos - DIRECTAMENTE SIN PANEL
        self.tabla_productos = TablaNoEditable()
        self.tabla_productos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: black;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #9CCDF0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 2px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QScrollBar:vertical{
                border: none;
                background: #E3E3E3;
                width: 12 px;
                margin: 0px;
            }
            QScrollBar::handle:vertical{
                background: #ccc;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        # Configurar tabla
        columnas = ["ID", "Nombre", "Precio", "Stock", "Acción"]        
        self.tabla_productos.setColumnCount(len(columnas))
        self.tabla_productos.setHorizontalHeaderLabels(columnas)
        
        # Configurar selección - igual que inventario
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setFocusPolicy(Qt.NoFocus)

        # Ajustar tamaños de columna - IGUAL QUE INVENTARIO
        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Configurar anchos específicos como en inventario
        anchos = [80, 600, 80, 80, 80]  # ID, Nombre, Precio, Stock, Acción
        for i, ancho in enumerate(anchos):
            self.tabla_productos.setColumnWidth(i, ancho)
        
        left_layout.addWidget(self.tabla_productos)
        
        panels_layout.addLayout(left_layout, 2)
        
        # Panel derecho - Carrito de compras (SIN QFrame envolvente)
        right_layout = QVBoxLayout()
        
        # Título del carrito
        titulo_carrito = QLabel("🛒 Carrito de Compras")
        titulo_carrito.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(titulo_carrito)
        
        # Tabla del carrito - DIRECTAMENTE SIN PANEL
        self.tabla_carrito = TablaNoEditable()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Cant.", "Precio", "Total", "Acción"])
        self.tabla_carrito.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: black;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #9CCDF0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 2px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QScrollBar:vertical{
                border: none;
                background: #E3E3E3;
                width: 12 px;
                margin: 0px;
            }
            QScrollBar::handle:vertical{
                background: #ccc;
                min-height: 20px;
                border-radius: 6px;
            }
        """)
        
        # Ajustar columnas del carrito
        self.tabla_carrito.setColumnWidth(0, 243)  # Producto
        self.tabla_carrito.setColumnWidth(1, 57)   # Cantidad
        self.tabla_carrito.setColumnWidth(2, 69)   # Precio
        self.tabla_carrito.setColumnWidth(3, 85)   # Total
        self.tabla_carrito.setColumnWidth(4, 58)   # Acción
        
        right_layout.addWidget(self.tabla_carrito)
        
        # Total
        self.label_total = QLabel("Total: S/ 0.00")
        self.label_total.setStyleSheet(f"""
            QLabel {{
                background-color: {THEME_COLOR};
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }}
        """)
        self.label_total.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.label_total)
        
        # Botones del carrito
        btn_procesar = QPushButton("💳 Procesar Venta")
        btn_procesar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        btn_procesar.clicked.connect(self.procesarVenta)
        
        btn_limpiar = QPushButton("🗑️ Limpiar Carrito")
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_COLOR};
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
        """)
        btn_limpiar.clicked.connect(self.limpiarCarrito)
        
        right_layout.addWidget(btn_procesar)
        right_layout.addWidget(btn_limpiar)
        
        panels_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(panels_layout)
    
    def crearInfoDia(self):
        resumen = self.venta_model.obtener_resumen_dia()
        
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; padding: 10px;")
        
        info_layout = QHBoxLayout(info_frame)
        
        titulo = QLabel("📦 Productos Disponibles")
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold;")
        info_layout.addWidget(titulo)
        info_layout.addStretch()
        
        ventas_label = QLabel(f"📊 Ventas hoy: {resumen['total_ventas']}")
        ventas_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(ventas_label)

        # Total del día
        total_label = QLabel(f"💰 Total: {formatear_precio(resumen['monto_total'])}")
        total_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        info_layout.addWidget(total_label)
        
        return info_frame
    
    def cargarProductos(self):
        df = self.producto_model.obtener_todos()
        
        # Filtrar productos con stock > 0
        productos_disponibles = []
        for _, row in df.iterrows():
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            if stock > 0:
                productos_disponibles.append(row)
        
        # Configurar número exacto de filas
        self.tabla_productos.setRowCount(len(productos_disponibles))
        
        for row_idx, row in enumerate(productos_disponibles):
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            
            # ID
            self.tabla_productos.setItem(row_idx, 0, QTableWidgetItem(str(row["ID"])))
            
            # Nombre
            self.tabla_productos.setItem(row_idx, 1, QTableWidgetItem(str(row["Nombre"])))
            
            # Precio
            precio_texto = formatear_precio(row["Precio"])
            self.tabla_productos.setItem(row_idx, 2, QTableWidgetItem(precio_texto))
            
            # Stock
            self.tabla_productos.setItem(row_idx, 3, QTableWidgetItem(str(stock)))
            
            # Botón agregar
            btn_agregar = QPushButton("➕")
            btn_agregar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {INFO_COLOR};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #2980b9;
                }}
            """)
            btn_agregar.clicked.connect(lambda checked, r=row: self.agregarCarrito(r))
            self.tabla_productos.setCellWidget(row_idx, 4, btn_agregar)
    
    def buscarProducto(self, texto):
        if not texto.strip():
            self.cargarProductos()
            return
        
        df = self.producto_model.buscarProducto(texto)
        
        # Filtrar productos con stock > 0
        productos_encontrados = []
        for _, row in df.iterrows():
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            if stock > 0:
                productos_encontrados.append(row)
        
        # Configurar número exacto de filas
        self.tabla_productos.setRowCount(len(productos_encontrados))
        
        for row_idx, row in enumerate(productos_encontrados):
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            
            self.tabla_productos.setItem(row_idx, 0, QTableWidgetItem(str(row["ID"])))
            self.tabla_productos.setItem(row_idx, 1, QTableWidgetItem(str(row["Nombre"])))
            self.tabla_productos.setItem(row_idx, 2, QTableWidgetItem(formatear_precio(row["Precio"])))
            self.tabla_productos.setItem(row_idx, 3, QTableWidgetItem(str(stock)))
            
            btn_agregar = QPushButton("➕")
            btn_agregar.clicked.connect(lambda checked, r=row: self.agregarCarrito(r))
            self.tabla_productos.setCellWidget(row_idx, 4, btn_agregar)
    
    def limpiarBusqueda(self):
        self.search_input.clear()
        self.cargarProductos()
    
    def agregarCarrito(self, producto):
        producto_id = str(producto["ID"])
        nombre = str(producto["Nombre"])
        precio = float(producto["Precio"])
        
        # Verificar si el producto ya está en el carrito
        for item in self.carrito:
            if item["id"] == producto_id:
                item["cantidad"] += 1
                item["total"] = item["cantidad"] * item["precio"]
                break
        else:
            # Agregar nuevo producto al carrito
            self.carrito.append({
                "id": producto_id,
                "nombre": nombre,
                "cantidad": 1,
                "precio": precio,
                "total": precio
            })
        
        self.actualizarCarrito()
        QMessageBox.information(self, "Producto agregado", f"'{nombre}' agregado al carrito")
    
    def actualizarCarrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        self.total = 0.0
        
        for row_idx, item in enumerate(self.carrito):
            self.tabla_carrito.setItem(row_idx, 0, QTableWidgetItem(item["nombre"]))
            self.tabla_carrito.setItem(row_idx, 1, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_carrito.setItem(row_idx, 2, QTableWidgetItem(formatear_precio(item["precio"])))
            self.tabla_carrito.setItem(row_idx, 3, QTableWidgetItem(formatear_precio(item["total"])))
            
            # Botón remover
            btn_remover = QPushButton("🗑️")
            btn_remover.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ERROR_COLOR};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #c0392b;
                }}
            """)
            btn_remover.clicked.connect(lambda checked, idx=row_idx: self.removerCarrito(idx))
            self.tabla_carrito.setCellWidget(row_idx, 4, btn_remover)
            
            self.total += item["total"]
        
        self.label_total.setText(f"Total: {formatear_precio(self.total)}")
    
    def removerCarrito(self, indice):
        if 0 <= indice < len(self.carrito):
            producto_removido = self.carrito.pop(indice)
            self.actualizarCarrito()
            QMessageBox.information(self, "Producto removido", 
                                   f"'{producto_removido['nombre']}' removido del carrito")
    
    def limpiarCarrito(self):
        self.carrito.clear()
        self.actualizarCarrito()
        QMessageBox.information(self, "Carrito limpio", "Todos los productos han sido removidos del carrito")
    
    def procesarVenta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "Agrega productos al carrito antes de procesar la venta")
            return
        
        # Confirmar venta
        reply = QMessageBox.question(self, "Procesar Venta", 
                                   f"¿Procesar venta por {formatear_precio(self.total)}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Procesar la venta usando el modelo
            success, venta_id, mensaje = self.venta_model.procesar_venta(
                carrito=self.carrito,
                empleado="Admin",  # Por ahora usamos Admin por defecto
                metodo_pago="efectivo"
            )
            
            if success:
                QMessageBox.information(self, "Venta Exitosa", 
                                       f"✅ {mensaje}\nID: {venta_id}")
                self.limpiarCarrito()
                self.cargarProductos()  # Recargar para actualizar stock

            else:
                QMessageBox.critical(self, "Error en Venta", f"❌ {mensaje}")