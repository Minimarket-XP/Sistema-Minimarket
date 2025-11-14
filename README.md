# Sistema Minimarket Don Manuelito

APLICACIÓN DE GESTIÓN DE VENTAS E INVENTARIO EN MINIMARKET "Don Manuelito"

## Descripción

Sistema de gestión completo para minimarket que incluye manejo de inventario, ventas, empleados y reportes. Desarrollado siguiendo la metodología SCRUM con arquitectura modular escalable.

## Estado del Proyecto

**Sprint 1** - FUNCIONALIDAD MÍNIMA VIABLE
- CRUD completo de productos
- Manejo de imágenes
- Sistema de categorías
- Interfaz moderna con PyQt5

**Sprint 2** - FUNCIONALIDADES COMPLEMENTARIAS
- Gestión de clientes y empleados
- Sistema de ventas con descuentos y devoluciones
- Reportes de ventas en PDF y Excel
- Notificaciones de stock bajo
- Roles y permisos de usuario

**Sprint 3** - OPTIMIZACIÓN Y PERFORMANCE
- Mejoras de rendimiento
- Optimización de consultas a la base de datos
- Refactorización de código

## Tecnologías

- **Python 3.x**
- **PyQt5** - Interfaz gráfica moderna y profesional
- **SQLite** - Base de datos integrada
- **pandas** - Manejo de datos
- **Pillow (PIL)** - Procesamiento de imágenes
- **ReportLab** - Generación de reportes PDF
- **OpenPyXL** - Exportación a Excel
- **requests** - Consumo de APIs externas
- **setuptools, wheel, PyInstaller** - Empaquetado y distribución

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
├── .venv/                     # Entorno virtual Python (286 MB)
├── core/
│   ├── base_model.py               # Modelos base
│   ├── config.py                   # Configuración global
│   └── database.py                 # Conexión base de datos
├── db/
│   ├── imagenes/                   # Imágenes de la aplicación
│   └── minimarket.db               # Base de datos SQLite
├── modules/
│   ├── clientes
│   │   ├── cliente_model.py        # Lógica clientes
│   │   └── cliente_view.py         # Interfaz clientes
│   ├── empleados
│   │   ├── empleado_model.py       # Lógica empleados
│   │   └── empleado_view.py        # Interfaz empleados
│   ├── productos
│   │   ├── alertas.py              # Lógica alertas productos
│   │   ├── inventario_view.py      # Interfaz inventario
│   │   └── producto_model.py       # Lógica productos
│   ├── reportes
│   │   ├── exportador.py           # Lógica exportar reportes
│   │   └── reporte_view.py         # Interfaz reportes
│   └── ventas
│       ├── comprobantes_api.py     # Lógica comprobantes
│       ├── descuentos.py           # Lógica descuentos
│       ├── devoluciones_view.py    # Interfaz devoluciones
│       ├── venta_model.py          # Lógica ventas
│       └── venta_view.py           # Interfaz ventas
├── shared/
│   ├── components
│       └── forms.py                # Formularios reutilizables
│   ├── dashboard.py                # Pantalla principal
│   ├── helpers.py                  # Funciones auxiliares
│   └── login.py                    # Módulo login
└── .env                        # Variables entorno (no subir a git)
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

### Sprint 2 - FUNCIONALIDADES COMPLEMENTARIAS
| Cod. Historia | Descripción de la Historia                                                                                                | Puntos |
|---------------|---------------------------------------------------------------------------------------------------------------------------|--------|
| **HUI004**    | Como cajero, quiero realizar devoluciones de productos para gestionar los reembolsos de manera adecuada.                  | **8**  |
| **HUI006**    | Como cajero, quiero registrar devoluciones de productos para gestionar correctamente las transacciones con los clientes.  | **5**  |
| **HUO004**    | Como almacenero, quiero recibir notificaciones de stock bajo para poder reabastecer los productos antes de que se agoten. | **5**  |
| **HUI008**    | Como administrador, quiero poder generar reportes de ventas diarias, semanales y mensuales para analizar el rendimiento del negocio.  | **5**  |
| **HUO006**    | Como administrador, quiero asignar roles a los usuarios para definir sus permisos y las acciones que pueden realizar.  | **3**  |
| **HUO007**    | Como administrador, quiero modificar la información de los usuarios para mantener actualizada la base de datos del personal.    | **3**  |
| **HUO009**    | Como administrador, quiero poder ver qué productos son los más vendidos para optimizar la gestión de inventario y compras.  | **5**  |
| **HUO010**    | Como administrador, quiero poder generar un reporte de ganancias y pérdidas para evaluar la salud financiera del minimarket.    | **5**  |

### Sprint 3 - OPTIMIZACIÓN Y PERFORMANCE

----------------------------------------------------------

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

#### **Características:**
- **Sistema completo** con todas las funcionalidades
- **Login integrado** (Usuario: `admin`, Contraseña: `admin`)
- **Gestión de inventarios** con sistema P0001
- **Gestión de ventas** con facturación y recibos
- **Punto de venta (POS)** completo
- **Reportes automáticos** (PDF y Excel)
- **Base de datos SQLite** incluida
- **Interfaz PyQt5** profesional

#### **Dependencias Incluidas:**
- Python 3.12
- PyQt5 (Interfaz gráfica)  
- SQLite (Base de datos)
- Pandas + OpenPyXL (Reportes Excel)
- ReportLab (PDFs)
- PIL/Pillow (Imágenes)
- requests (API comprobantes)
- setuptools
- wheel
- PyInstaller
- matplotlib
- Todas las librerías del sistema

#### **Scripts de Compilación:**
- `crear_exe_simple.bat` - Script principal para generar ejecutable
- `build_exe.ps1` - Script PowerShell alternativo con validaciones
- `SistemaMinimarket_Fixed.spec` - Configuración PyInstaller optimizada

> **Nota:** El ejecutable incluye correcciones de compatibilidad y todas las dependencias de Visual C++ Runtime para funcionamiento sin errores en cualquier PC Windows.

---
