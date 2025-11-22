## Módulo de Ventas - Sistema Minimarket

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QSpinBox, QMessageBox, QFrame, 
                             QAbstractItemView, QHeaderView, QDialog, QDialogButtonBox,
                             QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
from core.config import *
from modules.productos.models.producto_model import ProductoModel
from modules.ventas.service.venta_service import VentaService
from modules.ventas.service.comprobante_service import ComprobanteService
from shared.helpers import formatear_precio, validar_dni, validar_ruc
from modules.productos.view.inventario_view import TablaNoEditable
import pandas as pd
from modules.productos.models.unidad_medida_model import UnidadMedidaModel

class VentasFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.venta_service = VentaService()  # Usar Service en vez de Model
        self.comprobante_service = ComprobanteService()
        self.carrito = []  # Lista de productos en el carrito
        self.total = 0.0
        self.datos_cliente = None  # Para almacenar datos del cliente temporal

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
                font-size: 28px;
                font-weight: bold;
                font-family: Roboto;
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
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 17px;
            }
        """)
        self.search_input.textChanged.connect(self.buscarProducto)
        
        btn_limpiar = QPushButton("🧹")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #0061fc;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #260805;
            }
        """)
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
        
        # Configurar selección
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_productos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setFocusPolicy(Qt.NoFocus)

        # Ajustar tamaños de columna
        header = self.tabla_productos.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Configurar anchos específicos
        anchos = [100, 560, 80, 80, 80]  # ID, Nombre, Precio, Stock, Acción
        for i, ancho in enumerate(anchos):
            self.tabla_productos.setColumnWidth(i, ancho)
        
        left_layout.addWidget(self.tabla_productos)
        
        panels_layout.addLayout(left_layout, 2)
        
        # Panel derecho - Carrito de compras (SIN QFrame envolvente)
        right_layout = QVBoxLayout()
        
        # Título del carrito
        titulo_carrito = QLabel("🛒 Carrito de Compras")
        titulo_carrito.setStyleSheet(f"qproperty-alignment: 'AlignCenter'; color: {THEME_COLOR}; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(titulo_carrito)
        
        # Tabla del carrito - DIRECTAMENTE SIN PANEL
        self.tabla_carrito = TablaNoEditable()
        self.tabla_carrito.setColumnCount(6)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Cant.", "Precio", "Total", "Promoción", "Acción"]) 
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
        
        anchosC = [220, 57, 69, 85, 140, 58]  # Producto, Cant., Precio, Total, Promoción, Acción
        for i, anchoC in enumerate(anchosC):
            self.tabla_carrito.setColumnWidth(i, anchoC)
        
        right_layout.addWidget(self.tabla_carrito)
        right_layout.setAlignment(Qt.AlignRight)
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
        btn_procesar = QPushButton("Procesar Venta")
        btn_procesar.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 12px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        btn_procesar.clicked.connect(self.procesarVenta)
        
        btn_limpiar = QPushButton("Limpiar Carrito")
        btn_limpiar.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_COLOR};
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
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
        
        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: #bdc3c7;")
        right_layout.addWidget(linea)

        # Sección compacta de API
        api_group = QGroupBox("Consulta DNI/RUC")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #95a5a6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        api_layout = QVBoxLayout()

        # Fila 1: Tipo y número
        row1 = QHBoxLayout()
        self.tipo_doc_combo = QComboBox()
        self.tipo_doc_combo.addItems(['DNI', 'RUC'])
        self.tipo_doc_combo.setStyleSheet("padding: 5px; font-size: 12px;")
        self.tipo_doc_combo.setMaximumWidth(70)

        self.num_doc_input = QLineEdit()
        self.num_doc_input.setPlaceholderText("Número...")
        self.num_doc_input.setStyleSheet("padding: 5px; font-size: 12px;")
        self.num_doc_input.setMaxLength(11)

        btn_consultar = QPushButton("🔍")
        btn_consultar.setStyleSheet(f"""
            QPushButton {{
                background-color: {INFO_COLOR};
                color: white;
                border: none;
                padding: 5px;
                font-size: 14px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        btn_consultar.setMaximumWidth(40)
        btn_consultar.clicked.connect(self.consultarDocumento)

        row1.addWidget(self.tipo_doc_combo)
        row1.addWidget(self.num_doc_input)
        row1.addWidget(btn_consultar)

        # Fila 2: Resultado
        self.resultado_api = QLabel("Sin consulta")
        self.resultado_api.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding: 5px;
            background-color: #ecf0f1;
            border-radius: 3px;
        """)
        self.resultado_api.setWordWrap(True)

        api_layout.addLayout(row1)
        api_layout.addWidget(self.resultado_api)
        api_group.setLayout(api_layout)
        right_layout.addWidget(api_group)

        panels_layout.addLayout(right_layout, 1)
        
        main_layout.addLayout(panels_layout)
    
    def crearInfoDia(self):
        resumen = self.venta_service.obtener_resumen_dia()  # Usar service
        
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; padding: 10px;")
        
        info_layout = QHBoxLayout(info_frame)
        
        titulo = QLabel("Productos Disponibles")
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 22px; font-weight: bold;")
        info_layout.addWidget(titulo)
        info_layout.addStretch()
        
        ventas_label = QLabel(f"Ventas hoy: {resumen['total_ventas']}")
        ventas_label.setStyleSheet("font-size: 15 px; font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(ventas_label)

        # Total del día
        total_label = QLabel(f"💰 Total: {formatear_precio(resumen['monto_total'])}")
        total_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #27ae60;")
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
        id_producto = str(producto["ID"])
        nombre = str(producto["Nombre"])
        precio = float(producto["Precio"])
        stock = float(producto["Stock"]) if pd.notna(producto["Stock"]) else 0  # Stock en kg
        id_unidad = str(producto["id_unidad_medida"])
        
        # Obtener información de unidad de medida
        unidad_model = UnidadMedidaModel()
        unidad_info = unidad_model.obtener_por_id(id_unidad)
        nombre_unidad = unidad_info['nombre_unidad'] if unidad_info else 'und'
        es_peso = nombre_unidad.lower() in ['g', 'kg', 'gramos', 'kilogramos', 'gramo', 'kilogramo']
       
        # Obtener cantidad actual en carrito para este producto (siempre en kg)
        cantidad_en_carrito = 0
        for item in self.carrito:
            if item["id"] == id_producto:
                cantidad_en_carrito = item["cantidad"]
                break
        
        # Calcular stock disponible (en kg)
        stock_disponible = stock - cantidad_en_carrito
        
        if stock_disponible <= 0:
            QMessageBox.warning(self, "Sin stock", 
                              f"No hay stock disponible para '{nombre}'")
            return
        
        # Mostrar diálogo para ingresar cantidad
        cantidad_input = self.mostrarDialogoCantidad(id_unidad, nombre, stock_disponible, es_peso)
        
        if cantidad_input is None or cantidad_input <= 0:
            return  # Usuario canceló o ingresó cantidad inválida
        
        # Convertir a kg si es producto por peso (viene en gramos del diálogo)
        if es_peso:
            cantidad_kg = cantidad_input / 1000.0  # Convertir gramos a kg
            cantidad_display = cantidad_input  # Para mostrar en gramos
        else:
            cantidad_kg = cantidad_input  # Ya está en unidades
            cantidad_display = cantidad_input
        
        # Verificar que no exceda el stock disponible (comparar en kg)
        if cantidad_kg > stock_disponible:
            if es_peso:
                QMessageBox.warning(self, "Stock insuficiente",
                                  f"Solo hay {stock_disponible * 1000:.0f}g disponibles de '{nombre}'")
            else:
                QMessageBox.warning(self, "Stock insuficiente",
                                  f"Solo hay {stock_disponible:.0f} unidades disponibles de '{nombre}'")
            return

        # Verificar si el producto ya está en el carrito
        for item in self.carrito:
            if item["id"] == id_producto:
                item["cantidad"] += cantidad_kg  # Siempre almacenar en kg
                item["base_total"] = item["cantidad"] * item["precio"]
                item["total"] = item["base_total"]
                # Aplicar promoción automática si existe
                try:
                    from modules.productos.service.promocion_service import PromocionService
                    PromocionService().aplicar_descuento_a_item(item)
                except Exception:
                    # No detener la operación por errores en promociones
                    pass
                break
        else:
            # Agregar nuevo producto al carrito (cantidad siempre en kg)
            nuevo_item = {
                "id": id_producto,
                "nombre": nombre,
                "cantidad": cantidad_kg,
                "precio": precio,
                "base_total": precio * cantidad_kg,
                "total": precio * cantidad_kg,
                "descuento": None,
                "es_peso": es_peso  # Guardar si es producto por peso
            }
            # Aplicar promoción automática si existe
            try:
                from modules.productos.service.promocion_service import PromocionService
                PromocionService().aplicar_descuento_a_item(nuevo_item)
            except Exception:
                pass
            self.carrito.append(nuevo_item)

        self.actualizarCarrito()
        
        # Mensaje de confirmación
        if es_peso:
            QMessageBox.information(self, "Producto agregado", 
                                  f"{cantidad_display:.0f}g de '{nombre}' agregado al carrito")
        else:
            QMessageBox.information(self, "Producto agregado", 
                                  f"{cantidad_display:.0f} unidad(es) de '{nombre}' agregado(s) al carrito")
    
# → Mostrar diálogo para ingresar cantidad según unidad de medida
    def mostrarDialogoCantidad(self, id_unidad, nombre, stock_disponible, es_peso):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cantidad de Producto")
        dialog.setFixedSize(400, 220)
        
        layout = QVBoxLayout(dialog)
        
        # Mensaje
        if es_peso:
            mensaje = QLabel(f"Ingrese el peso de '{nombre}' (en gramos):")
        else:
            mensaje = QLabel(f"Ingrese la cantidad de '{nombre}':")
        mensaje.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(mensaje)
        
        # Stock disponible
        if es_peso:
            # Convertir stock de kg a gramos para mostrar
            stock_gramos = stock_disponible * 1000
            stock_label = QLabel(f"Stock disponible: {stock_gramos:.0f}g")
        else:
            stock_label = QLabel(f"Stock disponible: {stock_disponible:.0f} unidades")
        stock_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 5px;")
        layout.addWidget(stock_label)
        
        # INPUT de acuerdo al tipo de unidad
        if es_peso:
            # Para productos por peso: usar DoubleSpinBox - solo para los de gramos o kg
            from PyQt5.QtWidgets import QDoubleSpinBox
            spin_cantidad = QDoubleSpinBox()
            spin_cantidad.setMinimum(100.0)  # Mínimo 100 gramos por pesaje
            spin_cantidad.setMaximum(stock_disponible * 1000)  # Stock en gramos (o kilos? no sé)
            spin_cantidad.setValue(100.0)
            spin_cantidad.setSingleStep(50.0)  # Incrementos de 50g en 50g
            spin_cantidad.setDecimals(2)
            spin_cantidad.setSuffix(" g")
            
            # Mensaje de mínimo 
            min_label = QLabel("Mínimo de venta: 100g - 0.1 kg")
            min_label.setStyleSheet("font-size: 11px; color: #e74c3c; margin-bottom: 5px;")
            layout.addWidget(min_label)
        else:
            # Para productos por unidad: usar SpinBox - es entero como botellas, latas, paks, etc
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
        
        # Botones
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
        
        # Mostrar diálogo y retornar valor (en gramos si es peso, en unidades si no)
        if dialog.exec_() == QDialog.Accepted:
            return spin_cantidad.value()
        return None

    def actualizarCarrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))
        self.total = 0.0
        # Resetear descuento_aplicado temporal antes de cálculo (se actualizará si existe)
        # NOTE: descuentos se aplican sobre item['total'] que debe representar el estado actual
        for row_idx, item in enumerate(self.carrito):
            # Recalcular/promocionar item antes de mostrar (asegura datos actualizados)
            try:
                from modules.productos.service.promocion_service import PromocionService
                from modules.productos.models.promocion_model import PromocionModel
                PromocionService().aplicar_descuento_a_item(item)
            except Exception:
                # Silenciar errores en promociones para no romper la vista
                pass

            self.tabla_carrito.setItem(row_idx, 0, QTableWidgetItem(item["nombre"]))
            
            # Mostrar cantidad en gramos si es producto por peso, sino en unidades
            if item.get("es_peso", False):
                cantidad_display = f"{item['cantidad'] * 1000:.0f}g"  # Convertir kg a gramos
            else:
                cantidad_display = str(int(item["cantidad"]))
            self.tabla_carrito.setItem(row_idx, 1, QTableWidgetItem(cantidad_display))
            
            self.tabla_carrito.setItem(row_idx, 2, QTableWidgetItem(formatear_precio(item["precio"])))
            self.tabla_carrito.setItem(row_idx, 3, QTableWidgetItem(formatear_precio(item.get("total", 0))))

            # Promoción: mostrar badge si existe
            try:
                from modules.productos.models.promocion_model import PromocionModel
                id_prom = item.get('id_promocion')
                if id_prom:
                    prom = PromocionModel().obtener_por_id(id_prom)
                    if prom:
                        prom_name = prom.get('nombre', '')
                        prom_pct = prom.get('descuento', item.get('descuento_pct_aplicado', 0))
                        promo_label = QLabel(f"{prom_name} ({prom_pct:.0f}% )")
                        promo_label.setStyleSheet("background-color:#27ae60; color:white; padding:4px 8px; border-radius:8px; font-weight:bold;")
                        promo_label.setToolTip(f"Promoción: {prom_name}\nDescuento: {prom_pct:.0f}%")
                    else:
                        promo_label = QLabel("")
                else:
                    promo_label = QLabel("")
            except Exception:
                promo_label = QLabel("")

            promo_label.setAlignment(Qt.AlignCenter)
            self.tabla_carrito.setCellWidget(row_idx, 4, promo_label)

            # Acciones: solo botón remover
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            # Botón remover
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
            self.tabla_carrito.setCellWidget(row_idx, 5, action_widget)
            self.total += float(item.get("total", 0))

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
        # Limpiar también datos del cliente temporal
        self.datos_cliente = None
        self.num_doc_input.clear()
        self.resultado_api.setText("Sin consulta")
        self.resultado_api.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
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
            # Procesar la venta usando el SERVICE (lógica de negocio)
            success, venta_id, mensaje = self.venta_service.procesar_venta_completa(
                carrito=self.carrito,
                empleado_id=1,  # Por ahora usamos empleado 1 por defecto
                metodo_pago="efectivo"
            )
            
            if success:
                # Preguntar si desea emitir comprobante
                if self.datos_cliente:
                    tipo_comp = "Boleta" if self.datos_cliente.get('tipo') == 'boleta' else "Factura"
                    cliente_info = self.datos_cliente.get('nombre_completo') if tipo_comp == "Boleta" else self.datos_cliente.get('razon_social')

                    reply_comp = QMessageBox.question(
                        self,
                        "Emitir Comprobante",
                        f"Venta exitosa ✅\nID: {venta_id}\n\n¿Emitir {tipo_comp} para:\n{cliente_info}?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply_comp == QMessageBox.Yes:
                        self.emitirComprobante(venta_id)
                else:
                    QMessageBox.information(self, "Venta Exitosa",
                                           f"✅ {mensaje}\nID: {venta_id}\n\n💡 Tip: Consulta DNI/RUC antes de vender para emitir comprobante automáticamente.")

                self.limpiarCarrito()
                self.cargarProductos()  # Recargar para actualizar stock
            else:
                QMessageBox.critical(self, "Error en Venta", f"❌ {mensaje}")

    def emitirComprobante(self, venta_id):
        """Emite comprobante (boleta o factura) para una venta"""
        try:
            tipo = 'boleta' if self.datos_cliente.get('tipo') == 'boleta' else 'factura'
            resultado = self.comprobante_service.emitir_comprobante(venta_id, tipo, self.datos_cliente)

            if resultado.get('success'):
                codigo = resultado.get('codigo', '')
                QMessageBox.information(
                    self,
                    "Comprobante Emitido",
                    f"✅ {tipo.upper()} emitida correctamente\n\nCódigo: {codigo}"
                )
            else:
                QMessageBox.warning(self, "Error", f"No se pudo emitir el comprobante:\n{resultado.get('error', 'Error desconocido')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al emitir comprobante:\n{str(e)}")

    def consultarDocumento(self):
        """Consulta DNI o RUC usando la API"""
        tipo = self.tipo_doc_combo.currentText()
        numero = self.num_doc_input.text().strip()

        # Validaciones usando helpers
        if tipo == 'DNI':
            valido, mensaje = validar_dni(numero)
            if not valido:
                self.resultado_api.setText(f"⚠️ {mensaje}")
                self.resultado_api.setStyleSheet("font-size: 11px; color: #e74c3c; padding: 5px; background-color: #fadbd8; border-radius: 3px;")
                return
        else:  # RUC
            valido, mensaje = validar_ruc(numero)
            if not valido:
                self.resultado_api.setText(f"⚠️ {mensaje}")
                self.resultado_api.setStyleSheet("font-size: 11px; color: #e74c3c; padding: 5px; background-color: #fadbd8; border-radius: 3px;")
                return

        # Consultar
        self.resultado_api.setText("🔄 Consultando...")
        self.resultado_api.setStyleSheet("font-size: 11px; color: #3498db; padding: 5px; background-color: #d6eaf8; border-radius: 3px;")

        resultado = self.comprobante_service.obtener_datos_documento(numero, tipo)

        if resultado.get('success'):
            origen = resultado.get('origen', 'api')
            icono_origen = "💾" if origen == 'cache' else "🌐"

            if tipo == 'DNI':
                nombre = resultado.get('nombre_completo', 'N/A')
                texto = f"✅ {icono_origen} {nombre}"
                self.datos_cliente = {
                    'num_documento': numero,
                    'nombre_completo': nombre,
                    'tipo': 'boleta'
                }
            else:  # RUC
                razon = resultado.get('razon_social', 'N/A')
                texto = f"✅ {icono_origen} {razon[:40]}..." if len(razon) > 40 else f"✅ {icono_origen} {razon}"
                self.datos_cliente = {
                    'ruc': numero,
                    'razon_social': razon,
                    'direccion': resultado.get('direccion', ''),
                    'tipo': 'factura'
                }

            self.resultado_api.setText(texto)
            self.resultado_api.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px; background-color: #d5f4e6; border-radius: 3px;")
        else:
            error = resultado.get('error', 'Error desconocido')
            self.resultado_api.setText(f"❌ {error}")
            self.resultado_api.setStyleSheet("font-size: 11px; color: #e74c3c; padding: 5px; background-color: #fadbd8; border-radius: 3px;")
            self.datos_cliente = None

