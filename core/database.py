## Configuración y manejo de la base de datos SQLite

import sqlite3
import os
import bcrypt
from core.config import DB_DIR

class Database:
    def __init__(self):
        # Conectar a la base de datos SQLite
        self.db_path = os.path.join(DB_DIR, "minimarket.db")
        self.init_database()

    def get_connection(self): # Conecta a la BD - SQLite
        conn = sqlite3.connect(self.db_path)
        # Configurar la conexión para manejar UTF-8 correctamente
        conn.execute("PRAGMA encoding = 'UTF-8'")
        # Usar text_factory para manejar correctamente los strings
        # replace caracteres inválidos con el caracter de reemplazo �
        conn.text_factory = lambda x: str(x, 'utf-8', 'replace') if isinstance(x, bytes) else x
        return conn
<<<<<<< HEAD
    
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
                descuento REAL NOT NULL DEFAULT 0,
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
<<<<<<< HEAD
        # Asegurar columna 'descuento' en tablas existentes (migración simple)
        try:
            cursor.execute("PRAGMA table_info(ventas)")
            cols = [r[1] for r in cursor.fetchall()]
            # Añadir columna 'descuento' si no existe
=======

        # Migracion simple en la columna descuento en tabla existentes
        try:
            cursor.execute("PRAGMA table_info(ventas)")
            cols = [r[1] for r in cursor.fetchall()]
            # Añadir columna descuento si no existe
>>>>>>> dcd6b0d (Implemented migration for adding 'descuento', 'descuento_pct', and 'descuento_tipo' columns to 'ventas' and 'detalle_ventas' tables)
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
<<<<<<< HEAD
            # Si la alteración falla, continuar sin detener la inicialización
            pass

=======
            pass
>>>>>>> dcd6b0d (Implemented migration for adding 'descuento', 'descuento_pct', and 'descuento_tipo' columns to 'ventas' and 'detalle_ventas' tables)
        conn.close()
    
    def _insertar_datos_iniciales(self, cursor): # → Insertar datos iniciales del minimarket
=======

    def init_database(self): # Inicializa la base de datos y crea tablas si no existen
        try:
            # conn = conexión
            # cursor para crear tablas
            conn = self.get_connection()
            cursor = conn.cursor()
>>>>>>> 2291587 (feat(core-db): normalizar BD con 18 tablas y 17 triggers)

            # Tabla de tipo de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tipo_productos (
                    id_tipo_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_tipo TEXT NOT NULL UNIQUE,
                    descripcion TEXT
                )
            ''')

            # Tabla de categorías de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categoria_productos (
                    id_categoria_productos INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_categoria TEXT NOT NULL UNIQUE,
                    descripcion TEXT
                )
            ''')

            # Tabla de unidades de medida
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unidad_medida (
                id_unidad_medida INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_unidad TEXT NOT NULL UNIQUE,
                descripcion TEXT
                )
            ''')

            # Tabla de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id_producto TEXT PRIMARY KEY,
                    nombre_producto VARCHAR(100) NOT NULL,
                    descripcion_producto TEXT,
                    precio_producto REAL NOT NULL,
                    stock_producto INTEGER NOT NULL CHECK (stock_producto >= 0) DEFAULT 0,
                    stock_minimo INTEGER NOT NULL CHECK (stock_minimo >= 0) DEFAULT 0,
                    estado_producto TEXT CHECK(estado_producto IN ('activo', 'descontinuado', 'no disponible', 'en oferta')) NOT NULL DEFAULT 'activo',
                    tipo_corte TEXT,
                    imagen TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    id_tipo_productos INTEGER NOT NULL,
                    id_categoria_productos INTEGER NOT NULL,
                    id_unidad_medida INTEGER NOT NULL,
                    FOREIGN KEY (id_tipo_productos) REFERENCES tipo_productos (id_tipo_productos),
                    FOREIGN KEY (id_categoria_productos) REFERENCES categoria_productos (id_categoria_productos),
                    FOREIGN KEY (id_unidad_medida) REFERENCES unidad_medida (id_unidad_medida)
                )
            ''')

            # Tabla de promocion
            cursor.execute('''
                     CREATE TABLE IF NOT EXISTS promocion (
                         id_promocion INTEGER PRIMARY KEY AUTOINCREMENT,
                         nombre_promocion TEXT NOT NULL,
                         descripcion_promocion TEXT,
                         descuento REAL NOT NULL CHECK (descuento >= 0 AND descuento <= 100),
                         fecha_inicio DATETIME NOT NULL,
                         fecha_fin DATETIME NOT NULL,
                         estado_promocion TEXT CHECK(estado_promocion IN ('activa', 'inactiva', 'expirada')) NOT NULL DEFAULT 'inactiva'
                     )
                 ''')

            # Tabla de promocion_producto
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS promocion_producto (
                    descuento_aplicado REAL NOT NULL,
                    id_promocion INTEGER NOT NULL,
                    id_producto TEXT NOT NULL,
                    PRIMARY KEY (id_promocion, id_producto),
                    FOREIGN KEY (id_promocion) REFERENCES promocion (id_promocion),
                    FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
                )
            ''')

            # Tabla de roles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rol (
                    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_rol TEXT NOT NULL UNIQUE
                )
            ''')

            # Tabla de empleados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empleado (
                    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_empleado TEXT NOT NULL,
                    apellido_empleado TEXT NOT NULL,
                    estado_empleado TEXT CHECK(estado_empleado IN ('activo', 'inactivo')) NOT NULL DEFAULT 'activo',
                    fecha_contratacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    id_rol INTEGER NOT NULL,
                    FOREIGN KEY (id_rol) REFERENCES rol (id_rol)
                )
            ''')

            # Tabla de usuarios - separada de empleados para autenticación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    estado_usuario TEXT CHECK(estado_usuario IN ('activo', 'inactivo')) NOT NULL DEFAULT 'activo',
                    ultimo_login DATETIME,
                    id_empleado INTEGER NOT NULL,
                    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
                )
            ''')

            # Tabla de ventas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id_venta INTEGER PRIMARY KEY,
                    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metodo_pago TEXT CHECK(metodo_pago IN ('efectivo', 'tarjeta', 'yape', 'plin', 'transferencia', 'vale')) NOT NULL DEFAULT 'efectivo',
                    total_venta REAL NOT NULL DEFAULT 0,
                    estado_venta TEXT CHECK(estado_venta IN ('completado', 'cancelado', 'devuelto')) NOT NULL DEFAULT 'completado',
                    id_empleado INTEGER NOT NULL,
                    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
                )
            ''')

            # Tabla dme detalle de ventas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_venta (
                    id_detalle_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    cantidad_detalle INTEGER NOT NULL,
                    precio_unitario_detalle REAL NOT NULL,
                    descuento_aplicado REAL DEFAULT 0,
                    subtotal_detalle REAL NOT NULL,
                    id_producto INTEGER NOT NULL,
                    id_venta INTEGER NOT NULL,
                    FOREIGN KEY (id_producto) REFERENCES productos (id_producto),
                    FOREIGN KEY (id_venta) REFERENCES ventas (id_venta)
                )
            ''')

            # Tabla de comprobantes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comprobante (
                    id_comprobante INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_comprobante TEXT CHECK(tipo_comprobante IN ('factura', 'boleta')) NOT NULL,
                    numero_comprobante VARCHAR(30) NOT NULL,
                    serie_comprobante TEXT,
                    fecha_emision_comprobante DATETIME DEFAULT CURRENT_TIMESTAMP,
                    monto_total_comprobante REAL NOT NULL,
                    ruc_emisor CHAR(11),
                    razon_social VARCHAR(100),
                    direccion_fiscal VARCHAR(100),
                    num_documento CHAR(8),
                    nombre_cliente VARCHAR(100),
                    xml_path TEXT,
                    pdf_path TEXT,
                    estado_sunat TEXT,
                    id_venta INTEGER NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
                    CHECK (
                        (tipo_comprobante = 'factura' AND ruc_emisor IS NOT NULL) OR
                        (tipo_comprobante = 'boleta' AND num_documento IS NOT NULL)
                    )
                )
            ''')

            # Tabla de devoluciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devolucion (
                    id_devolucion INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_devolucion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    motivo_devolucion TEXT,
                    monto_devolucion REAL NOT NULL,
                    tipo_devolucion TEXT CHECK(tipo_devolucion IN ('total', 'parcial')) NOT NULL,
                    estado_devolucion TEXT CHECK(estado_devolucion IN ('pendiente', 'completada', 'en proceso')) DEFAULT 'pendiente',
                    id_venta INTEGER NOT NULL,
                    id_detalle_venta INTEGER NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
                    FOREIGN KEY (id_detalle_venta) REFERENCES detalle_venta (id_detalle_venta)
                )
            ''')

            # Tabla detalle devoluciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_devolucion (
                    id_detalle_devolucion INTEGER PRIMARY KEY AUTOINCREMENT,
                    cantidad_devolucion INTEGER NOT NULL,
                    monto_devolucion REAL NOT NULL,
                    estado_devolucion TEXT CHECK(estado_devolucion IN ('pendiente', 'completada', 'en proceso')) DEFAULT 'pendiente', 
                    id_devolucion INTEGER NOT NULL,
                    id_producto INTEGER NOT NULL, 
                    FOREIGN KEY (id_devolucion) REFERENCES devolucion (id_devolucion),
                    FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
                )
            ''')

            # Tabla de nota de crédito
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nota_credito(
                    id_nota_credito INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_emision_nota DATETIME DEFAULT CURRENT_TIMESTAMP,
                    monto_total_nota REAL NOT NULL,
                    motivo TEXT,
                    id_comprobante INTEGER NOT NULL,
                    id_venta INTEGER NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
                    FOREIGN KEY (id_comprobante) REFERENCES comprobante (id_comprobante)
                )
            ''')

            # Tabla de auditoría
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auditoria (
                    id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    accion_auditoria VARCHAR(100),
                    tabla_afectada VARCHAR(50),
                    fecha_hora_auditoria DATETIME DEFAULT CURRENT_TIMESTAMP,
                    descripcion_auditoria TEXT,
                    ip_cliente_auditoria VARCHAR(45),
                    id_usuario INTEGER NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
                )
            ''')

            # Tabla de backups
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_log (
                    id_backup INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_backup DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_backup TEXT CHECK(tipo_backup IN ('completo', 'incremental')) NOT NULL,
                    estado_backup TEXT CHECK(estado_backup IN ('exitoso', 'fallido')) NOT NULL,
                    ubicacion_archivo_backup VARCHAR(255),
                    descripcion_backup TEXT,
                    usuario_responsable INTEGER NOT NULL,
                    FOREIGN KEY (usuario_responsable) REFERENCES usuario (id_usuario)
                )
            ''')

            # Tabla Configuraciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    descripcion TEXT,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insertar datos iniciales si no existen
            self.datos_iniciales(cursor)
            # Crear triggers de lógica de negocio
            self.triggers(cursor)

            conn.commit() # Guardar cambios
        except Exception as e:
            print(f"Error al crear la base de datos: {e}")
        finally:
            conn.close() # Cerrar conexión

    def datos_iniciales(self, cursor): # → Insertar datos iniciales del minimarket
        try:
            # Insertar rol de administrador (en caso no exista)
            cursor.execute('''
                INSERT OR IGNORE INTO rol (nombre_rol)
                VALUES ('admin')
            ''')

            # obtener el id del rol admin
            cursor.execute("SELECT id_rol FROM rol WHERE nombre_rol = 'admin'")
            # fetchone() devuelve una tupla, obtener el primer elemento
            admin_rol_id = cursor.fetchone()[0]
            # Verificar si el empleado admin ya existe
            if admin_rol_id:
                # En caso no exista, insertar empleado admin y asignarle el rol de admin
                cursor.execute('''
                    INSERT OR IGNORE INTO empleado (nombre_empleado, apellido_empleado, id_rol)
                    VALUES ('Administrador', 'Sistema', ?)
                    ''', (admin_rol_id,))

            # Insertar usuario administrador (si no existe) con contraseña encriptada
            hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT OR IGNORE INTO usuario (username, password_hash, estado_usuario, id_empleado)
                VALUES ('admin', ?, 'activo', (SELECT id_empleado FROM empleado WHERE nombre_empleado = 'Administrador' AND apellido_empleado = 'Sistema'))
            ''', (hashed_password,))

            # Insertar categorías
            categorias_basicas = [
                ('Alimentos básicos', 'Productos esenciales para el consumo diario'),
                ('Bebidas no alcohólicas', 'Refrescos, jugos, aguas y otras bebidas sin alcohol'),
                ('Bebidas alcohólicas', 'Vino, cerveza, licores y otras bebidas con alcohol'),
                ('Lácteos y productos refrigerados', 'Leche, yogur, quesos y otros productos lácteos'),
                ('Carnes y embutidos', 'Carne fresca, pollo, cerdo y embutidos'),
                ('Frutas y verduras', 'Productos frescos'),
                ('Snacks y dulces', 'Galletas, chocolates, papas fritas y otros aperitivos'),
                ('Productos de limpieza y hogar', 'Detergentes, desinfectantes y otros productos para el hogar'),
                ('Cuidado personal', 'Productos de higiene y cuidado personal'),
                ('Productos de temporada', 'Artículos especiales según la temporada o festividades')
            ]

            for nombre, descripcion in categorias_basicas:
                cursor.execute(
                    "SELECT COUNT(*) "
                    "FROM categoria_productos "
                    "WHERE nombre_categoria = ?", (nombre,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO categoria_productos (nombre_categorias, descripcion)
                        VALUES (?, ?)
                    ''', (nombre, descripcion))

            tipos_productos = [
                ('Arroz', 'Diferentes tipos de arroz'),
                ('Azúcar', 'Variedades de azúcar'),
                ('Aceite', 'Aceites'),
                ('Leche', 'Variedades en leche'),
                ('Bebidas Alcohólicas', 'Cerveza, vino, licores'),
                ('Bebidas No Alcohólicas', 'Refrescos y aguas saborizadas'),
                ('Queso', 'Variedades de queso'),
                ('Carne de Res', 'Cortes de carne de res'),
                ('Carne de Pollo', 'Cortes de carne de pollo'),
                ('Verduras', 'Verduras frescas y congeladas'),
                ('Frutas', 'Frutas frescas y congeladas'),
                ('Detergentes', 'Detergentes y limpiadores'),
                ('Snacks', 'Aperitivos y snacks')
            ]

            # Insertar configuraciones básicas
            configuraciones = [
                ('nombre_empresa', 'Minimarket Don Manuelito', 'Nombre de la empresa'),
                ('ruc_empresa', '10730291529', 'RUC de la empresa'),
                ('direccion_empresa', 'Jr. José Francisco de Zela 1338', 'Dirección de la empresa'),
                ('telefono_empresa', '994-618-239', 'Teléfono de la empresa'),
                ('moneda', 'PEN', 'Moneda utilizada'),
                ('igv', '18', 'Porcentaje de IGV')
            ]

            for clave, valor, descripcion in configuraciones:
                cursor.execute('''
                    INSERT OR IGNORE INTO configuracion (clave, valor, descripcion)
                    VALUES (?, ?, ?)
                ''', (clave, valor, descripcion))

        except Exception as e:
            print(f"Error insertando datos iniciales: {e}")

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

    # Triggers → Lógica de negocio automatizada
    def triggers(self, cursor):
        
    # TRIGGERS DE VALIDACIÓN - DETALLE VENTA
        
        # TRIGGER 1: Validar cantidad positiva
        cursor.execute('DROP TRIGGER IF EXISTS validar_cantidad_detalle_venta')
        cursor.execute('''
            CREATE TRIGGER validar_cantidad_detalle_venta
            BEFORE INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.cantidad_detalle <= 0
                    THEN RAISE(ABORT, 'La cantidad debe ser mayor a 0')
                END;
            END
        ''')

        # TRIGGER 2: Validar precio positivo
        cursor.execute('DROP TRIGGER IF EXISTS validar_precio_detalle_venta')
        cursor.execute('''
            CREATE TRIGGER validar_precio_detalle_venta
            BEFORE INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.precio_unitario_detalle <= 0
                    THEN RAISE(ABORT, 'El precio unitario debe ser mayor a 0')
                END;
            END
        ''')

        # TRIGGER 3: Validar stock antes de venta
        cursor.execute('DROP TRIGGER IF EXISTS validar_stock_antes_venta')
        cursor.execute('''
            CREATE TRIGGER validar_stock_antes_venta
            BEFORE INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN (SELECT stock_producto FROM productos WHERE id_producto = NEW.id_producto) < NEW.cantidad_detalle
                    THEN RAISE(ABORT, 'Stock insuficiente para el producto')
                END;
            END
        ''')

    # TRIGGERS DE CÁLCULO AUTOMÁTICO

        # TRIGGER 4: Calcular subtotal automáticamente
        cursor.execute('DROP TRIGGER IF EXISTS calcular_subtotal_detalle')
        cursor.execute('''
            CREATE TRIGGER calcular_subtotal_detalle
            BEFORE INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                SELECT 
                    (NEW.cantidad_detalle * NEW.precio_unitario_detalle) - COALESCE(NEW.descuento_aplicado, 0);
            END
        ''')

    # TRIGGERS DE STOCK - ACTUALIZACIÓN

        # TRIGGER 5: Actualizar stock después de venta
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_stock_despues_venta')
        cursor.execute('''
            CREATE TRIGGER actualizar_stock_despues_venta
            AFTER INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                UPDATE productos
                SET stock_producto = stock_producto - NEW.cantidad_detalle,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_producto = NEW.id_producto;
            END
        ''')

        # TRIGGER 6: Restaurar stock al eliminar detalle
        cursor.execute('DROP TRIGGER IF EXISTS restaurar_stock_eliminar_detalle')
        cursor.execute('''
            CREATE TRIGGER restaurar_stock_eliminar_detalle
            AFTER DELETE ON detalle_venta
            FOR EACH ROW
            BEGIN
                UPDATE productos
                SET stock_producto = stock_producto + OLD.cantidad_detalle,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_producto = OLD.id_producto;
            END
        ''')

        # TRIGGER 7: Actualizar stock al modificar cantidad
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_stock_modificar_detalle')
        cursor.execute('''
            CREATE TRIGGER actualizar_stock_modificar_detalle
            AFTER UPDATE ON detalle_venta
            FOR EACH ROW
            WHEN OLD.cantidad_detalle != NEW.cantidad_detalle
            BEGIN
                UPDATE productos
                SET stock_producto = stock_producto + OLD.cantidad_detalle - NEW.cantidad_detalle,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_producto = NEW.id_producto;
            END
        ''')

    # TRIGGERS DE TOTAL VENTA

        # TRIGGER 8: Actualizar total_venta al insertar detalle
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_total_venta_insert')
        cursor.execute('''
            CREATE TRIGGER actualizar_total_venta_insert
            AFTER INSERT ON detalle_venta
            FOR EACH ROW
            BEGIN
                UPDATE ventas
                SET total_venta = (
                    SELECT COALESCE(SUM(subtotal_detalle), 0)
                    FROM detalle_venta
                    WHERE id_venta = NEW.id_venta
                )
                WHERE id_venta = NEW.id_venta;
            END
        ''')

        # TRIGGER 9: Actualizar total_venta al eliminar detalle
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_total_venta_delete')
        cursor.execute('''
            CREATE TRIGGER actualizar_total_venta_delete
            AFTER DELETE ON detalle_venta
            FOR EACH ROW
            BEGIN
                UPDATE ventas
                SET total_venta = (
                    SELECT COALESCE(SUM(subtotal_detalle), 0)
                    FROM detalle_venta
                    WHERE id_venta = OLD.id_venta
                )
                WHERE id_venta = OLD.id_venta;
            END
        ''')

        # TRIGGER 10: Actualizar total_venta al modificar detalle
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_total_venta_update')
        cursor.execute('''
            CREATE TRIGGER actualizar_total_venta_update
            AFTER UPDATE ON detalle_venta
            FOR EACH ROW
            BEGIN
                UPDATE ventas
                SET total_venta = (
                    SELECT COALESCE(SUM(subtotal_detalle), 0)
                    FROM detalle_venta
                    WHERE id_venta = NEW.id_venta
                )
                WHERE id_venta = NEW.id_venta;
            END
        ''')

    # TRIGGERS DE INTEGRIDAD REFERENCIAL

        # TRIGGER 11: Eliminar detalles al eliminar venta
        cursor.execute('DROP TRIGGER IF EXISTS eliminar_detalles_al_eliminar_venta')
        cursor.execute('''
            CREATE TRIGGER eliminar_detalles_al_eliminar_venta
            BEFORE DELETE ON ventas
            FOR EACH ROW
            BEGIN
                DELETE FROM detalle_venta WHERE id_venta = OLD.id_venta;
            END
        ''')

    # TRIGGERS DE USUARIOS Y SEGURIDAD

        # TRIGGER 12: Validar contraseña no vacía
        cursor.execute('DROP TRIGGER IF EXISTS validar_password_usuario')
        cursor.execute('''
            CREATE TRIGGER validar_password_usuario
            BEFORE INSERT ON usuario
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.password_hash IS NULL OR LENGTH(NEW.password_hash) = 0
                    THEN RAISE(ABORT, 'La contraseña no puede estar vacía')
                END;
            END
        ''')

        # TRIGGER 13: Validar username único en updates
        cursor.execute('DROP TRIGGER IF EXISTS validar_username_update')
        cursor.execute('''
            CREATE TRIGGER validar_username_update
            BEFORE UPDATE ON usuario
            FOR EACH ROW
            WHEN OLD.username != NEW.username
            BEGIN
                SELECT CASE
                    WHEN (SELECT COUNT(*) FROM usuario WHERE username = NEW.username) > 0
                    THEN RAISE(ABORT, 'El nombre de usuario ya existe')
                END;
            END
        ''')

    # TRIGGERS DE PROMOCIONES

        # TRIGGER 14: Validar fechas de promoción
        cursor.execute('DROP TRIGGER IF EXISTS validar_fechas_promocion')
        cursor.execute('''
            CREATE TRIGGER validar_fechas_promocion
            BEFORE INSERT ON promocion
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.fecha_fin <= NEW.fecha_inicio
                    THEN RAISE(ABORT, 'La fecha de fin debe ser posterior a la fecha de inicio')
                END;
            END
        ''')

        # TRIGGER 15: Actualizar estado de promoción expirada
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_estado_promocion_expirada')
        cursor.execute('''
            CREATE TRIGGER actualizar_estado_promocion_expirada
            BEFORE UPDATE ON promocion
            FOR EACH ROW
            WHEN datetime('now') > NEW.fecha_fin AND NEW.estado_promocion != 'expirada'
            BEGIN
                SELECT CASE
                    WHEN 1 = 1 THEN
                        UPDATE promocion SET estado_promocion = 'expirada' WHERE id_promocion = NEW.id_promocion
                END;
            END
        ''')

    # TRIGGERS DE PRODUCTOS

        # TRIGGER 16: Actualizar fecha de modificación de productos
        cursor.execute('DROP TRIGGER IF EXISTS actualizar_fecha_producto')
        cursor.execute('''
            CREATE TRIGGER actualizar_fecha_producto
            BEFORE UPDATE ON productos
            FOR EACH ROW
            BEGIN
                SELECT datetime('now');
            END
        ''')

        # TRIGGER 17: Validar descuento no mayor al 100%
        cursor.execute('DROP TRIGGER IF EXISTS validar_descuento_promocion')
        cursor.execute('''
            CREATE TRIGGER validar_descuento_promocion
            BEFORE INSERT ON promocion
            FOR EACH ROW
            BEGIN
                SELECT CASE
                    WHEN NEW.descuento < 0 OR NEW.descuento > 100
                    THEN RAISE(ABORT, 'El descuento debe estar entre 0 y 100')
                END;
            END
        ''')

# Instancia global de la base de datos
db = Database()