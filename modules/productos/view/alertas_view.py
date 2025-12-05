from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QAbstractItemView, QHBoxLayout,
                             QMessageBox, QInputDialog, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import pandas as pd
from shared.styles import TITULO
from modules.productos.service.alertas_service import AlertasService
from modules.productos.models.producto_model import ProductoModel
from shared.helpers import formatear_precio
from core.config import THEME_COLOR

class AlertasStockView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alertas de Stock Bajo")
        self.setFixedSize(800, 600)
        self.alertas_service = AlertasService()
        self.producto_model = ProductoModel()
        self.crearInterfaz()
        self.cargarDatos()

    def crearInterfaz(self):
        layout = QVBoxLayout(self)
        
        titulo = QLabel("Productos con Stock Bajo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITULO)
        layout.addWidget(titulo)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Producto", "Stock Actual", "Stock Mínimo", "Déficit"])
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        
        layout.addWidget(self.tabla)
        
        # Botones
        botones_layout = QHBoxLayout()
        
        btn_agregar_stock = QPushButton("➕ Agregar Stock")
        btn_agregar_stock.clicked.connect(self.agregarStock)
        btn_agregar_stock.setStyleSheet(f"""
            QPushButton {{
                background-color: #e67e22;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #d35400;
            }}
        """)
        botones_layout.addWidget(btn_agregar_stock)
        
        btn_actualizar = QPushButton("Actualizar Lista")
        btn_actualizar.clicked.connect(self.cargarDatos)
        btn_actualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        botones_layout.addWidget(btn_actualizar)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        botones_layout.addWidget(btn_cerrar)
        
        layout.addLayout(botones_layout)

    def cargarDatos(self):
        df = self.alertas_service.obtener_productos_bajo_stock()
        self.tabla.setRowCount(len(df))
        
        for row_idx, (_, row) in enumerate(df.iterrows()):
            try:
                stock = float(row['Stock'])
                minimo = float(row['Stock Mínimo'])
                deficit = minimo - stock
                
                # Crear items
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(row['ID'])))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(row['Nombre'])))
                
                item_stock = QTableWidgetItem(str(stock))
                item_stock.setForeground(Qt.red)
                item_stock.setFont(self._get_bold_font())
                self.tabla.setItem(row_idx, 2, item_stock)
                
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(str(minimo)))
                
                item_deficit = QTableWidgetItem(f"-{deficit}")
                item_deficit.setForeground(Qt.red)
                item_deficit.setFont(self._get_bold_font())
                self.tabla.setItem(row_idx, 4, item_deficit)
                
                # Resaltar toda la fila según criticidad
                if stock <= 0:
                    # Stock agotado - rojo fuerte
                    color_fondo = QColor(255, 180, 180)
                elif stock <= minimo * 0.5:
                    # Stock crítico - rojo claro
                    color_fondo = QColor(255, 200, 200)
                else:
                    # Stock bajo - naranja claro
                    color_fondo = QColor(255, 230, 180)
                
                for col_idx in range(self.tabla.columnCount()):
                    self.tabla.item(row_idx, col_idx).setBackground(color_fondo)
                self.tabla.setItem(row_idx, 4, item_deficit)
            except Exception as e:
                print(f"Error mostrando fila alerta: {e}")

    def _get_bold_font(self):
        from PyQt5.QtGui import QFont
        font = QFont()
        font.setBold(True)
        return font

    def agregarStock(self):
        """Permite incrementar el stock del producto seleccionado"""
        fila_seleccionada = self.tabla.currentRow()
        
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Sin selección", 
                              "Por favor selecciona un producto de la lista")
            return
        
        # Obtener datos del producto seleccionado
        id_producto = self.tabla.item(fila_seleccionada, 0).text()
        nombre_producto = self.tabla.item(fila_seleccionada, 1).text()
        stock_actual = float(self.tabla.item(fila_seleccionada, 2).text())
        stock_minimo = float(self.tabla.item(fila_seleccionada, 3).text())
        
        # Calcular cantidad sugerida (para alcanzar el stock mínimo + 20%)
        cantidad_sugerida = max(0, stock_minimo * 1.2 - stock_actual)
        
        # Diálogo personalizado para ingresar cantidad
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Incrementar Stock")
        dialogo.setFixedSize(400, 200)
        
        layout = QVBoxLayout(dialogo)
        
        # Información del producto
        info_label = QLabel(f"<b>Producto:</b> {nombre_producto}<br>"
                           f"<b>Stock actual:</b> {stock_actual}<br>"
                           f"<b>Stock mínimo:</b> {stock_minimo}")
        layout.addWidget(info_label)
        
        # SpinBox para cantidad
        cantidad_label = QLabel("Cantidad a agregar:")
        layout.addWidget(cantidad_label)
        
        cantidad_spin = QDoubleSpinBox()
        cantidad_spin.setMinimum(0.01)
        cantidad_spin.setMaximum(10000)
        cantidad_spin.setValue(cantidad_sugerida if cantidad_sugerida > 0 else stock_minimo)
        cantidad_spin.setDecimals(2)
        cantidad_spin.setSuffix(" unidades")
        cantidad_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 5px;
            }
        """)
        layout.addWidget(cantidad_spin)
        
        # Botones
        botones = QHBoxLayout()
        btn_aceptar = QPushButton("✓ Agregar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_aceptar.clicked.connect(dialogo.accept)
        
        btn_cancelar = QPushButton("✗ Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancelar.clicked.connect(dialogo.reject)
        
        botones.addWidget(btn_aceptar)
        botones.addWidget(btn_cancelar)
        layout.addLayout(botones)
        
        # Mostrar diálogo
        if dialogo.exec_() == QDialog.Accepted:
            cantidad_agregar = cantidad_spin.value()
            
            try:
                # Calcular nuevo stock
                nuevo_stock = stock_actual + cantidad_agregar
                
                # Actualizar en la base de datos
                self.producto_model.actualizarProducto(id_producto, {
                    'Stock': nuevo_stock
                })
                
                # Mensaje de éxito
                QMessageBox.information(self, "Stock Actualizado",
                                      f"Se agregaron {cantidad_agregar} unidades a '{nombre_producto}'.\n"
                                      f"Stock anterior: {stock_actual}\n"
                                      f"Stock nuevo: {nuevo_stock}")
                
                # Recargar la tabla
                self.cargarDatos()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"No se pudo actualizar el stock: {str(e)}")
