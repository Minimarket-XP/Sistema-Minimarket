## Modelo para manejar los datos de productos

import shutil
from core.config import *
from core.base_model import BaseModel
from core.database import db
import pandas as pd

# → Modelo para gestionar productos
class ProductoModel(BaseModel):
# → Inicializa el modelo de productos con las columnas definidas
    def __init__(self):
        # Definir columnas de la tabla productos
        columns = ['id_producto', 'nombre_producto', 'descripcion_producto', 'precio_producto', 
                   'stock_producto', 'stock_minimo', 'estado_producto', 'tipo_corte', 'imagen',
                   'id_tipo_productos', 'id_categoria_productos', 'id_unidad_medida']
        super().__init__('productos', columns)
        self.columnas = ["ID", "Nombre", "Categoría", "Tipo", "Precio", "Stock", "Stock Mínimo", "Imagen"]
    
# → Genera el siguiente ID de producto en formato PROD0001, PROD0002, etc., rellenando huecos.
    def generar_siguiente_id(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            # Obtener todos los IDs existentes ordenados
            cursor.execute("SELECT id_producto FROM productos ORDER BY id_producto ASC")
            ids_existentes = [row[0] for row in cursor.fetchall()]
            
            # Buscar el primer hueco en la secuencia
            for i in range(1, 9999):  # PROD0001 hasta PROD9999
                id_esperado = f"PROD{i:04d}"
                if id_esperado not in ids_existentes:
                    conn.close()
                    return id_esperado
            
            # Si no hay huecos, usar el siguiente después del último
            if ids_existentes:
                # Extraer el número del último ID
                ultimo_id = max(ids_existentes)
                ultimo_numero = int(ultimo_id[4:])  # Remover 'PROD' y convertir a int
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            conn.close()
            return f"PROD{nuevo_numero:04d}"
            
        except Exception as e:
            print(f"Error generando ID: {e}")
            # Fallback: usar timestamp
            from datetime import datetime
            return f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
# → Obtiene todos los productos con sus detalles relacionados.
    def obtener_todos(self):
        try:
            from core.database import db
            import pandas as pd
            
            conexion = db.get_connection()
            query = '''
                SELECT p.id_producto, p.nombre_producto, p.precio_producto, 
                       p.stock_producto, p.stock_minimo, p.tipo_corte, p.imagen,
                       c.nombre_categoria, t.nombre_tipo, u.nombre_unidad
                FROM productos p
                LEFT JOIN categoria_productos c ON p.id_categoria_productos = c.id_categoria_productos
                LEFT JOIN tipo_productos t ON p.id_tipo_productos = t.id_tipo_producto
                LEFT JOIN unidad_medida u ON p.id_unidad_medida = u.id_unidad_medida
                ORDER BY p.id_producto
            '''
            productos = pd.read_sql_query(query, conexion)
            conexion.close()
            
            if productos.empty:
                return pd.DataFrame(columns=self.columnas)
            
            # Mapear a formato esperado (sin Unidad para tabla de inventario)
            productos_mapeados = pd.DataFrame({
                "ID": productos['id_producto'],
                "Nombre": productos['nombre_producto'],
                "Categoría": productos['nombre_categoria'].fillna('Sin categoría'),
                "Tipo": productos['nombre_tipo'].fillna('Sin tipo'),
                "Precio": productos['precio_producto'],
                "Stock": productos['stock_producto'],
                "Stock Mínimo": productos['stock_minimo'],
                "Imagen": productos['imagen'].fillna('')
            })
            
            return productos_mapeados
            
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            import pandas as pd
            return pd.DataFrame(columns=self.columnas)

# → Obtiene un producto por su ID con detalles relacionados
    def obtenerPorId(self, producto_id):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT p.id_producto, p.nombre_producto, p.precio_producto, 
                       p.stock_producto, p.stock_minimo, p.tipo_corte, p.imagen,
                       c.nombre_categoria, t.nombre_tipo
                FROM productos p
                LEFT JOIN categoria_productos c ON p.id_categoria_productos = c.id_categoria_productos
                LEFT JOIN tipo_productos t ON p.id_tipo_productos = t.id_tipo_producto
                WHERE p.id_producto = ?
            '''
            producto = pd.read_sql_query(query, conexion, params=[producto_id])
            conexion.close()
            
            if producto.empty:
                return pd.DataFrame(columns=self.columnas)
            
            # Mapear a formato esperado
            data_mapeada = pd.DataFrame({
                "ID": producto['id_producto'],
                "Nombre": producto['nombre_producto'],
                "Categoría": producto['nombre_categoria'].fillna('Sin categoría'),
                "Tipo": producto['nombre_tipo'].fillna('Sin tipo'),
                "Precio": producto['precio_producto'],
                "Stock": producto['stock_producto'],
                "Stock Mínimo": producto['stock_minimo'],
                "Imagen": producto['imagen'].fillna('')
            })
            return data_mapeada

        except Exception as e:
            print(f"Error al obtener producto por ID: {e}")
            return pd.DataFrame(columns=self.columnas)

    def crearProducto(self, datos):
        try:
            from core.database import db
            
            # Generar ID usando el nuevo sistema PROD0001, PROD0002, etc.
            nuevo_id = self.generar_siguiente_id()
            
            # Manejar imagen si existe
            imagen_destino = ""
            if datos.get("imagen_origen"):
                imagen_destino = self.plagiarImagen(datos["imagen_origen"], nuevo_id)
            
            # Obtener IDs de categoria, tipo y unidad
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            # Categoria
            categoria_nombre = datos.get('Categoría', '')
            cursor.execute("SELECT id_categoria_productos FROM categoria_productos WHERE nombre_categoria = ?", [categoria_nombre])
            categoria_row = cursor.fetchone()
            id_categoria = categoria_row[0] if categoria_row else 1
            
            # Tipo
            tipo_nombre = datos.get('Tipo', '')
            cursor.execute("SELECT id_tipo_producto FROM tipo_productos WHERE nombre_tipo = ?", [tipo_nombre])
            tipo_row = cursor.fetchone()
            id_tipo = tipo_row[0] if tipo_row else 1
            
            # Unidad
            unidad_nombre = datos.get('Unidad', '')
            cursor.execute("SELECT id_unidad_medida FROM unidad_medida WHERE nombre_unidad = ?", [unidad_nombre])
            unidad_row = cursor.fetchone()
            id_unidad = unidad_row[0] if unidad_row else 1
            
            # Insertar producto
            cursor.execute('''
                INSERT INTO productos (
                    id_producto, nombre_producto, descripcion_producto, precio_producto,
                    stock_producto, stock_minimo, estado_producto, tipo_corte, imagen,
                    id_tipo_productos, id_categoria_productos, id_unidad_medida
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nuevo_id,
                datos.get('Nombre', ''),
                datos.get('Descripción', ''),
                float(datos.get('Precio', 0)),
                int(datos.get('Stock inicial', datos.get('Stock', 0))),
                int(datos.get('Stock Mínimo', 0)),
                'activo',
                datos.get('Tipo de Corte', ''),
                imagen_destino,
                id_tipo,
                id_categoria,
                id_unidad
            ))
            
            conexion.commit()
            conexion.close()
            return nuevo_id
            
        except Exception as e:
            print(f"Error creando producto: {e}")
            if conexion:
                conexion.close()
            raise
    
    def actualizarProducto(self, producto_id, datos):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT id_producto FROM productos WHERE id_producto = ?", [producto_id])
            if not cursor.fetchone():
                conexion.close()
                raise ValueError(f"Producto con ID {producto_id} no encontrado")
            
            # Manejar imagen si se proporciona una nueva
            imagen_destino = None
            if datos.get("imagen_origen"):
                imagen_destino = self.plagiarImagen(datos["imagen_origen"], producto_id)

            # Construir UPDATE dinámicamente
            updates = []
            params = []
            
            if 'Nombre' in datos:
                updates.append('nombre_producto = ?')
                params.append(datos['Nombre'])
            if 'Descripción' in datos:
                updates.append('descripcion_producto = ?')
                params.append(datos['Descripción'])
            if 'Precio' in datos:
                updates.append('precio_producto = ?')
                params.append(float(datos['Precio']))
            if 'Stock inicial' in datos or 'Stock' in datos:
                updates.append('stock_producto = ?')
                params.append(int(datos.get('Stock inicial', datos.get('Stock', 0))))
            if 'Stock Mínimo' in datos:
                updates.append('stock_minimo = ?')
                params.append(int(datos['Stock Mínimo']))
            if 'Tipo de Corte' in datos:
                updates.append('tipo_corte = ?')
                params.append(datos['Tipo de Corte'])
            if imagen_destino:
                updates.append('imagen = ?')
                params.append(imagen_destino)
            
            # Actualizar IDs de relaciones si es necesario
            if 'Categoría' in datos:
                cursor.execute("SELECT id_categoria_productos FROM categoria_productos WHERE nombre_categoria = ?", [datos['Categoría']])
                cat_row = cursor.fetchone()
                if cat_row:
                    updates.append('id_categoria_productos = ?')
                    params.append(cat_row[0])
            
            if 'Tipo' in datos:
                cursor.execute("SELECT id_tipo_producto FROM tipo_productos WHERE nombre_tipo = ?", [datos['Tipo']])
                tipo_row = cursor.fetchone()
                if tipo_row:
                    updates.append('id_tipo_productos = ?')
                    params.append(tipo_row[0])
            
            if updates:
                params.append(producto_id)
                query = f"UPDATE productos SET {', '.join(updates)} WHERE id_producto = ?"
                cursor.execute(query, params)
                conexion.commit()
            
            conexion.close()
            return True
            
        except Exception as e:
            print(f"Error actualizando producto {producto_id}: {e}")
            if conexion:
                conexion.close()
            raise
    
    def eliminarProducto(self, producto_id):
        try:
            conexion = db.get_connection()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id_producto = ?", [producto_id])
            conexion.commit()
            rows_affected = cursor.rowcount
            conexion.close()
            return rows_affected > 0
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
            
            conexion = db.get_connection()
            query = '''
                SELECT p.id_producto, p.nombre_producto, p.precio_producto, 
                       p.stock_producto, p.stock_minimo, p.tipo_corte, p.imagen,
                       c.nombre_categoria, t.nombre_tipo
                FROM productos p
                LEFT JOIN categoria_productos c ON p.id_categoria_productos = c.id_categoria_productos
                LEFT JOIN tipo_productos t ON p.id_tipo_productos = t.id_tipo_producto
                WHERE p.nombre_producto LIKE ? OR p.id_producto LIKE ? OR c.nombre_categoria LIKE ?
                ORDER BY p.id_producto
            '''
            termino_busqueda = f"%{termino}%"
            productos = pd.read_sql_query(query, conexion, params=[termino_busqueda, termino_busqueda, termino_busqueda])
            conexion.close()
            
            if productos.empty:
                return pd.DataFrame(columns=self.columnas)
            
            # Mapear a formato esperado
            productos_mapeados = pd.DataFrame({
                "ID": productos['id_producto'],
                "Nombre": productos['nombre_producto'],
                "Categoría": productos['nombre_categoria'].fillna('Sin categoría'),
                "Tipo": productos['nombre_tipo'].fillna('Sin tipo'),
                "Precio": productos['precio_producto'],
                "Stock": productos['stock_producto'],
                "Stock Mínimo": productos['stock_minimo'],
                "Imagen": productos['imagen'].fillna('')
            })
            
            return productos_mapeados
            
        except Exception as e:
            print(f"Error buscando productos: {e}")
            return pd.DataFrame(columns=self.columnas)

    def obtenerStockBajo(self):
        try:
            conexion = db.get_connection()
            query = '''
                SELECT p.id_producto, p.nombre_producto, p.precio_producto, 
                       p.stock_producto, p.stock_minimo, p.tipo_corte, p.imagen,
                       c.nombre_categoria, t.nombre_tipo
                FROM productos p
                LEFT JOIN categoria_productos c ON p.id_categoria_productos = c.id_categoria_productos
                LEFT JOIN tipo_productos t ON p.id_tipo_productos = t.id_tipo_producto
                WHERE p.stock_minimo > 0
                ORDER BY p.stock_producto ASC
            '''
            productos = pd.read_sql_query(query, conexion)
            conexion.close()
            
            productos_problematicos = []
            
            for _, producto in productos.iterrows():
                stock_actual = int(producto['stock_producto'])
                stock_minimo = int(producto['stock_minimo'])
                
                producto_series = pd.Series({
                    "ID": producto['id_producto'],
                    "Nombre": producto['nombre_producto'],
                    "Categoría": producto.get('nombre_categoria', 'Sin categoría'),
                    "Tipo": producto.get('nombre_tipo', 'Sin tipo'),
                    "Precio": producto['precio_producto'],
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