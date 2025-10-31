## Módulo de Ventas - Sistema Minimarket

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QMessageBox, QFrame, 
                             QAbstractItemView, QHeaderView, QInputDialog)
from PyQt5.QtCore import Qt
<<<<<<< HEAD:views/ventas.py
from views.settings import *
from models.producto import ProductoModel
from models.venta import VentaModel
from models.helpers import formatear_precio
from models.descuentos import AplicarDescuento
from views.inventario import TablaNoEditable
=======
from core.config import *
from modules.productos.producto_model import ProductoModel
from modules.ventas.venta_model import VentaModel
from shared.helpers import formatear_precio
from modules.productos.inventario_view import TablaNoEditable
>>>>>>> 51bcbc5 (feat: Preparación de la estructura para el Sprint 2 XP - archivos base):modules/ventas/venta_view.py
import pandas as pd

class VentasFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.venta_model = VentaModel()
        self.carrito = []  # Lista de productos en el carrito
        self.total = 0.0
        self.descuento_aplicado = 0.0  # monto total descontado
        self.descuento_pct = 0.0
        self.descuento_tipo = ''
        
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

        anchosC = [243, 57, 69, 85, 58]  # Producto, Cant., Precio, Total, Acción
        for i, anchoC in enumerate(anchosC):
            self.tabla_carrito.setColumnWidth(i, anchoC)
        
        right_layout.addWidget(self.tabla_carrito)

        # Área de descuento: solo botón de opciones (eliminar input % global)
        discount_layout = QHBoxLayout()
        discount_layout.addStretch()

        btn_descuento = QPushButton("Aplicar Descuento")
        btn_descuento.clicked.connect(self.abrir_dialogo_aplicar_descuento)
        discount_layout.addWidget(btn_descuento)

        btn_deshacer = QPushButton("Deshacer Descuento")
        btn_deshacer.clicked.connect(self.deshacer_descuento)
        discount_layout.addWidget(btn_deshacer)

        right_layout.addLayout(discount_layout)

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
                item['base_total'] = item["cantidad"] * item["precio"]
                item["total"] = item['base_total']
                break
        else:
            # Agregar nuevo producto al carrito (mantener estructura simple: id, nombre, cantidad, precio, base_total, total)
            self.carrito.append({
                "id": producto_id,
                "nombre": nombre,
                "cantidad": 1,
                "precio": precio,
                "base_total": precio,
                "total": precio,
                # descuento por línea (None si no aplica)
                "descuento": None
            })
        
        self.actualizarCarrito()
        QMessageBox.information(self, "Producto agregado", f"'{nombre}' agregado al carrito")
    
    def actualizarCarrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        self.total = 0.0
        # Resetear descuento_aplicado temporal antes de cálculo (se actualizará si existe)
        # NOTE: descuentos se aplican sobre item['total'] que debe representar el estado actual
        
        for row_idx, item in enumerate(self.carrito):
            self.tabla_carrito.setItem(row_idx, 0, QTableWidgetItem(item["nombre"]))
            self.tabla_carrito.setItem(row_idx, 1, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_carrito.setItem(row_idx, 2, QTableWidgetItem(formatear_precio(item["precio"])))
            # Mostrar total (puede haber sido ajustado por descuentos)
            self.tabla_carrito.setItem(row_idx, 3, QTableWidgetItem(formatear_precio(item.get("total", item.get('base_total', 0)))))
            
            # Acciones: botón de descuento por producto + remover
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            btn_desc_line = QPushButton("D")
            btn_desc_line.setStyleSheet(f"""
                QPushButton {{
                    background-color: {INFO_COLOR};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    padding: 4px;
                }}
                QPushButton:hover {{
                    background-color: #2980b9;
                }}
            """)
            btn_desc_line.clicked.connect(lambda checked, idx=row_idx: self.aplicar_descuento_item(idx))
            action_layout.addWidget(btn_desc_line)

            btn_remover = QPushButton("🗑️")
            btn_remover.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ERROR_COLOR};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    padding: 4px;
                }}
                QPushButton:hover {{
                    background-color: #c0392b;
                }}
            """)
            btn_remover.clicked.connect(lambda checked, idx=row_idx: self.removerCarrito(idx))
            action_layout.addWidget(btn_remover)

            self.tabla_carrito.setCellWidget(row_idx, 4, action_widget)
            
            self.total += float(item.get("total", item.get('base_total', 0)))

        # Mostrar total y monto de descuento si existe
        if self.descuento_aplicado and float(self.descuento_aplicado) > 0:
            self.label_total.setText(f"Total: {formatear_precio(self.total)}  (Descuento: {formatear_precio(self.descuento_aplicado)})")
        else:
            self.label_total.setText(f"Total: {formatear_precio(self.total)}")

    def _reset_totals_to_base(self):
        for item in self.carrito:
            item['total'] = float(item.get('base_total', item.get('precio', 0) * item.get('cantidad', 1)))
            # limpiar descuento por línea al resetear (None = no descuento por línea)
            item['descuento'] = None


    def abrir_dialogo_aplicar_descuento(self):
        opciones = ["Por producto", "Por total (%)", "Monto fijo"]
        # El diálogo global ya no permite "Por producto"; esa opción se hizo por-fila.
        opciones = ["Por total (%)", "Monto fijo"]
        opcion, ok = QInputDialog.getItem(self, "Aplicar Descuento", "Selecciona opción:", opciones, 0, False)
        if not ok or not opcion:
            return

        try:
            if opcion == "Por total (%)":
                pct, ok = QInputDialog.getDouble(self, "Porcentaje total", "Ingrese porcentaje (0-100):", min=0, max=100, decimals=2)
                if not ok:
                    return
                self._reset_totals_to_base()
                carrito, descuento = AplicarDescuento.aplicar_descuento_total(self.carrito, pct)
                self.carrito = carrito
                self.descuento_aplicado = descuento
                self.descuento_pct = float(pct)
                self.descuento_tipo = 'total_pct'

            else:  # Monto fijo
                monto, ok = QInputDialog.getDouble(self, "Monto fijo", "Ingrese monto fijo a descontar:", min=0, decimals=2)
                if not ok:
                    return
                self._reset_totals_to_base()
                carrito, descuento = AplicarDescuento.aplicar_descuento_fijo(self.carrito, monto)
                self.carrito = carrito
                self.descuento_aplicado = descuento
                self.descuento_pct = 0.0
                self.descuento_tipo = 'fijo'

            self.actualizarCarrito()

        except Exception as e:
            QMessageBox.warning(self, "Error al aplicar descuento", str(e))

    def deshacer_descuento(self):
        # Resetear totales a base y limpiar metadatos de descuento
        self._reset_totals_to_base()
        self.descuento_aplicado = 0.0
        self.descuento_pct = 0.0
        self.descuento_tipo = ''
        self.actualizarCarrito()

    def aplicar_descuento_item(self, indice):
        """Abrir diálogo para aplicar descuento solo al producto en la fila 'indice'."""
        if not (0 <= indice < len(self.carrito)):
            return
        item = self.carrito[indice]
        opciones = ["Porcentaje", "Monto fijo"]
        opcion, ok = QInputDialog.getItem(self, "Descuento por producto", "Tipo:", opciones, 0, False)
        if not ok or not opcion:
            return

        try:
            if opcion == "Porcentaje":
                pct, ok2 = QInputDialog.getDouble(self, "Porcentaje", "Ingrese porcentaje (0-100):", min=0, max=100, decimals=2)
                if not ok2:
                    return
                carrito, descuento = AplicarDescuento.aplicar_descuento_producto(self.carrito, item['id'], pct)
                self.carrito = carrito
                self.descuento_aplicado = descuento
                self.descuento_pct = float(pct)
                self.descuento_tipo = 'producto'

            else:  # Monto fijo sobre este producto
                monto, ok2 = QInputDialog.getDouble(self, "Monto fijo", "Ingrese monto fijo a descontar:", min=0, decimals=2)
                if not ok2:
                    return
                base = float(item.get('base_total', item.get('precio', 0) * item.get('cantidad', 1)))
                descuento = min(monto, base)
                nuevo_total = round(max(base - descuento, 0.0), 2)
                item['total'] = nuevo_total
                item['descuento'] = round(descuento, 2)
                # recalcular descuento total como suma de diferencias
                total_desc = sum(float(it.get('descuento', 0.0) or 0.0) for it in self.carrito)
                self.descuento_aplicado = round(total_desc, 2)
                self.descuento_pct = 0.0
                self.descuento_tipo = 'fijo_producto'

            self.actualizarCarrito()
        except Exception as e:
            QMessageBox.warning(self, "Error descuento", str(e))
    
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
                metodo_pago="efectivo",
                descuento_total=self.descuento_aplicado,
                descuento_pct=self.descuento_pct,
                descuento_tipo=self.descuento_tipo
            )
            
            if success:
                QMessageBox.information(self, "Venta Exitosa", 
                                       f"✅ {mensaje}\nID: {venta_id}")
                self.limpiarCarrito()
                self.cargarProductos()  # Recargar para actualizar stock

            else:
                QMessageBox.critical(self, "Error en Venta", f"❌ {mensaje}")