# Sistema Minimarket Don Manuelito

APLICACIÓN DE GESTIÓN DE VENTAS E INVENTARIO EN MINIMARKET "Don Manuelito"

## Descripción

Sistema de gestión completo para minimarket que incluye manejo de inventario, ventas, empleados y reportes. Desarrollado siguiendo la metodología SCRUM con arquitectura modular escalable.

## Estado del Proyecto

**Sprint 1 - PROCESO** - FUNCIONALIDAD MÍNIMA VIABLE
- CRUD completo de productos
- Manejo de imágenes
- Sistema de categorías
- Interfaz moderna con PyQt5

## Tecnologías

- **Python 3.x**
- **PyQt5** - Interfaz gráfica moderna y profesional
- **SQLite** - Base de datos integrada
- **pandas** - Manejo de datos
- **Pillow (PIL)** - Procesamiento de imágenes

## Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/Sistema-Minimarket-wa.git
cd Sistema-Minimarket-wa
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar aplicación**
```bash
python main.py
```

## Estructura del Proyecto

```
Sistema-Minimarket-wa/
├── gitignore                  # Exclusiones git
├── buid_exe.ps1               # Script PowerShell para crear .exe
├── main.py                    # Punto de entrada aplicación
├── README.md                  # Documentación proyecto
├── requirements.txt           # Lista dependencias python
├── S_Minimarket_Fixed.espec   # Configuración PyInstaller
├── temp_minimarket.jpg        # Imagen temporal
├── models/
│   ├── base_model.py          # CRUD base SQLite
│   ├── empleado.py            # Lógica empleados
│   ├── helpers.py             # Funciones Auxiliares
│   ├── producto.py            # Lógica productos
│   └── venta.py               # Lógica ventas
├── views/
│   ├── dashboard.py           # Interfaz principal
│   ├── empleados.py           # Gestión empleados
│   ├── inventario.py          # Gestión inventario
│   ├── login.py               # Pantalla login
│   ├── settings.py            # Configuraciones globales
│   ├── ventas.py              # Proceso ventas
│   └── components/
│       └── forms.py           # Formularios reutilizables
├── db/
│   ├── database.py            # Conexión SQLite
│   ├── minimarket.db          # Base datos principal
│   └── imagenes/              # Imágenes productos/logos
├── .venv/                     # Entorno virtual Python (286 MB)
```

## Funcionalidades

###  Sprint 1 - FUNCIONALIDAD MÍNIMA VIABLE
| Cod. Historia     | Descripción de la Historia    | Puntos    |
|-------------------|-------------------------------|-----------|
| **HUO001**        | Como administrador, quiero poder registrar nuevos productos en el sistema para mantener actualizado el catálogo del minimarket.  | **5** |
| **HUO003**        | Como administrador, quiero ver el stock actual de los productos para saber cuáles debo reabastecer.                              | **3** |
| **HUO005**        | Como administrador, quiero crear nuevas cuentas de usuario para que el personal pueda acceder al sistema.                        | **3** |
| **HUI001**        | Como cajero, quiero registrar una venta de productos para poder procesar la compra de un cliente de manera eficiente.            | **8** |
| **HUI002**        | Como cajero, quiero buscar productos por nombre para poder agregarlos rápidamente a la venta.                                    | **3** |
| **HUI005**        | Como cajero, quiero cancelar una venta en curso para corregir errores antes de completarla.                                      | **3** |  
| **HUO002**        | Como almacenero, quiero actualizar la información de un producto (precio, stock, estado, descripción) para mantener el inventario al día | **5** |
| **HUI003**        | Como cajero, quiero aplicar descuentos a productos o al total de la venta para poder ofrecer promociones a los clientes.         | **5** |  

### Próximos Sprints
- [ ] **Sprint 2**: FUNCIONALIDADES COMPLEMENTARIAS
- [ ] **Sprint 3**: OPTIMIZACIÓN Y PERFORMANCE   
- [ ] **Sprint 4**: EXPANSIÓN DE NEGOCIO


## 👨‍💻 Equipo de Desarrollo 

| Autor             | Cargo      |
|-------------------|------------|
| **Arif Khan Montoya, Rayyan**  | **Developer**  |
| **Campos Acevedo,	Gianfranco**     | **Scrum Master** |
| **Choncen Gutierrez, Daniela**     | **Developer** |
| **Perez Rocha,	Hugo**     | **Developer** |
| **Rodriguez Malca, Rodrigo**     | **Developer** |
| **Zumaeta Calderon, Adriel**     | **Developer** |

---

## EJECUTABLE DISTRIBUIBLE

### Versión para Distribución

El sistema está disponible como **ejecutable independiente** que no requiere Python instalado:

#### **Descarga y Uso:**
- **Archivo:** `SistemaMinimarket_Fixed.exe` (102.4 MB)
- **Ubicación:** `/dist/SistemaMinimarket_Fixed.exe`
- **Plataforma:** Windows 10/11
- **Instalación:** **NO REQUIERE** - Ejecutar directamente

#### **Características del Ejecutable:**
- 🏪 **Sistema completo** con todas las funcionalidades
- 🔐 **Login integrado** (Usuario: `admin`, Contraseña: `admin`)
- 📦 **Gestión de inventarios** con sistema P0001
- 💰 **Punto de venta (POS)** completo
- 📊 **Reportes automáticos** (PDF y Excel)
- 🗄️ **Base de datos SQLite** incluida
- 🖼️ **Interfaz PyQt5** profesional

#### **Para Distribución Comercial:**
1. **Copiar** solo el archivo `SistemaMinimarket_Fixed.exe`
2. **Compartir** con cualquier PC Windows
3. **Ejecutar** con doble clic
4. **¡Listo!** - Sistema completamente funcional

#### **Dependencias Incluidas:**
- Python 3.12
- PyQt5 (Interfaz gráfica)  
- SQLite (Base de datos)
- Pandas + OpenPyXL (Reportes Excel)
- ReportLab (PDFs)
- PIL/Pillow (Imágenes)
- Todas las librerías del sistema

#### **Scripts de Compilación:**
- `crear_exe_simple.bat` - Script principal para generar ejecutable
- `build_exe.ps1` - Script PowerShell alternativo con validaciones
- `SistemaMinimarket_Fixed.spec` - Configuración PyInstaller optimizada

> **Nota:** El ejecutable incluye correcciones de compatibilidad y todas las dependencias de Visual C++ Runtime para funcionamiento sin errores en cualquier PC Windows.

---
