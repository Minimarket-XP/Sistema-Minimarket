## Módulo de Ventas - Sistema Minimarket

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QSpinBox, QMessageBox, QFrame, 
                             QAbstractItemView, QHeaderView, QInputDialog, QComboBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from core.config import *
from modules.productos.models.producto_model import ProductoModel
from modules.ventas.service.venta_service import VentaService
from shared.helpers import formatear_precio, consulta_dni_api, consulta_ruc_api
from modules.ventas.service.descuentos_service import AplicarDescuento
from modules.productos.view.inventario_view import TablaNoEditable
from modules.clientes.models.cliente_model import ClienteModel
from shared.components.forms import ClienteForm
from modules.ventas.service.comprobantes_api import ComprobantesAPI
import pandas as pd
from modules.productos.models.unidad_medida_model import UnidadMedidaModel

class VentasFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.venta_service = VentaService()
        self.cliente_model = ClienteModel()
        self.comprobantes_api = ComprobantesAPI()
        self.carrito = []
        self.total = 0.0
        self.descuento_aplicado = 0.0
        self.descuento_pct = 0.0
        self.descuento_tipo = ""
        self.tipo_comprobante = 'Boleta'
        self.cliente_id = 1
        
        self.crearInterfaz()
        self.cargarProductos()
    
    def crearInterfaz(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
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
        
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(15)

        left_layout = QVBoxLayout()
        info_frame = self.crearInfoDia()
        left_layout.addWidget(info_frame)
        
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

        columnas = ["ID", "Nombre", "Precio", "Stock", "Acción"]        
        self.tabla_productos.setColumnCount(len(columnas))
        self.tabla_productos.setHorizontalHeaderLabels(columnas)
        
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setFocusPolicy(Qt.NoFocus)

        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        
        anchos = [80, 600, 80, 80, 80]
        for i, ancho in enumerate(anchos):
            self.tabla_productos.setColumnWidth(i, ancho)
        
        left_layout.addWidget(self.tabla_productos)
        panels_layout.addLayout(left_layout, 2)
        
        right_layout = QVBoxLayout()
        titulo_carrito = QLabel("🛒 Carrito de Compras")
        titulo_carrito.setStyleSheet(f"color: {THEME_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(titulo_carrito)
        
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

        anchosC = [243, 57, 69, 85, 58]
        for i, anchoC in enumerate(anchosC):
            self.tabla_carrito.setColumnWidth(i, anchoC)
        
        right_layout.addWidget(self.tabla_carrito)

        comprobante_layout = QVBoxLayout()
        titulo_comp = QLabel("🧾 Comprobante")
        titulo_comp.setStyleSheet(f"color: {THEME_COLOR}; font-size: 16px; font-weight: bold;")
        comprobante_layout.addWidget(titulo_comp)
        fila1 = QHBoxLayout()
        self.tipo_cb = QComboBox()
        self.tipo_cb.addItems(["Boleta", "Factura"])
        self.tipo_cb.currentTextChanged.connect(self._on_tipo_changed)
        fila1.addWidget(QLabel("Tipo:"))
        fila1.addWidget(self.tipo_cb)
        comprobante_layout.addLayout(fila1)
        fila2 = QHBoxLayout()
        self.doc_input = QLineEdit()
        self.doc_input.setPlaceholderText("DNI (8) o RUC (11)")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscarCliente)
        btn_nuevo = QPushButton("Nuevo")
        btn_nuevo.clicked.connect(self.nuevoCliente)
        fila2.addWidget(QLabel("Documento:"))
        fila2.addWidget(self.doc_input)
        fila2.addWidget(btn_buscar)
        fila2.addWidget(btn_nuevo)
        comprobante_layout.addLayout(fila2)
        self.lbl_cliente = QLabel("Cliente: Genérico")
        comprobante_layout.addWidget(self.lbl_cliente)
        right_layout.addLayout(comprobante_layout)

        discount_layout = QHBoxLayout()
        discount_layout.addStretch()

        btn_descuento = QPushButton("Aplicar Descuento")
        btn_descuento.clicked.connect(self.abrir_dialogo_aplicar_descuento)
        discount_layout.addWidget(btn_descuento)

        btn_deshacer = QPushButton("Deshacer Descuento")
        btn_deshacer.clicked.connect(self.deshacer_descuento)
        discount_layout.addWidget(btn_deshacer)
        btn_descuento.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)

        btn_deshacer.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)

        right_layout.addLayout(discount_layout)

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
        resumen = self.venta_service.obtener_resumen_dia()
        
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

        total_label = QLabel(f"💰 Total: {formatear_precio(resumen['monto_total'])}")
        total_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        info_layout.addWidget(total_label)
        
        return info_frame
    
    def cargarProductos(self):
        df = self.producto_model.obtener_todos()
        productos_disponibles = []
        for _, row in df.iterrows():
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            if stock > 0:
                productos_disponibles.append(row)
        self.tabla_productos.setRowCount(len(productos_disponibles))
        for row_idx, row in enumerate(productos_disponibles):
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            self.tabla_productos.setItem(row_idx, 0, QTableWidgetItem(str(row["ID"])))
            self.tabla_productos.setItem(row_idx, 1, QTableWidgetItem(str(row["Nombre"])))
            precio_texto = formatear_precio(row["Precio"])
            self.tabla_productos.setItem(row_idx, 2, QTableWidgetItem(precio_texto))
            self.tabla_productos.setItem(row_idx, 3, QTableWidgetItem(str(stock)))
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
        productos_encontrados = []
        for _, row in df.iterrows():
            stock = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            if stock > 0:
                productos_encontrados.append(row)
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
        id_producto = str(producto["ID"])
        nombre = str(producto["Nombre"])
        precio = float(producto["Precio"])
        stock = float(producto["Stock"]) if pd.notna(producto["Stock"]) else 0
        id_unidad = str(producto.get("id_unidad_medida", ""))
        unidad_model = UnidadMedidaModel()
        unidad_info = unidad_model.obtener_por_id(id_unidad) if id_unidad else None
        nombre_unidad = unidad_info['nombre_unidad'] if unidad_info else 'und'
        es_peso = nombre_unidad.lower() in ['g', 'kg', 'gramos', 'kilogramos', 'gramo', 'kilogramo']
        cantidad_en_carrito = 0
        for item in self.carrito:
            if item["id"] == id_producto:
                cantidad_en_carrito = item["cantidad"]
                break
        stock_disponible = stock - cantidad_en_carrito
        if stock_disponible <= 0:
            QMessageBox.warning(self, "Sin stock", f"No hay stock disponible para '{nombre}'")
            return
        cantidad_input = self.mostrarDialogoCantidad(id_unidad, nombre, stock_disponible, es_peso)
        if cantidad_input is None or cantidad_input <= 0:
            return
        if es_peso:
            cantidad_kg = cantidad_input / 1000.0
            cantidad_display = cantidad_input
        else:
            cantidad_kg = cantidad_input
            cantidad_display = cantidad_input
        if cantidad_kg > stock_disponible:
            if es_peso:
                QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock_disponible * 1000:.0f}g disponibles de '{nombre}'")
            else:
                QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {stock_disponible:.0f} unidades disponibles de '{nombre}'")
            return
        for item in self.carrito:
            if item["id"] == id_producto:
                item["cantidad"] += cantidad_kg
                item["base_total"] = item["cantidad"] * item["precio"]
                item["total"] = item["base_total"]
                break
        else:
            self.carrito.append({
                "id": id_producto,
                "nombre": nombre,
                "cantidad": cantidad_kg,
                "precio": precio,
                "base_total": precio * cantidad_kg,
                "total": precio * cantidad_kg,
                "descuento": None,
                "es_peso": es_peso
            })
        self.actualizarCarrito()
        if es_peso:
            QMessageBox.information(self, "Producto agregado", f"{cantidad_display:.0f}g de '{nombre}' agregado al carrito")
        else:
            QMessageBox.information(self, "Producto agregado", f"{cantidad_display:.0f} unidad(es) de '{nombre}' agregado(s) al carrito")
    
    def mostrarDialogoCantidad(self, id_unidad, nombre, stock_disponible, es_peso):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cantidad de Producto")
        dialog.setFixedSize(400, 220)
        layout = QVBoxLayout(dialog)
        if es_peso:
            mensaje = QLabel(f"Ingrese el peso de '{nombre}' (en gramos):")
        else:
            mensaje = QLabel(f"Ingrese la cantidad de '{nombre}':")
        mensaje.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(mensaje)
        if es_peso:
            stock_gramos = stock_disponible * 1000
            stock_label = QLabel(f"Stock disponible: {stock_gramos:.0f}g")
        else:
            stock_label = QLabel(f"Stock disponible: {stock_disponible:.0f} unidades")
        stock_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 5px;")
        layout.addWidget(stock_label)
        if es_peso:
            from PyQt5.QtWidgets import QDoubleSpinBox
            spin_cantidad = QDoubleSpinBox()
            spin_cantidad.setMinimum(100.0)
            spin_cantidad.setMaximum(stock_disponible * 1000)
            spin_cantidad.setValue(100.0)
            spin_cantidad.setSingleStep(50.0)
            spin_cantidad.setDecimals(2)
            spin_cantidad.setSuffix(" g")
            min_label = QLabel("Mínimo de venta: 100g - 0.1 kg")
            min_label.setStyleSheet("font-size: 11px; color: #e74c3c; margin-bottom: 5px;")
            layout.addWidget(min_label)
        else:
            from PyQt5.QtWidgets import QSpinBox
            spin_cantidad = QSpinBox()
            spin_cantidad.setMinimum(1)
            spin_cantidad.setMaximum(int(stock_disponible))
            spin_cantidad.setValue(1)
        spin_cantidad.setStyleSheet("""
            QSpinBox, QDoubleSpinBox {
                padding: 8px;
                font-size: 16px;
                border: 2px solid #3498db;
                border-radius: 5px;
            }
        """)
        layout.addWidget(spin_cantidad)
        from PyQt5.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec_() == QDialog.Accepted:
            return spin_cantidad.value()
        return None

    def actualizarCarrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        self.total = 0.0
        for row_idx, item in enumerate(self.carrito):
            self.tabla_carrito.setItem(row_idx, 0, QTableWidgetItem(item["nombre"]))
            if item.get("es_peso", False):
                cantidad_display = f"{item['cantidad'] * 1000:.0f}g"
            else:
                cantidad_display = str(int(item["cantidad"]))
            self.tabla_carrito.setItem(row_idx, 1, QTableWidgetItem(cantidad_display))
            self.tabla_carrito.setItem(row_idx, 2, QTableWidgetItem(formatear_precio(item["precio"])))
            self.tabla_carrito.setItem(row_idx, 3, QTableWidgetItem(formatear_precio(item.get("total", item.get("base_total", 0)))))

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
            action_widget.setLayout(action_layout)
            self.tabla_carrito.setCellWidget(row_idx, 4, action_widget)
            self.total += float(item.get("total", item.get('base_total', 0)))

        if self.descuento_aplicado and float(self.descuento_aplicado) > 0:
            self.label_total.setText(
                f"Total: {formatear_precio(self.total)}  (Descuento: {formatear_precio(self.descuento_aplicado)})")
        else:
            self.label_total.setText(f"Total: {formatear_precio(self.total)}")

    def _reset_totals_to_base(self):
        for item in self.carrito:
            item['total'] = float(item.get('base_total', item.get('precio', 0) * item.get('cantidad', 1)))
            item['descuento'] = None

    def abrir_dialogo_aplicar_descuento(self):
        opciones = ["Por total (%)", "Monto fijo"]
        from PyQt5.QtWidgets import QInputDialog
        opcion, ok = QInputDialog.getItem(self, "Aplicar Descuento", "Selecciona opción:", opciones, 0, False)
        if not ok or not opcion:
            return
        try:
            if opcion == "Por total (%)":
                pct, ok2 = QInputDialog.getDouble(self, "Porcentaje total", "Ingrese porcentaje (0-100):", min=0, max=100, decimals=2)
                if not ok2:
                    return
                self._reset_totals_to_base()
                carrito, descuento = AplicarDescuento.aplicar_descuento_total(self.carrito, pct)
                self.carrito = carrito
                self.descuento_aplicado = descuento
                self.descuento_pct = float(pct)
                self.descuento_tipo = 'total_pct'
            else:
                monto, ok2 = QInputDialog.getDouble(self, "Monto fijo", "Ingrese monto fijo a descontar:", min=0, decimals=2)
                if not ok2:
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
        self._reset_totals_to_base()
        self.descuento_aplicado = 0.0
        self.descuento_pct = 0.0
        self.descuento_tipo = ''
        self.actualizarCarrito()

    def aplicar_descuento_item(self, indice):
        if not (0 <= indice < len(self.carrito)):
            return
        item = self.carrito[indice]
        from PyQt5.QtWidgets import QInputDialog
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
            else:
                monto, ok2 = QInputDialog.getDouble(self, "Monto fijo", "Ingrese monto fijo a descontar:", min=0, decimals=2)
                if not ok2:
                    return
                base = float(item.get('base_total', item.get('precio', 0) * item.get('cantidad', 1)))
                descuento = min(monto, base)
                nuevo_total = round(max(base - descuento, 0.0), 2)
                item['total'] = nuevo_total
                item['descuento'] = round(descuento, 2)
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
            QMessageBox.information(self, "Producto removido", f"'{producto_removido['nombre']}' removido del carrito")
    
    def limpiarCarrito(self):
        self.carrito.clear()
        self.actualizarCarrito()
        QMessageBox.information(self, "Carrito limpio", "Todos los productos han sido removidos del carrito")
    
    def procesarVenta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "Agrega productos al carrito antes de procesar la venta")
            return
        if self.tipo_comprobante == 'Factura' and not self.cliente_id:
            QMessageBox.warning(self, "Cliente requerido", "Seleccione un cliente con RUC para la factura")
            return
        reply = QMessageBox.question(self, "Procesar Venta", f"¿Procesar venta por {formatear_precio(self.total)}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, venta_id, mensaje = self.venta_service.procesar_venta_completa(
                carrito=self.carrito,
                empleado_id=1,
                metodo_pago="efectivo"
            )
            if success:
                tipo = 'BOLETA' if self.tipo_comprobante == 'Boleta' else 'FACTURA'
                cliente_id = self.cliente_id or 1
                comp = self.comprobantes_api.emitir(venta_id, tipo, cliente_id)
                QMessageBox.information(self, "Venta Exitosa", f"✅ {mensaje}\nID: {venta_id}\n{comp['tipo']} {comp['serie']}-{comp['numero']}")
                self.limpiarCarrito()
                self.cargarProductos()
            else:
                QMessageBox.critical(self, "Error en Venta", f"❌ {mensaje}")

    def _on_tipo_changed(self, tipo):
        self.tipo_comprobante = tipo
        if tipo == 'Boleta' and not self.doc_input.text().strip():
            self.cliente_id = 1
            self.lbl_cliente.setText("Cliente: Genérico")
        
    def buscarCliente(self):
        doc = self.doc_input.text().strip()
        if self.tipo_comprobante == 'Boleta':
            if not doc:
                self.cliente_id = 1
                self.lbl_cliente.setText("Cliente: Genérico")
                return
            if not self.cliente_model.validar_documento('DNI', doc):
                QMessageBox.warning(self, "DNI inválido", "El DNI debe tener 8 dígitos")
                return
            c = self.cliente_model.obtener_cliente(doc)
            if c:
                self.cliente_id = c['id']
                self.lbl_cliente.setText(f"Cliente: {c['nombre']}")
            else:
                info = consulta_dni_api(doc)
                if not info:
                    QMessageBox.information(self, "No encontrado", "No existe el DNI. Usará Cliente Genérico")
                    self.cliente_id = 1
                    self.lbl_cliente.setText("Cliente: Genérico")
                    return
                data = info.get('data') if isinstance(info, dict) else None
                if not data:
                    QMessageBox.information(self, "No encontrado", "No existe el DNI. Usará Cliente Genérico")
                    self.cliente_id = 1
                    self.lbl_cliente.setText("Cliente: Genérico")
                    return
                nombre = (data.get('nombre_completo') or ' '.join([x for x in [data.get('nombres'), data.get('apellido_paterno'), data.get('apellido_materno')] if x])).strip() or f"DNI {doc}"
                try:
                    cid = self.cliente_model.crear_cliente('DNI', doc, nombre)
                    self.cliente_id = cid
                    self.lbl_cliente.setText(f"Cliente: {nombre}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))
        else:
            if not self.cliente_model.validar_documento('RUC', doc):
                QMessageBox.warning(self, "RUC inválido", "El RUC debe tener 11 dígitos")
                return
            c = self.cliente_model.obtener_cliente(doc)
            if c:
                self.cliente_id = c['id']
                self.lbl_cliente.setText(f"Cliente: {c['nombre']}")
            else:
                info = consulta_ruc_api(doc)
                if not info:
                    QMessageBox.information(self, "No disponible", "No fue posible consultar el RUC en la API")
                    self.nuevoCliente(prefill={'tipo_documento':'RUC','num_documento':doc})
                    return
                data = info.get('data') if isinstance(info, dict) else None
                if not data:
                    QMessageBox.information(self, "No disponible", "Respuesta de API sin datos para el RUC")
                    self.nuevoCliente(prefill={'tipo_documento':'RUC','num_documento':doc})
                    return
                nombre = (data.get('nombre_o_razon_social') or data.get('razonSocial') or data.get('razon_social') or '').strip() or f"RUC {doc}"
                direccion = (data.get('direccion') or data.get('direccion_completa') or '').strip()
                try:
                    cid = self.cliente_model.crear_cliente('RUC', doc, nombre, direccion=direccion)
                    self.cliente_id = cid
                    self.lbl_cliente.setText(f"Cliente: {nombre}")
                except Exception as e:
                    c2 = self.cliente_model.obtener_cliente(doc)
                    if c2:
                        self.cliente_id = c2['id']
                        self.lbl_cliente.setText(f"Cliente: {c2['nombre']}")
                    else:
                        QMessageBox.warning(self, "Error", str(e))

    def nuevoCliente(self, prefill=None):
        datos = None
        if prefill:
            datos = {'tipo_documento': prefill.get('tipo_documento',''), 'num_documento': prefill.get('num_documento',''), 'nombre':'', 'direccion':'', 'telefono':'', 'email':''}
        dialog = ClienteForm(self, "Registrar Cliente", datos)
        def guardar():
            d = dialog.validarDatos()
            if not d:
                return
            try:
                cid = self.cliente_model.crear_cliente(d['tipo_documento'], d['num_documento'], d['nombre'], d['direccion'], d['telefono'], d['email'])
                self.cliente_id = cid
                self.lbl_cliente.setText(f"Cliente: {d['nombre']}")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
        dialog.validarYGuardar = guardar
        dialog.exec_()