# -*- mode: python ; coding: utf-8 -*-
# Sistema Minimarket Don Manuelito v2.1.0 - MVP
# Configuración PyInstaller actualizada - 2025

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('db/minimarket.db', 'db'),
        ('db/imagenes', 'db/imagenes'),
    ],
    hiddenimports=[
        # PyQt5 Core
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',

        # Pandas y dependencias
        'pandas',
        'pandas.plotting._matplotlib',
        'pandas.core',
        'pandas.io.sql',
        'numpy',

        # Database
        'sqlite3',

        # Matplotlib y backend
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'unittest',  # Requerido por matplotlib

        # Reportes
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.platypus',
        'openpyxl',
        
        # APIs y networking
        'requests',
        'urllib',
        'urllib.request',
        'urllib.parse',
        'http',
        'http.client',
        'ssl',
        'certifi',
        'json',
        
        # XML generation
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'xml.dom',
        'xml.dom.minidom',

        # Módulos del sistema
        'modules.productos.models.producto_model',
        'modules.productos.models.categoria_model',
        'modules.productos.models.tipo_producto_model',
        'modules.productos.models.unidad_medida_model',
        'modules.productos.models.promocion_model',
        'modules.productos.models.promocion_producto_model',
        'modules.productos.service.producto_service',
        'modules.productos.service.promocion_service',
        'modules.productos.service.alertas_service',
        'modules.productos.view.inventario_view',

        'modules.ventas.models.venta_model',
        'modules.ventas.models.detalle_venta_model',
        'modules.ventas.models.devolucion_model',
        'modules.ventas.models.detalle_devolucion_model',
        'modules.ventas.models.comprobante_model',
        'modules.ventas.models.nota_credito_model',
        'modules.ventas.service.venta_service',
        'modules.ventas.service.devolucion_service',
        'modules.ventas.service.comprobante_service',
        'modules.ventas.service.descuentos_service',
        'modules.ventas.view.venta_view',
        'modules.ventas.view.devoluciones_view',
        'modules.ventas.view.dialogo_comprobante',

        'modules.seguridad.models.usuario_model',
        'modules.seguridad.models.empleado_model',
        'modules.seguridad.models.rol_model',
        'modules.seguridad.services.auth_service',
        'modules.seguridad.services.empleado_service',
        'modules.seguridad.view.login',
        'modules.seguridad.view.empleado_view',

        'modules.sistema.models.auditoria_model',
        'modules.sistema.models.backuplog_model',
        'modules.sistema.models.configuracion_model',
        'modules.sistema.auditoria_service',
        'modules.sistema.backup_service',
        'modules.sistema.configuracion_view',

        'modules.reportes.reporte_service',
        'modules.reportes.exportador_service',
        'modules.reportes.reportes_view',

        'shared.dashboard',
        'shared.helpers',
        'shared.components.forms',

        'core.database',
        'core.base_model',
        'core.config',
        'core.exceptions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaMinimarket',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola para versión de producción
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='db\\imagenes\\LOGO.ico',
    version_file=None,
)

