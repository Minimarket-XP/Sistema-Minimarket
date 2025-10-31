# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Recopilar todos los modulos y archivos de PyQt5
datas_pyqt5 = collect_data_files('PyQt5', include_py_files=True)
hiddenimports_pyqt5 = collect_submodules('PyQt5')

binaries = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('db/imagenes', 'db/imagenes'),
        ('db/*.db', 'db'),
        ('modules', 'modules'),
        ('shared', 'shared'),
        ('core', 'core'),
    ] + datas_pyqt5,
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'PyQt5.sip',
        'sqlite3',
        'pandas',
        'openpyxl',
        'PIL',
        'PIL.Image',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
    ] + hiddenimports_pyqt5,
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