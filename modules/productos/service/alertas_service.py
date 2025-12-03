
from modules.productos.models.producto_model import ProductoModel
import pandas as pd

class AlertasService:
    def __init__(self):
        self.producto_model = ProductoModel()

    def obtener_productos_bajo_stock(self):
        """
        Retorna un DataFrame con los productos cuyo stock es menor al mínimo.
        """
        df = self.producto_model.obtener_todos()
        if df.empty:
            return df
            
        # Asegurar tipos numéricos
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0)
        df['Stock Mínimo'] = pd.to_numeric(df['Stock Mínimo'], errors='coerce').fillna(0)
        
        # Filtrar productos donde Stock < Stock Mínimo
        bajo_stock = df[df['Stock'] < df['Stock Mínimo']]
        return bajo_stock

    def verificar_cambio_stock(self, stock_inicial, stock_final, stock_minimo):
        """
        Verifica si el stock bajó del mínimo (transición).
        Retorna True si antes estaba >= minimo y ahora está < minimo.
        """
        try:
            inicial = float(stock_inicial)
            final = float(stock_final)
            minimo = float(stock_minimo)
            
            return inicial >= minimo and final < minimo
        except Exception:
            return False
