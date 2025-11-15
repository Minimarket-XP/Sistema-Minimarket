## Configuración y manejo de la base de datos SQLite

import sqlite3
import os
import bcrypt
from core.config import DB_DIR

class Database:
    def __init__(self):
        self.db_path = os.path.join(DB_DIR, "minimarket.db")
        self.init_database()
    
    def get_connection(self): # Conecta a la BD - SQLite
        conn = sqlite3.connect(self.db_path)
        # Configurar la conexión para manejar UTF-8 correctamente
        conn.execute("PRAGMA encoding = 'UTF-8'")
        # Usar text_factory para manejar correctamente los strings
        conn.text_factory = lambda x: str(x, 'utf-8', 'replace') if isinstance(x, bytes) else x
        return conn
    
    def init_database(self): # Inicia la BD 
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                tipo_corte TEXT,
                precio REAL NOT NULL DEFAULT 0,
                stock INTEGER NOT NULL DEFAULT 0,
                stock_minimo INTEGER NOT NULL DEFAULT 0,
                imagen TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de empleados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'empleado',
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de clientes (para facturación electrónica)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_documento TEXT NOT NULL,
                num_documento TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                direccion TEXT,
                telefono TEXT,
                email TEXT,
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id TEXT PRIMARY KEY,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                empleado_id INTEGER,
                total REAL NOT NULL DEFAULT 0,
                metodo_pago TEXT,
                estado TEXT DEFAULT 'completada',
                descuento REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (empleado_id) REFERENCES empleados (id)
            )
        ''')
        
        # Tabla de comprobantes electrónicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comprobantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id TEXT NOT NULL,
                tipo TEXT NOT NULL,
                serie TEXT,
                numero INTEGER,
                cliente_id INTEGER,
                ruc_emisor TEXT,
                xml_path TEXT,
                pdf_path TEXT,
                estado_sunat TEXT,
                fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venta_id) REFERENCES ventas (id),
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        # Tabla de detalle de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id TEXT NOT NULL,
                producto_id TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                descuento REAL DEFAULT 0,
                FOREIGN KEY (venta_id) REFERENCES ventas (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # Tabla de devoluciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devoluciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id TEXT NOT NULL,
                producto_id TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                motivo TEXT,
                empleado_id INTEGER,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (venta_id) REFERENCES ventas (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id),
                FOREIGN KEY (empleado_id) REFERENCES empleados (id)
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                descripcion TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de auditoría de logins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exitoso INTEGER NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')

        # Tabla de intentos fallidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intentos_fallidos (
                usuario TEXT PRIMARY KEY,
                intentos INTEGER NOT NULL DEFAULT 0,
                bloqueado_hasta TIMESTAMP,
                ultimo_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de sesiones activas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activa INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (usuario) REFERENCES empleados (usuario)
            )
        ''')

        # Tabla de auditoría de acciones (DEBE EXISTIR ANTES DE LOS TRIGGERS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                accion TEXT NOT NULL,
                tabla_afectada TEXT,
                registro_id TEXT,
                detalles TEXT,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de alertas de stock (DEBE EXISTIR ANTES DE LOS TRIGGERS)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id TEXT NOT NULL,
                stock_actual INTEGER NOT NULL,
                stock_minimo INTEGER NOT NULL,
                fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resuelta INTEGER DEFAULT 0,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                UNIQUE(producto_id, resuelta)
            )
        ''')

        # Insertar datos iniciales si no existen
        self._insertar_datos_iniciales(cursor)
        
        # Crear triggers de lógica de negocio
        self._crear_triggers(cursor)

        conn.commit()

        # Migracion simple en la columna descuento en tabla existentes
        try:
            cursor.execute("PRAGMA table_info(ventas)")
            cols = [r[1] for r in cursor.fetchall()]
            # Añadir columna descuento si no existe
            if 'descuento' not in cols:
                cursor.execute('ALTER TABLE ventas ADD COLUMN descuento REAL NOT NULL DEFAULT 0')
                conn.commit()
            # Añadir columna 'descuento_pct' si no existe
            if 'descuento_pct' not in cols:
                cursor.execute('ALTER TABLE ventas ADD COLUMN descuento_pct REAL NOT NULL DEFAULT 0')
                conn.commit()
            # Añadir columna 'descuento_tipo' si no existe
            if 'descuento_tipo' not in cols:
                cursor.execute("ALTER TABLE ventas ADD COLUMN descuento_tipo TEXT DEFAULT ''")
                conn.commit()
            # Asegurar columna 'descuento' en detalle_ventas (puede ser NULL)
            cursor.execute("PRAGMA table_info(detalle_ventas)")
            cols_det = [r[1] for r in cursor.fetchall()]
            if 'descuento' not in cols_det:
                # Allow NULL so line may have no discount when global discount applies
                cursor.execute("ALTER TABLE detalle_ventas ADD COLUMN descuento REAL")
                conn.commit()
        except Exception:
            pass
        conn.close()
    
    def _insertar_datos_iniciales(self, cursor): # → Insertar datos iniciales del minimarket

        # Insertar usuario administrador por defecto (verificar si no existe)
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE usuario = 'admin'")
        if cursor.fetchone()[0] == 0:
            hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO empleados (nombre, apellido, usuario, contraseña, rol)
                VALUES ('Administrador', 'Sistema', 'admin', ?, 'administrador')
            ''', (hashed_password,))

        # Insertar cliente genérico para boletas sin DNI
        cursor.execute('''
            INSERT OR IGNORE INTO clientes (id, tipo_documento, num_documento, nombre)
            VALUES (1, 'GENERICO', '00000000', 'Cliente Genérico')
        ''')
        
        # Insertar categorías básicas
        categorias_basicas = [
            ('Abarrotes', 'Productos de consumo básico'),
            ('Bebidas', 'Bebidas alcohólicas y no alcohólicas'),
            ('Lácteos', 'Productos lácteos y derivados'),
            ('Carnes', 'Carnes y embutidos'),
            ('Frutas y Verduras', 'Productos frescos'),
            ('Limpieza', 'Productos de limpieza e higiene'),
            ('Panadería', 'Pan y productos de panadería')
        ]
        
        for nombre, descripcion in categorias_basicas:
            cursor.execute("SELECT COUNT(*) FROM categorias WHERE nombre = ?", (nombre,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO categorias (nombre, descripcion)
                    VALUES (?, ?)
                ''', (nombre, descripcion))

        # Insertar configuraciones básicas
        configuraciones = [
            ('nombre_empresa', 'Minimarket Don Manuelito', 'Nombre de la empresa'),
            ('ruc_empresa', '10730291529', 'RUC de la empresa'),
            ('direccion_empresa', 'Jr. José Francisco de Zela 1338', 'Dirección de la empresa'),
            ('telefono_empresa', '123-456-789', 'Teléfono de la empresa'),
            ('moneda', 'PEN', 'Moneda utilizada'),
            ('igv', '18', 'Porcentaje de IGV')
        ]
        
        for clave, valor, descripcion in configuraciones:
            cursor.execute('''
                INSERT OR IGNORE INTO configuracion (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', (clave, valor, descripcion))
    
    def execute_query(self, query, params=None): # Ejecuta una consulta
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        
        return result
    
    def execute_insert(self, query, params=None): # Ejecuta un INSERT y retorna el ID último
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return last_id
    
    def verificar_credenciales(self, usuario, contraseña):
        query = "SELECT contraseña FROM empleados WHERE usuario = ? AND activo = 1"
        result = self.execute_query(query, (usuario,))
    
        if not result:
            return False
    
        hashed_password = result[0][0]
    
        # Verificar contraseña con bcrypt
        try:
            return bcrypt.checkpw(contraseña.encode('utf-8'), hashed_password)
        except Exception as e:
            print(f"Error verificando contraseña: {e}")
            return False

    def _crear_triggers(self, cursor):
        """Crea triggers SOLO para ventas y empleados"""

        # ============================================
        # TRIGGERS PARA VENTAS Y STOCK (6 triggers)
        # ============================================

        # TRIGGER 1: Validar stock antes de venta
        cursor.execute('DROP TRIGGER IF EXISTS validar_stock_antes_venta')
        cursor.execute('''
            CREATE TRIGGER validar_stock_antes_venta
            BEFORE INSERT ON detalle_ventas
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN (SELECT stock FROM productos WHERE id = NEW.producto_id) < NEW.cantidad
                    THEN RAISE(ABORT, 'Stock insuficiente para el producto')
                END;
            END
        ''')

        # TRIGGER 2: Actualizar stock después de venta
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_stock_despues_venta')
        cursor.execute('''
            CREATE TRIGGER actualizar_stock_despues_venta
            AFTER INSERT ON detalle_ventas
            FOR EACH ROW
            BEGIN
                UPDATE productos 
                SET stock = stock - NEW.cantidad,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = NEW.producto_id;
            END
        ''')

        # TRIGGER 3: Restaurar stock al eliminar detalle
        cursor.execute('DROP TRIGGER IF EXISTS restaurar_stock_eliminar_detalle')
        cursor.execute('''
            CREATE TRIGGER restaurar_stock_eliminar_detalle
            AFTER DELETE ON detalle_ventas
            FOR EACH ROW
            BEGIN
                UPDATE productos 
                SET stock = stock + OLD.cantidad,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = OLD.producto_id;
            END
        ''')

        # TRIGGER 4: Eliminar detalles al eliminar venta
        cursor.execute('DROP TRIGGER IF EXISTS eliminar_detalles_al_eliminar_venta')
        cursor.execute('''
            CREATE TRIGGER eliminar_detalles_al_eliminar_venta
            BEFORE DELETE ON ventas
            FOR EACH ROW
            BEGIN
                DELETE FROM detalle_ventas WHERE venta_id = OLD.id;
            END
        ''')

        # TRIGGER 5: Validar precio positivo
        cursor.execute('DROP TRIGGER IF EXISTS validar_precio_detalle_venta')
        cursor.execute('''
            CREATE TRIGGER validar_precio_detalle_venta
            BEFORE INSERT ON detalle_ventas
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.precio_unitario <= 0
                    THEN RAISE(ABORT, 'El precio unitario debe ser mayor a 0')
                END;
            END
        ''')

        # TRIGGER 6: Validar cantidad positiva
        cursor.execute('DROP TRIGGER IF EXISTS validar_cantidad_detalle_venta')
        cursor.execute('''
            CREATE TRIGGER validar_cantidad_detalle_venta
            BEFORE INSERT ON detalle_ventas
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.cantidad <= 0
                    THEN RAISE(ABORT, 'La cantidad debe ser mayor a 0')
                END;
            END
        ''')

        # ============================================
        # TRIGGERS PARA EMPLEADOS (2 triggers)
        # ============================================

        # TRIGGER 7: Validar usuario único
        cursor.execute('DROP TRIGGER IF EXISTS validar_usuario_empleado_insert')
        cursor.execute('''
            CREATE TRIGGER validar_usuario_empleado_insert
            BEFORE INSERT ON empleados
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN (SELECT COUNT(*) FROM empleados WHERE usuario = NEW.usuario) > 0
                    THEN RAISE(ABORT, 'El usuario ya existe')
                END;
            END
        ''')

        # TRIGGER 8: Validar contraseña no vacía
        cursor.execute('DROP TRIGGER IF EXISTS validar_password_empleado')
        cursor.execute('''
            CREATE TRIGGER validar_password_empleado
            BEFORE INSERT ON empleados
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.contraseña IS NULL OR LENGTH(NEW.contraseña) = 0
                    THEN RAISE(ABORT, 'La contraseña no puede estar vacía')
                END;
            END
        ''')

        print("8 triggers esenciales creados exitosamente (6 ventas + 2 empleados)")

# Instancia global de la base de datos
db = Database()
