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
- Sistema de pagos integrado con Culqi (5 métodos: Efectivo, Tarjeta, Yape, Plin, Transferencia)
- Módulo de reportes completo con 4 secciones (Ventas, Productos Top 10, Ganancias, Comprobantes)
- Exportación de reportes en PDF y Excel
- Notificaciones de stock bajo
- Roles y permisos de usuario
- Estilos centralizados y componentes reutilizables

**Sprint 3** - OPTIMIZACIÓN Y PERFORMANCE
- Mejoras de rendimiento
- Optimización de consultas a la base de datos
- Refactorización de código

## Tecnologías

- **Python 3.12**
- **PyQt5** - Interfaz gráfica moderna y profesional
- **SQLite** - Base de datos integrada con 17 triggers automáticos
- **bcrypt** - Encriptación segura de contraseñas
- **pandas** - Manejo de datos y análisis
- **matplotlib** - Gráficos y visualizaciones
- **Pillow (PIL)** - Procesamiento de imágenes
- **ReportLab** - Generación de reportes PDF
- **OpenPyXL** - Exportación a Excel
- **requests** - Consumo de APIs externas
- **python-dotenv** - Gestión de variables de entorno
- **culqi** - Integración de pagos electrónicos
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
├── .gitignore                 # Exclusiones git
├── build_exe.ps1              # Script PowerShell para crear .exe
├── main.py                    # Punto de entrada aplicación
├── README.md                  # Documentación proyecto
├── requirements.txt           # Lista dependencias python
├── SistemaMinimarket.spec     # Configuración PyInstaller
├── .venv/                     # Entorno virtual Python
├── core/
│   ├── base_model.py          # Modelo base para herencia
│   ├── config.py              # Configuración global
│   ├── database.py            # Conexión BD y schema (17 tablas, 17 triggers)
│   └── exceptions.py          # Excepciones personalizadas
├── db/
│   ├── imagenes/              # Imágenes de productos
│   └── minimarket.db          # Base de datos SQLite
├── modules/
│   ├── productos/
│   │   ├── models/
│   │   │   ├── categoria_model.py
│   │   │   ├── producto_model.py
│   │   │   ├── promocion_model.py
│   │   │   ├── promocion_producto_model.py
│   │   │   ├── tipo_producto_model.py
│   │   │   └── unidad_medida_model.py
│   │   ├── service/
│   │   │   ├── alertas_service.py         # Alertas de stock
│   │   │   ├── producto_service.py        # Lógica de negocio productos
│   │   │   └── promocion_service.py       # Lógica de promociones
│   │   └── view/
│   │       └── inventario_view.py         # Interfaz inventario
│   ├── ventas/
│   │   ├── models/
│   │   │   ├── comprobante_model.py
│   │   │   ├── detalle_devolucion_model.py
│   │   │   ├── detalle_venta_model.py
│   │   │   ├── devolucion_model.py
│   │   │   ├── nota_credito_model.py
│   │   │   └── venta_model.py
│   │   ├── service/
│   │   │   ├── comprobante_service.py     # Facturación electrónica
│   │   │   ├── culqi_service.py           # Integración de pagos Culqi
│   │   │   ├── descuentos_service.py      # Lógica de descuentos
│   │   │   ├── devolucion_service.py      # Lógica de devoluciones
│   │   │   └── venta_service.py           # Lógica de ventas
│   │   └── view/
│   │       ├── dialogo_comprobante.py     # Diálogo de comprobantes
│   │       ├── dialogo_pago_qr.py         # Diálogo pago Yape/Plin
│   │       ├── dialogo_pago_tarjeta.py    # Diálogo pago con tarjeta
│   │       ├── dialogo_pago_transferencia.py # Diálogo transferencia
│   │       ├── devoluciones_view.py       # Interfaz devoluciones
│   │       └── venta_view.py              # Interfaz punto de venta
│   ├── reportes/
│   │   ├── exportador_service.py          # Exportación PDF/Excel
│   │   ├── reporte_service.py             # Generación de reportes
│   │   └── reportes_view.py               # Interfaz reportes
│   ├── seguridad/
│   │   ├── models/
│   │   │   ├── empleado_model.py
│   │   │   ├── rol_model.py
│   │   │   └── usuario_model.py
│   │   ├── services/
│   │   │   ├── auth_service.py            # Autenticación y autorización
│   │   │   └── empleado_service.py        # Lógica de empleados
│   │   └── view/
│   │       ├── empleado_view.py           # Interfaz empleados
│   │       └── login.py                   # Módulo login
│   └── sistema/
│       ├── models/
│       │   ├── auditoria_model.py
│       │   ├── backuplog_model.py
│       │   └── configuracion_model.py
│       ├── auditoria_service.py           # Logs de auditoría
│       ├── backup_service.py              # Backups automáticos
│       └── configuracion_view.py          # Configuración sistema
└── shared/
    ├── components/
    │   └── forms.py                       # Formularios reutilizables
    ├── dashboard.py                       # Pantalla principal
    ├── helpers.py                         # Funciones auxiliares
    └── styles.py                          # Estilos CSS centralizados
```

## Funcionalidades

### Arquitectura

El sistema implementa una arquitectura MVC modular de 4 capas:

1. **Presentation Layer (View)** - Interfaces PyQt5
2. **Business Logic Layer (Service)** - Lógica de negocio
3. **Data Access Layer (Model)** - Acceso a datos
4. **Infrastructure Layer (Core)** - Configuración y utilidades

### Base de Datos

**18 Tablas Normalizadas:**
- Productos: `tipo_productos`, `categoria_productos`, `unidad_medida`, `productos`, `promocion`, `promocion_producto`
- Seguridad: `rol`, `empleado`, `usuario`
- Ventas: `ventas`, `detalle_venta`, `comprobante`, `devolucion`, `detalle_devolucion`, `nota_credito`
- Sistema: `auditoria`, `backup_log`, `configuracion`, `cache_documentos`

**17 Triggers Automáticos:**
- Validación: cantidad, precio, stock, fechas, descuentos, usuarios
- Cálculo: subtotal automático en detalles
- Stock: actualización automática en ventas/devoluciones/modificaciones
- Total venta: recálculo automático en operaciones
- Integridad: cascada de eliminaciones
- Promociones: validación de fechas y porcentajes
- Seguridad: validación de contraseñas y usernames

### Sprint 1 - FUNCIONALIDAD MÍNIMA VIABLE
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

- Refactorización completa a arquitectura MVC modular
- Separación de responsabilidades en capas (Model-Service-View)
- Normalización de base de datos (17 tablas)
- Implementación de 17 triggers automáticos
- Separación empleado/usuario para autenticación
- Encriptación bcrypt para contraseñas
- Sistema de auditoría y backups
- Optimización de consultas SQL

---

## Sistema de Pagos

### Integración Culqi (Modo TEST)

El sistema incluye integración completa con la pasarela de pagos Culqi para procesar transacciones con tarjeta de crédito/débito.

**Características:**
- Procesamiento seguro de pagos con tarjeta
- Modo TEST para desarrollo y pruebas
- Captura de datos de tarjeta con validación
- Generación de tokens seguros
- Manejo de errores y respuestas de API

### Métodos de Pago Soportados

1. **Efectivo**
   - Confirmación manual del cajero
   - Cálculo automático de vuelto
   - Validación de monto recibido

2. **Tarjeta de Crédito/Débito**
   - Integración con Culqi API
   - Captura segura de datos
   - Validación de número de tarjeta
   - Procesamiento en tiempo real

3. **Yape**
   - Diálogo especializado con código QR
   - Captura de número de operación
   - Validación de transacción

4. **Plin**
   - Interfaz similar a Yape
   - Código QR para escaneo
   - Registro de operación

5. **Transferencia Bancaria**
   - Formulario con datos de cuenta
   - Captura de número de operación
   - Validación de banco y cuenta

**Arquitectura:**
- `culqi_service.py` - Lógica de integración con API
- `dialogo_pago_tarjeta.py` - Interfaz para pago con tarjeta
- `dialogo_pago_qr.py` - Interfaz para Yape/Plin
- `dialogo_pago_transferencia.py` - Interfaz para transferencias
- `.env` - Configuración de claves API (TEST mode)

### Módulo de Reportes

**4 Secciones de Análisis:**

1. **Ventas por Período**
   - Gráfico de líneas con evolución temporal
   - Tabla detallada con fecha, cliente, total y método de pago
   - Filtros por rango de fechas

2. **Productos Top 10**
   - Gráfico de barras con degradado de colores
   - Top 10 productos más vendidos
   - Tabla con cantidad e ingresos totales
   - Optimización de espacio con truncamiento inteligente

3. **Ganancias y Pérdidas**
   - Resumen visual de rendimiento financiero
   - Gráficos comparativos
   - Tabla de análisis detallado

4. **Comprobantes Emitidos**
   - Visualización completa de todos los comprobantes
   - Leyenda con códigos de color:
     * Tipo: Boleta (verde), Factura (azul)
     * Método: Efectivo (verde), Tarjeta (magenta), Yape/Plin (rojo), Transferencia (amarillo)
   - Tabla con datos completos: tipo, serie, número, fecha, cliente, RUC/DNI, total, método
   - Exportación individual por tab

**Exportación:**
- PDF con formato profesional
- Excel con datos estructurados
- Gráficos incluidos en exportaciones
- Filtros aplicados respetados

**Estilos Centralizados:**
- `TablaNoEditableCSS` para consistencia visual
- Componentes reutilizables en `shared/styles.py`
- Diseño responsivo y moderno

---

## Equipo de Desarrollo

| Autor             | Cargo      |
|-------------------|------------|
| **Arif Khan Montoya, Rayyan**  | **Developer**  |
| **Campos Acevedo, Gianfranco**     | **Scrum Master** |
| **Choncen Gutierrez, Daniela**     | **Developer** |
| **Perez Rocha, Hugo**     | **Developer** |
| **Rodriguez Malca, Rodrigo**     | **Developer** |
| **Zumaeta Calderon, Adriel**     | **Developer** |

---

## EJECUTABLE DISTRIBUIBLE

### Versión para Distribución

El sistema está disponible como **ejecutable independiente** que no requiere Python instalado:

#### Características:
- **Sistema completo** con todas las funcionalidades
- **Login integrado** (Usuario: `admin`, Contraseña: `admin`)
- **Gestión de inventarios** con sistema de códigos automáticos
- **Gestión de ventas** con facturación y comprobantes
- **Punto de venta (POS)** completo con descuentos
- **Sistema de pagos integrado** (5 métodos: Efectivo, Tarjeta, Yape, Plin, Transferencia)
- **Integración Culqi** para pagos con tarjeta (modo TEST)
- **Sistema de devoluciones** y notas de crédito
- **Módulo de reportes** con 4 secciones de análisis
- **Reportes automáticos** (PDF y Excel con gráficos)
- **Base de datos SQLite** con 18 tablas y 17 triggers automáticos
- **Interfaz PyQt5** profesional y moderna con estilos centralizados
- **Sistema de auditoría** y backups integrado

#### Dependencias Incluidas:
- Python 3.12
- PyQt5 (Interfaz gráfica)
- SQLite (Base de datos)
- bcrypt (Encriptación)
- Pandas + OpenPyXL (Reportes Excel)
- matplotlib (Gráficos y visualizaciones)
- ReportLab (PDFs)
- PIL/Pillow (Imágenes)
- requests (API comprobantes)
- python-dotenv (Variables de entorno)
- culqi (Integración de pagos)
- setuptools, wheel, PyInstaller
- Todas las librerías del sistema

#### Scripts de Compilación:
- `build_exe.ps1` - Script PowerShell principal para generar ejecutable
- `SistemaMinimarket.spec` - Configuración PyInstaller optimizada

> **Nota:** El ejecutable incluye correcciones de compatibilidad y todas las dependencias necesarias para funcionamiento sin errores en cualquier PC Windows 10/11.

---
