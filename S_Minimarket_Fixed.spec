# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

# Agregar librerías dinámicas de sistema
binaries = []
binaries += collect_dynamic_libs('PyQt5')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('db/imagenes/*.png', 'db/imagenes'),
        ('db/imagenes/*.jpg', 'db/imagenes'),
        ('db/imagenes/*.webp', 'db/imagenes'),
        ('db/imagenes/*.ico', 'db/imagenes'),
        ('db/*.db', 'db'),
        ('models', 'models'),
        ('views', 'views'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'sqlite3',
        'pandas',
        'openpyxl',
        'PIL.Image',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'datetime',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'notebook', 'IPython'],
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
    name='SistemaMinimarket_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='db\\imagenes\\LOGO.ico'
)