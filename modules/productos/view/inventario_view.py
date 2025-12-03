## Módulo de Inventario

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pandas as pd
from modules.productos.models.producto_model import ProductoModel
from shared.components.forms import ProductoForm, ImagenViewer
from shared.helpers import formatear_precio
from core.config import *
from modules.productos.view.alertas_view import AlertasStockView

# → Vista principal de inventario
class InventarioFrame(QWidget):      
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.crear_interfaz()
        self.mostrarInventario()
    
    def crear_interfaz(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título de la interfaz
        titulo = QLabel("Inventario")
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
        
        # Tabla de productos - USAR TABLA PERSONALIZADA NO EDITABLE
        self.tabla = TablaNoEditable()
        self.tabla.setStyleSheet("""
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
        columnas = ["ID", "Nombre", "Categoría", "Tipo", "Precio", "Stock", "Stock Mín"]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        
        # Configurar selección
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        
        # Ajustar tamaños de columna
        header = self.tabla.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Configurar anchos específicos
        anchos = [160, 550, 280, 100, 100, 80, 80]
        for i, ancho in enumerate(anchos):
            self.tabla.setColumnWidth(i, ancho)
        
        # Conectar MÚLTIPLES señales de selección para garantizar funcionamiento
        self.tabla.itemSelectionChanged.connect(self.mostrarImagen)
        self.tabla.currentItemChanged.connect(self.detectarCambioSeleccion)
        self.tabla.itemClicked.connect(self.detectarSeleccion)
        
        # PROTECCIÓN FINAL: Sobrescribir metodo de edición
        def no_edit(item):
            return False
        self.tabla.openPersistentEditor = no_edit
        
        main_layout.addWidget(self.tabla)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        # Crear botones
        btn_agregar = self.crearBoton("Agregar Producto", SUCCESS_COLOR, self.agregarProducto)
        btn_modificar = self.crearBoton("Modificar Producto", INFO_COLOR, self.modificarProducto)
        btn_eliminar = self.crearBoton("Eliminar Producto", ERROR_COLOR, self.eliminarProducto)
        btn_refrescar = self.crearBoton("Refrescar", "#2980b9", self.mostrarInventario)
        
        # Botón de alertas
        btn_alertas = self.crearBoton("⚠️ Alertas Stock", "#e74c3c", self.mostrarAlertas)
        
        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_modificar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addWidget(btn_refrescar)
        botones_layout.addWidget(btn_alertas)
        botones_layout.addStretch()  # Espaciador
        
        main_layout.addLayout(botones_layout)
        
        # Visor de imagen
        self.img_viewer = ImagenViewer(self)
        main_layout.addWidget(self.img_viewer)
    
    def crearBoton(self, texto, color, comando):
        btn = QPushButton(texto)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial;
            }}      
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 40)};
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(comando)
        return btn
    
# → darken_color es una función auxiliar para oscurecer colores
    def _darken_color(self, color, amount=20): #
        # Remover # si existe
        color = color.lstrip('#')
        # Convertir a RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        # Oscurecer
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def mostrarInventario(self):
        # Limpiar tabla
        self.tabla.setRowCount(0)
        
        # Obtener productos
        df = self.producto_model.obtener_todos()
        
        # Configurar número de filas
        self.tabla.setRowCount(len(df))
        
        # Llenar tabla
        for row_idx, (_, row) in enumerate(df.iterrows()):
            precio = formatear_precio(row.get("Precio", 0))
            stock_actual = int(row["Stock"]) if pd.notna(row["Stock"]) else 0
            stock_minimo = int(row["Stock Mínimo"]) if pd.notna(row["Stock Mínimo"]) else 0
            
            values = [
                str(row["ID"]), 
                str(row["Nombre"]), 
                str(row["Categoría"]), 
                str(row.get("Tipo de Corte", "")),
                precio, 
                str(stock_actual), 
                str(stock_minimo)
            ]
            
            # Determinar si hay stock bajo
            es_stock_bajo = stock_actual < stock_minimo
            
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                # IMPORTANTE: Permitir selección completa
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
                
                # Resaltar si stock es bajo
                if es_stock_bajo:
                    item.setBackground(QColor("#e74c3c")) # Rojo
                    item.setForeground(Qt.white)
                    item.setFont(self._get_bold_font())
                
                self.tabla.setItem(row_idx, col_idx, item)
        
        # Limpiar visor de imagen
        self.img_viewer.limpiar()

    def _get_bold_font(self):
        from PyQt5.QtGui import QFont
        font = QFont()
        font.setBold(True)
        return font

    def mostrarAlertas(self):
        try:
            dialog = AlertasStockView(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar alertas: {e}")
    
    def mostrarImagen(self):
        try:
            current_row = self.tabla.currentRow()
            print(f"-- Fila seleccionada: {current_row}")
            
            if current_row < 0:
                print("-- No hay fila seleccionada")
                self.img_viewer.limpiar()
                return
            
            producto_id_item = self.tabla.item(current_row, 0)  # Primera columna es ID
            if producto_id_item:
                producto_id = producto_id_item.text()
                print(f"-- ID del producto: {producto_id}")
                
                if producto_id:
                    producto = self.producto_model.obtenerPorId(producto_id)
                    print(f"-- Producto obtenido: {type(producto)}")
                    
                    if producto is not None and not producto.empty:
                        imagen_series  = producto.get("Imagen")

                        if imagen_series is not None and not imagen_series.empty:
                            imagen_path = imagen_series.item()
                            print(f"-- Ruta de imagen extraída: {imagen_path}")
                            if imagen_path and os.path.exists(imagen_path):
                                print("-- Mostrando imagen")
                                self.img_viewer.mostrarImagen(imagen_path)
                            else:
                                print("-- Imagen no encontrada, limpiando visor")
                                self.img_viewer.limpiar()
                        else:
                            print("-- Columna de imagen vacía o no encontrada")
                            self.img_viewer.limpiar()
                    else:
                        print("-- Producto vacío o None")
                        self.img_viewer.limpiar()
                else:
                    print("-- ID vacío")
                    self.img_viewer.limpiar()
            else:
                print("-- No se pudo obtener el item de ID")
                self.img_viewer.limpiar()
        except Exception as e:
            print(f"-- Error al mostrar imagen: {e}")
            import traceback
            traceback.print_exc()
            self.img_viewer.limpiar()
    
# → Detecta cambios en la selección de la tabla y actualiza la imagen mostrada
    def detectarCambioSeleccion(self, current, previous):
        print(f"-- Item actual cambió: {current}")
        self.mostrarImagen()
    
# → Detecta selección de un ítem y actualiza la imagen mostrada
    def detectarSeleccion(self, item):
        print(f"-- Item clickeado: {item}")
        self.mostrarImagen()
    
# → Agrega un nuevo producto al inventario
    def agregarProducto(self):
        try:
            print("-- Abriendo formulario agregar producto...")
            dialog = AgregarProductoForm(self)
            print("-- Formulario creado, mostrando...")
            result = dialog.exec_()  # Usar exec_() en lugar de show() para modal
            print(f"-- Formulario cerrado con resultado: {result}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir formulario: {e}")
            print(f"X - Error en agregar producto: {e}")
            import traceback
            traceback.print_exc()
    
# → Modifica el producto seleccionado en el inventario
    def modificarProducto(self):
        current_row = self.tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Modificar producto", "Selecciona un producto para modificar.")
            return
        
        try:
            print(f"-- Modificando producto en fila: {current_row}")
            producto_id_item = self.tabla.item(current_row, 0)
            if not producto_id_item:
                QMessageBox.warning(self, "Error", "No se pudo obtener el ID del producto.")
                return
                
            producto_id = producto_id_item.text()
            print(f"-- ID del producto: {producto_id}")
            
            producto_data = self.producto_model.obtenerPorId(producto_id)
            print(f"-- Datos del producto: {type(producto_data)}")
            
            if producto_data is not None and not producto_data.empty:
                print("-- Extrayendo datos antes de crear el formulario...")
                row = producto_data.iloc[0]
                id_val = row.get("ID", "")
                nombre_val = row.get("Nombre", "Nombre no encontrado")
                precio_val = row.get("Precio", 0.0)
                stock_val = row.get("Stock", 0)

                # Para la categoría, verificamos ambas formas de escribirlo como medida de seguridad
                categoria_val = row.get("Categoria", row.get("Categoría", "Sin Categoría"))

                # El constructor del formulario recibe datos limpios y garantizados
                dialog = ModificarProductoForm(self, id_val, nombre_val, precio_val, stock_val, categoria_val)
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Error", "No se encontró el producto seleccionado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir formulario: {e}")
            print(f"X - Error en modificar producto: {e}")
            import traceback
            traceback.print_exc()
    
# → Elimina el producto seleccionado del inventario
    def eliminarProducto(self):
        current_row = self.tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Eliminar producto", "Selecciona un producto para eliminar.")
            return
        
        producto_id_item = self.tabla.item(current_row, 0)
        nombre_item = self.tabla.item(current_row, 1)
        
        producto_id = producto_id_item.text()
        nombre_producto = nombre_item.text()
        
        reply = QMessageBox.question(self, "Confirmar eliminación", 
                                   f"¿Seguro que deseas eliminar el producto '{nombre_producto}'?",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.producto_model.eliminarProducto(producto_id):
                self.mostrarInventario()
                QMessageBox.information(self, "Producto eliminado", 
                                       f"Producto '{nombre_producto}' eliminado correctamente.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el producto.")

# → Formulario base para agregar/modificar productos
class AgregarProductoForm(ProductoForm):    
    def __init__(self, parent):
        self.parent_frame = parent
        super().__init__(parent, "Registrar Producto")
    
    def validarYGuardar(self):
        datos = self.validarDatos()
        if datos is None:
            return
        try:
            producto_model = ProductoModel()
            nuevo_id = producto_model.crearProducto(datos)
            QMessageBox.information(self, "Éxito", "Producto registrado correctamente.")
            self.parent_frame.mostrarInventario()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"Error: {e}")

# → Formulario para modificar productos existentes
class ModificarProductoForm(ProductoForm):
    def __init__(self, parent, prod_id, prod_nombre, prod_precio, prod_stock, prod_categoria):
        # La clase base creará todos los widgets y el diccionario 'self.entries'.
        super().__init__(parent, "Modificar Producto")
        # Guardamos el ID para cuando guardemos los cambios.
        self.parent_frame = parent
        self.producto_id = prod_id
        # Ahora rellenamos el formulario usando los nombres de widget correctos que encontramos arriba.
        # Accede al QLineEdit para "Nombre" desde el diccionario
        self.entries["Nombre"].setText(prod_nombre)
        # Accede al QLineEdit para "Precio"
        self.entries["Precio"].setText(str(prod_precio))
        # Accede al QLineEdit para "Stock inicial"
        self.entries["Stock inicial"].setText(str(prod_stock))
        index = self.categoria_cb.findText(prod_categoria)
        if index >= 0:
            self.categoria_cb.setCurrentIndex(index)

    # Esta función se llamará cuando el usuario haga clic en el botón "Guardar".
    def validarYGuardar(self):
        datos = self.validarDatos()
        if datos is None:
            return  # La validación falló

        try:
            producto_model = ProductoModel()
            producto_model.actualizarProducto(self.producto_id, datos)
            QMessageBox.information(self, "Éxito", "Producto modificado correctamente.")
            self.parent_frame.mostrarInventario()  # Actualiza la tabla
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"Ocurrió un error: {e}")
            print(f"Error detallado en modificar: {e}")

# Tabla personalizada que NUNCA permite edición pero SÍ selección
class TablaNoEditable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Configurar como no editable pero seleccionable
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Focus para selección pero no edición
        self.setFocusPolicy(Qt.StrongFocus)
    
    def edit(self, index, trigger, event):
        return False
    
    def mouseDoubleClickEvent(self, event):
        # Permitir selección en doble click pero no edición
        super(QTableWidget, self).mouseDoubleClickEvent(event)