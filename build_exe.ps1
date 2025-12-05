# Script PowerShell para crear ejecutable del Sistema Minimarket Don Manuelito
# Versión 2.1.0 - MVP | Actualizado: 2025-11-21
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SISTEMA MINIMARKET DON MANUELITO v2.1.0" -ForegroundColor Cyan
Write-Host "       BUILD EJECUTABLE - MVP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host

# Variables de configuración
$pythonPath = "python"
$specFile = "SistemaMinimarket.spec"
$exeName = "SistemaMinimarket"
$versionApp = "2.1.0-MVP"

Write-Host "[1/5] Limpiando archivos anteriores..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

Write-Host "[2/5] Verificando Python y dependencias..." -ForegroundColor Yellow
try {
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green

    Write-Host "`nVerificando módulos necesarios..." -ForegroundColor Yellow
    & $pythonPath -c "import PyQt5; print('  ✓ PyQt5 instalado')"
    & $pythonPath -c "import pandas; print('  ✓ Pandas instalado')"
    & $pythonPath -c "import numpy; print('  ✓ NumPy instalado')"
    & $pythonPath -c "import matplotlib; print('  ✓ Matplotlib instalado')"
    & $pythonPath -c "import reportlab; print('  ✓ ReportLab instalado')"
    & $pythonPath -c "import openpyxl; print('  ✓ OpenPyXL instalado')"
    & $pythonPath -c "import PyInstaller; print('  ✓ PyInstaller instalado')"

    Write-Host "`n✅ Todas las dependencias están instaladas" -ForegroundColor Green
} catch {
    Write-Host "❌ Error verificando dependencias: $_" -ForegroundColor Red
    Write-Host "`nPara instalar dependencias faltantes, ejecuta:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host "  pip install --upgrade pyinstaller" -ForegroundColor Cyan
    pause
    exit
}

Write-Host "`n[3/5] Verificando archivos necesarios..." -ForegroundColor Yellow
$requiredFiles = @("main.py", "db/minimarket.db", "db/imagenes/LOGO.ico", $specFile)
$allFilesExist = $true

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file NO ENCONTRADO" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`n❌ Faltan archivos necesarios. Por favor verifica." -ForegroundColor Red
    pause
    exit
}

Write-Host "`n[4/5] Construyendo ejecutable..." -ForegroundColor Yellow
Write-Host "⏳ Este proceso puede tomar 3-7 minutos, por favor espera..." -ForegroundColor Cyan
Write-Host "   • Compilando módulos Python (productos, ventas, devoluciones)" -ForegroundColor Gray
Write-Host "   • Empaquetando dependencias (PyQt5, pandas, matplotlib)" -ForegroundColor Gray
Write-Host "   • Incluyendo base de datos SQLite e imágenes" -ForegroundColor Gray
Write-Host "   • Optimizando y comprimiendo con UPX" -ForegroundColor Gray
Write-Host "   • Creando ejecutable único (.exe)" -ForegroundColor Gray
Write-Host

try {
    & $pythonPath -m PyInstaller --clean --noconfirm $specFile

    if (Test-Path "dist\$exeName.exe") {
        Write-Host
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✓✓✓ EJECUTABLE CREADO EXITOSAMENTE ✓✓✓" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green

        $fileInfo = Get-Item "dist\$exeName.exe"
        $sizeInMB = [Math]::Round($fileInfo.Length / 1MB, 2)

        Write-Host "`n📦 INFORMACIÓN DEL EJECUTABLE:" -ForegroundColor Cyan
        Write-Host "   📂 Ubicación: dist\$exeName.exe" -ForegroundColor White
        Write-Host "   📏 Tamaño: $sizeInMB MB" -ForegroundColor White
        Write-Host "   🏷️  Versión: $versionApp" -ForegroundColor White
        Write-Host "   📅 Fecha creación: $($fileInfo.CreationTime)" -ForegroundColor White

        Write-Host "`n🎯 CARACTERÍSTICAS INCLUIDAS:" -ForegroundColor Cyan
        Write-Host "   ✅ Gestión de Inventario (productos, categorías, stock)" -ForegroundColor White
        Write-Host "   ✅ Sistema de Ventas (POS con descuentos y promociones)" -ForegroundColor White
        Write-Host "   ✅ Devoluciones (validación por peso/unidad)" -ForegroundColor White
        Write-Host "   ✅ Reportes y Gráficos (ventas, productos, Excel/PDF)" -ForegroundColor White
        Write-Host "   ✅ Control de Usuarios y Seguridad" -ForegroundColor White
        Write-Host "   ✅ Base de datos SQLite integrada" -ForegroundColor White

        Write-Host "`n📤 PARA DISTRIBUIR:" -ForegroundColor Cyan
        Write-Host "   1. Comparte SOLO el archivo: dist\$exeName.exe" -ForegroundColor White
        Write-Host "   2. NO necesita Python instalado en la PC destino" -ForegroundColor White
        Write-Host "   3. Funciona en Windows 10/11 (64-bit)" -ForegroundColor White
        Write-Host "   4. Incluye base de datos e imágenes integradas" -ForegroundColor White
        Write-Host "   5. Todo el sistema en un solo archivo ejecutable" -ForegroundColor White

        Write-Host "`n⚠️  IMPORTANTE:" -ForegroundColor Yellow
        Write-Host "   • Primera ejecución puede tardar 5-10 segundos" -ForegroundColor White
        Write-Host "   • Algunos antivirus pueden requerir autorización" -ForegroundColor White
        Write-Host "   • Si Windows SmartScreen aparece: 'Más información' > 'Ejecutar de todas formas'" -ForegroundColor White
        Write-Host "   • Usuario de prueba: admin / Contraseña: admin123" -ForegroundColor White
        Write-Host
        Write-Host "========================================" -ForegroundColor Green
        
        Write-Host "`n[5/5] Opciones finales..." -ForegroundColor Yellow
        $openFolder = Read-Host "`n¿Deseas abrir la carpeta con el ejecutable? (s/n)"
        if ($openFolder -eq 's' -or $openFolder -eq 'S') {
            Start-Process "explorer.exe" -ArgumentList "/select,`"$PWD\dist\$exeName.exe`""
        }

        $testExe = Read-Host "`n¿Deseas probar el ejecutable ahora? (s/n)"
        if ($testExe -eq 's' -or $testExe -eq 'S') {
            Write-Host "`n🚀 Iniciando $exeName.exe..." -ForegroundColor Cyan
            Start-Process "dist\$exeName.exe"
        }
        
    } else {
        Write-Host
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "❌ ERROR: No se pudo crear el ejecutable" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "`nPosibles causas:" -ForegroundColor Yellow
        Write-Host "  • Archivos fuente con errores" -ForegroundColor White
        Write-Host "  • Dependencias faltantes" -ForegroundColor White
        Write-Host "  • Permisos insuficientes" -ForegroundColor White
        Write-Host "`nRevisa los mensajes de error anteriores para más detalles." -ForegroundColor White
    }
    
} catch {
    Write-Host
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ ERROR DURANTE LA CONSTRUCCIÓN" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Mensaje de error: $_" -ForegroundColor Red
    Write-Host "`nSi el problema persiste:" -ForegroundColor Yellow
    Write-Host "  1. Verifica que todas las dependencias estén instaladas" -ForegroundColor White
    Write-Host "  2. Ejecuta: pip install --upgrade pyinstaller" -ForegroundColor White
    Write-Host "  3. Revisa que no haya errores en el código" -ForegroundColor White
}

Write-Host
Write-Host "========================================" -ForegroundColor Gray
Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")