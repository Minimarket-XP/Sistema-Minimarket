## Modelo para manejar los datos de productos

import shutil
from views.settings import *
from models.base_model import BaseModel
from db.database import db
import pandas as pd

class ProductoModel(BaseModel):
    def __init__(self):
        # Definir columnas de la tabla productos
        columns = ['id', 'nombre', 'categoria', 'tipo_corte', 'precio', 'stock', 'stock_minimo', 'imagen']
        super().__init__('productos', columns)
        self.columnas = ["ID", "Nombre", "Categoría", "Tipo de Corte", "Precio", "Stock", "Stock Mínimo", "Imagen"]
    
    def generar_siguiente_id(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Obtener todos los IDs existentes ordenados
            cursor.execute("SELECT id FROM productos ORDER BY id ASC")
            ids_existentes = [row[0] for row in cursor.fetchall()]
            
            # Buscar el primer hueco en la secuencia
            for i in range(1, 9999):  # P0001 hasta P9999
                id_esperado = f"P{i:04d}"
                if id_esperado not in ids_existentes:
                    conn.close()
                    return id_esperado
            
            # Si no hay huecos, usar el siguiente después del último
            if ids_existentes:
                # Extraer el número del último ID
                ultimo_id = max(ids_existentes)
                ultimo_numero = int(ultimo_id[1:])  # Remover 'P' y convertir a int
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            conn.close()
            return f"P{nuevo_numero:04d}"
            
        except Exception as e:
            print(f"Error generando ID: {e}")
            # Fallback: usar timestamp
            from datetime import datetime
            return f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def obtener_todos(self):
        try:
            productos = self.get_all()
            # Convertir a formato pandas-like para compatibilidad
            import pandas as pd
            
            if not productos:
                return pd.DataFrame(columns=self.columnas)
            
            # Mapear campos de SQLite a formato Excel esperado
            data = []
            for producto in productos:
                data.append({
                    "ID": producto.get('id', ''),
                    "Nombre": producto.get('nombre', ''),
                    "Categoría": producto.get('categoria', ''),
                    "Tipo de Corte": producto.get('tipo_corte', ''),
                    "Precio": producto.get('precio', 0),
                    "Stock": producto.get('stock', 0),
                    "Stock Mínimo": producto.get('stock_minimo', 0),
                    "Imagen": producto.get('imagen', '')
                })
            
            return pd.DataFrame(data, columns=self.columnas)
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            import pandas as pd
            return pd.DataFrame(columns=self.columnas)

    def obtenerPorId(self, producto_id):
        try:
            # Usar el metodo optimizado del modelo base
            producto_dict = self.obtenerRegistro(producto_id, 'id')

            if producto_dict:
                # Mapear manualmente el diccionario de minúsculas a mayúsculas
                data_mapeada = {
                    "ID": producto_dict.get('id', ''),
                    "Nombre": producto_dict.get('nombre', ''),
                    "Categoría": producto_dict.get('categoria', ''),
                    "Tipo de Corte": producto_dict.get('tipo_corte', ''),
                    "Precio": producto_dict.get('precio', 0),
                    "Stock": producto_dict.get('stock', 0),
                    "Stock Mínimo": producto_dict.get('stock_minimo', 0),
                    "Imagen": producto_dict.get('imagen', '')
                }
                return pd.DataFrame([data_mapeada]) # → DataFrame creado con Mapeo
            else: # → Retorna un DataFrame vacío si no encuentra nada
                return pd.DataFrame(columns=self.columnas)

        except Exception as e:
            print(f"Error al obtener producto por ID: {e}")
            return pd.DataFrame(columns=self.columnas)

    def crearProducto(self, datos):
        try:
            # Generar ID usando el nuevo sistema P0001, P0002, etc.
            nuevo_id = self.generar_siguiente_id()
            
            # Manejar imagen si existe
            imagen_destino = ""
            if datos.get("imagen_origen"):
                imagen_destino = self.plagiarImagen(datos["imagen_origen"], nuevo_id)
            
            # Mapear datos al formato SQLite
            producto_data = {
                'id': nuevo_id,
                'nombre': datos.get('Nombre', ''),
                'categoria': datos.get('Categoría', ''),
                'tipo_corte': datos.get('Tipo de Corte', ''),
                'precio': float(datos.get('Precio', 0)),
                'stock': int(datos.get('Stock inicial', datos.get('Stock', 0))),
                'stock_minimo': int(datos.get('Stock Mínimo', 0)),
                'imagen': imagen_destino
            }
            
            # Crear producto usando el metodo base
            self.crearRegistro(producto_data)
            return nuevo_id
            
        except Exception as e:
            print(f"Error creando producto: {e}")
            raise
    
    def actualizarProducto(self, producto_id, datos):
        try:
            # Verificar que el producto existe
            if not self.vericarRegistroID(producto_id, 'id'):
                raise ValueError(f"Producto con ID {producto_id} no encontrado")
            
            # Manejar imagen si se proporciona una nueva
            imagen_destino = None
            if datos.get("imagen_origen"):
                imagen_destino = self.plagiarImagen(datos["imagen_origen"], producto_id)

            # Mapear datos al formato SQLite
            update_data = {}
            if 'Nombre' in datos:
                update_data['nombre'] = datos['Nombre']
            if 'Categoría' in datos:
                update_data['categoria'] = datos['Categoría']
            if 'Tipo de Corte' in datos:
                update_data['tipo_corte'] = datos['Tipo de Corte']
            if 'Precio' in datos:
                update_data['precio'] = float(datos['Precio'])
            if 'Stock inicial' in datos or 'Stock' in datos:
                update_data['stock'] = int(datos.get('Stock inicial', datos.get('Stock', 0)))
            if 'Stock Mínimo' in datos:
                update_data['stock_minimo'] = int(datos['Stock Mínimo'])
            if imagen_destino:
                update_data['imagen'] = imagen_destino
            
            # Actualizar usando el método base
            return self.actualizarRegistroID(producto_id, update_data, 'id')
            
        except Exception as e:
            print(f"Error actualizando producto {producto_id}: {e}")
            raise
    
    def eliminarProducto(self, producto_id):
        try:
            return self.eliminarRegistroID(producto_id, 'id')
        except Exception as e:
            print(f"Error eliminando producto {producto_id}: {e}")
            return False
    
    def plagiarImagen(self, origen, producto_id):
        try:
            if not os.path.exists(origen):
                return ""
            
            extension = os.path.splitext(origen)[1]
            destino = os.path.join(IMG_DIR, f"{producto_id}{extension}")
            
            # Si ya existe la misma imagen, no copiar
            if os.path.exists(destino) and os.path.samefile(origen, destino):
                return destino
            
            # Si existe una imagen diferente con el mismo nombre, eliminarla primero
            if os.path.exists(destino):
                os.remove(destino)
            
            shutil.copy(origen, destino)
            return destino
        except Exception as e:
            print(f"Error al copiar imagen: {e}")
            return ""

    def buscarProducto(self, termino):
        try:
            if not termino.strip():
                return self.obtener_todos()
            
            # Buscar en SQLite usando el método base
            search_columns = ['nombre', 'id', 'categoria']
            productos = self.buscarRegistro(termino, search_columns)
            
            # Convertir a formato pandas-like para compatibilidad
            import pandas as pd
            
            if not productos:
                return pd.DataFrame(columns=self.columnas)
            
            # Mapear campos de SQLite a formato Excel esperado
            data = []
            for producto in productos:
                data.append({
                    "ID": producto.get('id', ''),
                    "Nombre": producto.get('nombre', ''),
                    "Categoría": producto.get('categoria', ''),
                    "Tipo de Corte": producto.get('tipo_corte', ''),
                    "Precio": producto.get('precio', 0),
                    "Stock": producto.get('stock', 0),
                    "Stock Mínimo": producto.get('stock_minimo', 0),
                    "Imagen": producto.get('imagen', '')
                })
            
            return pd.DataFrame(data, columns=self.columnas)
            
        except Exception as e:
            print(f"Error buscando productos: {e}")
            import pandas as pd
            return pd.DataFrame(columns=self.columnas)

    def obtenerStockBajo(self):
        try:
            productos = self.get_all()
            productos_problematicos = []
            
            for producto in productos:
                stock_actual = int(producto.get('stock', 0))
                stock_minimo = int(producto.get('stock_minimo', 0))
                
                if stock_minimo > 0:
                    # Convertir producto a formato pandas-like para compatibilidad
                    import pandas as pd
                    producto_series = pd.Series({
                        "ID": producto.get('id', ''),
                        "Nombre": producto.get('nombre', ''),
                        "Categoría": producto.get('categoria', ''),
                        "Tipo de Corte": producto.get('tipo_corte', ''),
                        "Precio": producto.get('precio', 0),
                        "Stock": stock_actual,
                        "Stock Mínimo": stock_minimo,
                        "Imagen": producto.get('imagen', '')
                    })
                    
                    if stock_actual <= stock_minimo:
                        productos_problematicos.append({
                            'tipo': 'critico',
                            'producto': producto_series
                        })
                    elif stock_actual <= stock_minimo * 1.5:
                        productos_problematicos.append({
                            'tipo': 'bajo',
                            'producto': producto_series
                        })
            
            return productos_problematicos

        except Exception as e:
            print(f"Error obteniendo productos con stock bajo: {e}")
            return []