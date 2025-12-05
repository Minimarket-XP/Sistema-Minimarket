from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QAbstractItemView, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import pandas as pd
from shared.styles import TITULO
from modules.productos.service.alertas_service import AlertasService
from shared.helpers import formatear_precio
from core.config import THEME_COLOR

class AlertasStockView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alertas de Stock Bajo")
        self.setFixedSize(800, 600)
        self.alertas_service = AlertasService()
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
