## Módulo de Inventario

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QColor, QPixmap
import pandas as pd
import os
from shared.styles import TablaNoEditableCSS, TITULO
from modules.productos.models.producto_model import ProductoModel
from shared.components.forms import ProductoForm, ImagenViewer
from shared.helpers import formatear_precio
from core.config import *

# → Interfaz para gestionar el inventario de productos
class InventarioFrame(QWidget):      
    def __init__(self, parent):
        super().__init__(parent)
        
        self.producto_model = ProductoModel()
        self.crearInterfaz()
        self.mostrarInventario()
    
    def crearInterfaz(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Inventario")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITULO)
        main_layout.addWidget(titulo)
        
        # Tabla de productos - USAR TABLA PERSONALIZADA NO EDITABLE
        self.tabla = TablaNoEditable()
        self.tabla.setStyleSheet(TablaNoEditableCSS)

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
        
        # Bloquear edición doble clic
        def no_edit(item):
            return False
        self.tabla.itemDoubleClicked.connect(no_edit)
        
        # Habilitar tracking del mouse para tooltips
        self.tabla.setMouseTracking(True)
        self.tabla.viewport().setMouseTracking(True)
        self.tabla.viewport().installEventFilter(self)
        
        # Tooltip flotante para imágenes
        self.tooltip_label = None
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.mostrarTooltipImagen)
        self.current_hover_row = -1
        
        main_layout.addWidget(self.tabla)
        
        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        btn_agregar = self.crearBoton("Agregar", SUCCESS_COLOR, self.agregarProducto)
        btn_modificar = self.crearBoton("Modificar", INFO_COLOR, self.modificarProducto)
        btn_eliminar = self.crearBoton("Eliminar", ERROR_COLOR, self.eliminarProducto)
        
        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_modificar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addStretch()
        
        main_layout.addLayout(botones_layout)
    
# → Crear botón con estilo consistente
    def crearBoton(self, texto, color, comando):
        btn = QPushButton(texto)
        btn.clicked.connect(comando)
        darker_color = self._darken_color(color)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {darker_color};
            }}
        """)
        return btn
    
# → darken_color es una función auxiliar para oscurecer colores
    def _darken_color(self, color, amount=20):
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    
# → Filtro de eventos para detectar hover del mouse
    def eventFilter(self, obj, event):
        if obj == self.tabla.viewport():
            if event.type() == event.MouseMove:
                pos = event.pos()
                item = self.tabla.itemAt(pos)
                if item:
                    row = item.row()
                    if row != self.current_hover_row:
                        self.current_hover_row = row
                        self.hover_timer.start(500)  # Delay de 500ms
                else:
                    self.ocultarTooltipImagen()
                    self.current_hover_row = -1
            elif event.type() == event.Leave:
                self.ocultarTooltipImagen()
                self.current_hover_row = -1
        return super().eventFilter(obj, event)
    
# → Muestra tooltip flotante con imagen del producto
    def mostrarTooltipImagen(self):
        if self.current_hover_row < 0:
            return
        
        try:
            id_producto = self.tabla.item(self.current_hover_row, 0).text()
            df = self.producto_model.obtener_todos()
            producto = df[df["ID"] == id_producto].iloc[0]
            
            ruta_imagen = producto.get("Imagen", "")
            if not ruta_imagen or not os.path.exists(ruta_imagen):
                return
            
            # Crear tooltip si no existe
            if self.tooltip_label is None:
                self.tooltip_label = QLabel(self)
                self.tooltip_label.setWindowFlags(Qt.ToolTip)
                self.tooltip_label.setStyleSheet("""
                    QLabel {
                        background-color: white;
                        border: 2px solid #3498db;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
            
            # Cargar y escalar imagen
            pixmap = QPixmap(ruta_imagen)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.tooltip_label.setPixmap(scaled_pixmap)
                
                # Posicionar tooltip cerca del cursor
                cursor_pos = self.tabla.viewport().mapToGlobal(self.tabla.viewport().mapFromGlobal(self.cursor().pos()))
                self.tooltip_label.move(cursor_pos.x() + 20, cursor_pos.y() + 20)
                self.tooltip_label.show()
        except Exception as e:
            print(f"Error mostrando tooltip: {e}")
    
# → Oculta el tooltip flotante
    def ocultarTooltipImagen(self):
        if self.tooltip_label:
            self.tooltip_label.hide()
        self.hover_timer.stop()
    
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
        # Llenar celdas
            values = [
                str(row["ID"]), 
                str(row["Nombre"]), 
                str(row["Categoría"]), 
                str(row.get("Tipo de Corte", "")),
                precio, 
                str(stock_actual), 
                str(stock_minimo)
            ]
        # Llenar fila en la tabla
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                # IMPORTANTE: Permitir selección completa
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
                self.tabla.setItem(row_idx, col_idx, item)
            # Resaltar productos con stock bajo del mínimo con fondo rojo/naranja
            if stock_actual <= stock_minimo:
                # Stock crítico - fondo rojo claro
                color_fondo = QColor(255, 200, 200)  # Rojo claro
                for col_idx in range(self.tabla.columnCount()):
                    self.tabla.item(row_idx, col_idx).setBackground(color_fondo)
            elif stock_actual <= stock_minimo * 1.5:
                # Stock bajo - fondo naranja claro
                color_fondo = QColor(255, 230, 180)  # Naranja claro
                for col_idx in range(self.tabla.columnCount()):
                    self.tabla.item(row_idx, col_idx).setBackground(color_fondo)

# → Agrega un nuevo producto al inventario
    def agregarProducto(self):
        formulario = AgregarProductoForm(self)
        formulario.exec_()

# → Modifica el producto seleccionado en el inventario
    def modificarProducto(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Sin selección", "Selecciona un producto de la tabla")
            return
        
        id_producto = self.tabla.item(fila_seleccionada, 0).text()
        formulario = ModificarProductoForm(self, id_producto)
        formulario.exec_()

# → Elimina el producto seleccionado del inventario
    def eliminarProducto(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Sin selección", "Selecciona un producto de la tabla")
            return
        
        id_producto = self.tabla.item(fila_seleccionada, 0).text()
        nombre_producto = self.tabla.item(fila_seleccionada, 1).text()
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el producto '{nombre_producto}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                self.producto_model.eliminarProducto(id_producto)
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.mostrarInventario()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {str(e)}")


# → Formulario base para agregar/modificar productos
class AgregarProductoForm(ProductoForm):    
    def __init__(self, parent_frame):
        super().__init__(None)
        self.parent_frame = parent_frame
        self.setWindowTitle("Agregar Producto")
    
    def validarYGuardar(self):
        datos = self.validarDatos()
        if datos is None:
            return  # La validación falló
        
        try:
            producto_model = ProductoModel()
            producto_model.crearProducto(datos)
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
            self.parent_frame.mostrarInventario()  # Actualiza la tabla
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"Ocurrió un error: {e}")
            print(f"Error detallado: {e}")


# → Formulario para modificar productos existentes
class ModificarProductoForm(ProductoForm):
    def __init__(self, parent_frame, producto_id):
        super().__init__(None)
        self.parent_frame = parent_frame
        self.producto_id = producto_id
        self.setWindowTitle("Modificar Producto")
        self.cargarDatosProducto()
    
    def cargarDatosProducto(self):
        """Carga los datos del producto en los campos del formulario"""
        try:
            producto_model = ProductoModel()
            df = producto_model.obtener_todos()
            producto = df[df["ID"] == self.producto_id].iloc[0]
            
            # Llenar campos
            self.entries["Nombre"].setText(str(producto["Nombre"]))
            
            # Seleccionar categoría en combobox
            categoria = str(producto["Categoría"])
            index_cat = self.categoria_cb.findText(categoria)
            if index_cat >= 0:
                self.categoria_cb.setCurrentIndex(index_cat)
            
            # Tipo de corte
            tipo_corte = str(producto.get("Tipo de Corte", ""))
            index_corte = self.corte_cb.findText(tipo_corte)
            if index_corte >= 0:
                self.corte_cb.setCurrentIndex(index_corte)
            
            self.entries["Precio"].setText(str(producto["Precio"]))
            self.entries["Stock inicial"].setText(str(int(producto["Stock"])))
            self.entries["Stock Mínimo"].setText(str(int(producto["Stock Mínimo"])))
            
            # Cargar imagen si existe
            ruta_imagen = producto.get("Imagen", "")
            if ruta_imagen:
                self.img_path = ruta_imagen
                self.img_viewer.cargar_imagen(ruta_imagen)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos: {e}")
            print(f"Error cargando datos: {e}")
    
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

# Tabla no editable personalizada
class TablaNoEditable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
