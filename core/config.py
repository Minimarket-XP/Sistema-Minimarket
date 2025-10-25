## Configuraciones del sistema Minimarket Don Manuelito

import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
IMG_DIR = os.path.join(DB_DIR, "imagenes")
DATABASE_FILE = os.path.join(DB_DIR, "minimarket.db")

# Archivos Excel (respaldo/migración)
PRODUCTOS_FILE = os.path.join(DB_DIR, "productos.xlsx")
CATEGORIAS_FILE = os.path.join(DB_DIR, "categorias.xlsx")
EMPLEADOS_FILE = os.path.join(DB_DIR, "empleados.xlsx")

# Configuración de aplicación
APP_NAME = "Minimarket Don Manuelito"
APP_ICON = os.path.join(IMG_DIR, "LOGOO.ico")
APP_VERSION = "1.5.190925"
WINDOW_SIZE = "1800x1200"
USE_SQLITE = True

# Esquema de colores
THEME_COLOR = "#256d85"
THEME_COLOR_HOVER = "#1e5a6b"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
ERROR_COLOR = "#e74c3c"
INFO_COLOR = "#3498db"
NIGHT_COLOR = "#2c3e50"

# Crear directorios necesarios
for directory in [DB_DIR, IMG_DIR]:
    os.makedirs(directory, exist_ok=True)