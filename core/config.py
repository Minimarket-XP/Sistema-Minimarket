## Configuraciones del sistema Minimarket Don Manuelito

import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
IMG_DIR = os.path.join(DB_DIR, "imagenes")
DATABASE_FILE = os.path.join(DB_DIR, "minimarket.db")

# Configuración de aplicación
APP_NAME = "Minimarket Don Manuelito"
APP_ICON = os.path.join(IMG_DIR, "LOGOO.ico")
APP_ICON_BLANCO = os.path.join(IMG_DIR, "LOGOBLANCO2.png")
APP_VERSION = "1.9.11"
WINDOW_SIZE = "1800x1200"
USE_SQLITE = True

# Esquema de colores
THEME_COLOR = "#1E3A5F"
THEME_COLOR_HOVER = "#1e5a6b"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"
ERROR_COLOR = "#e60000"
INFO_COLOR = "#3498db"
WHITE_COLOR = "#ffffff"
NIGHT_COLOR = "#2c3e50"

# Crear directorios necesarios
for directory in [DB_DIR, IMG_DIR]:
    os.makedirs(directory, exist_ok=True)