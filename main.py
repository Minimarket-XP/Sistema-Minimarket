## Sistema de Minimarket Don Manuelito - PyQt5 Version

import sys
import os
import locale
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTextCodec

# Configurar la codificación por defecto del sistema
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configurar locale para UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
    except locale.Error:
        pass  # Usar configuración por defecto

def main():
    try:
        # Configurar variables de entorno para UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Crear la aplicación PyQt5
        app = QApplication(sys.argv)
        
        # Configurar codec de texto para UTF-8 en PyQt5
        try:
            codec = QTextCodec.codecForName("UTF-8")
            if codec:
                QTextCodec.setCodecForLocale(codec)
        except Exception as codec_error:
            print(f"Advertencia: No se pudo configurar codec UTF-8: {codec_error}")
        
        # Configurar propiedades de la aplicación
        app.setApplicationName("Sistema Minimarket Don Manuelito")
        app.setApplicationVersion("2.0.0 - PyQt5 Migration")

        # Importar y crear la ventana principal de login
        from views.login import LoginVentana
        login_window = LoginVentana()
        login_window.show()
        
        # Ejecutar la aplicación
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Error al importar módulos PyQt5: {e}")
        print("Verifica que PyQt5 esté instalado: pip install PyQt5")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
    