from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QPushButton, QAbstractItemView)
from PyQt5.QtCore import Qt
import pandas as pd
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
        titulo.setStyleSheet(f"color: {THEME_COLOR}; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
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
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_cerrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(btn_cerrar)

    def cargarDatos(self):
        df = self.alertas_service.obtener_productos_bajo_stock()
        self.tabla.setRowCount(len(df))
        
        for row_idx, (_, row) in enumerate(df.iterrows()):
            try:
                stock = float(row['Stock'])
                minimo = float(row['Stock Mínimo'])
                deficit = minimo - stock
                
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
            except Exception as e:
                print(f"Error mostrando fila alerta: {e}")

    def _get_bold_font(self):
        from PyQt5.QtGui import QFont
        font = QFont()
        font.setBold(True)
        return font
