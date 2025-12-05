"""
Servicio de Backup Automático
Sistema Minimarket Don Manuelito
Gestiona backups automáticos y manuales de la base de datos
"""

import os
import shutil
import gzip
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional, List
from core.database import db
from core.config import BASE_DIR


class BackupService:
    """
    Servicio para realizar backups automáticos y manuales de la base de datos.
    Características:
    - Backups automáticos diarios a las 2:00 AM
    - Compresión GZIP para ahorrar espacio
    - Retención de backups (últimos 30 días)
    - Verificación de integridad de backups
    - Registro de operaciones en backup_log
    """
    
    def __init__(self):
        """Inicializa el servicio de backup"""
        self.db_path = os.path.join(BASE_DIR, 'db', 'minimarket.db')
        self.backup_dir = self._crear_directorio_backups()
        self.running = False
        self.thread = None
        
        # Configuración
        self.hora_backup = "02:00"  # 2:00 AM
        self.dias_retencion = 30  # Mantener últimos 30 días
        self.compresion = True  # Comprimir backups
    
    def _crear_directorio_backups(self) -> str:
        """Crea el directorio de backups si no existe"""
        try:
            # Intentar crear en Documentos del usuario
            documentos = os.path.join(os.path.expanduser("~"), "Documents")
            backup_dir = os.path.join(documentos, "Backups_Minimarket")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            return backup_dir
        except Exception as e:
            print(f"Error creando directorio en Documentos: {e}")
            # Fallback a carpeta del proyecto
            backup_dir = os.path.join(BASE_DIR, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            return backup_dir
    
    def realizar_backup_manual(self, id_usuario: int = 1) -> Tuple[bool, str, Optional[str]]:
        """
        Realiza un backup manual de la base de datos
        
        Args:
            id_usuario: ID del usuario que solicita el backup
        
        Returns:
            Tupla (success, mensaje, ruta_archivo)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"minimarket_manual_{timestamp}.db"
            
            if self.compresion:
                nombre_archivo += ".gz"
            
            ruta_backup = os.path.join(self.backup_dir, nombre_archivo)
            
            # Verificar que la BD existe
            if not os.path.exists(self.db_path):
                return False, "Base de datos no encontrada", None
            
            # Realizar backup
            if self.compresion:
                success = self._backup_comprimido(ruta_backup)
            else:
                success = self._backup_simple(ruta_backup)
            
            if success:
                # Verificar integridad
                if self._verificar_integridad(ruta_backup):
                    # Registrar en log
                    self._registrar_backup(
                        tipo='manual',
                        estado='exitoso',
                        ubicacion=ruta_backup,
                        descripcion='Backup manual realizado por usuario',
                        usuario_id=id_usuario
                    )
                    
                    # Obtener tamaño del archivo
                    tamanio_mb = os.path.getsize(ruta_backup) / (1024 * 1024)
                    
                    return True, f"Backup realizado exitosamente ({tamanio_mb:.2f} MB)", ruta_backup
                else:
                    os.remove(ruta_backup)  # Eliminar backup corrupto
                    return False, "Backup creado pero falló la verificación de integridad", None
            else:
                return False, "Error al crear el archivo de backup", None
                
        except Exception as e:
            self._registrar_backup(
                tipo='manual',
                estado='fallido',
                ubicacion='',
                descripcion=f'Error: {str(e)}',
                usuario_id=id_usuario
            )
            return False, f"Error al realizar backup: {str(e)}", None
    
    def _backup_simple(self, ruta_destino: str) -> bool:
        """Copia simple de la base de datos"""
        try:
            # Cerrar cualquier conexión abierta
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(ruta_destino)
            
            # Usar API de backup de SQLite (más seguro)
            conn.backup(backup_conn)
            
            backup_conn.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error en backup simple: {e}")
            return False
    
    def _backup_comprimido(self, ruta_destino: str) -> bool:
        """Backup comprimido con GZIP"""
        try:
            # Primero crear backup temporal sin comprimir
            temp_backup = ruta_destino.replace('.gz', '_temp.db')
            
            if not self._backup_simple(temp_backup):
                return False
            
            # Comprimir el archivo
            with open(temp_backup, 'rb') as f_in:
                with gzip.open(ruta_destino, 'wb', compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar temporal
            os.remove(temp_backup)
            
            return True
        except Exception as e:
            print(f"Error en backup comprimido: {e}")
            # Limpiar archivos temporales
            temp_backup = ruta_destino.replace('.gz', '_temp.db')
            if os.path.exists(temp_backup):
                os.remove(temp_backup)
            return False
    
    def _verificar_integridad(self, ruta_backup: str) -> bool:
        """Verifica la integridad del backup"""
        try:
            if ruta_backup.endswith('.gz'):
                # Descomprimir temporalmente para verificar
                temp_db = ruta_backup.replace('.gz', '_verify.db')
                
                with gzip.open(ruta_backup, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Verificar
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                conn.close()
                
                # Limpiar
                os.remove(temp_db)
                
                return result[0] == 'ok'
            else:
                # Verificar directamente
                conn = sqlite3.connect(ruta_backup)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                conn.close()
                
                return result[0] == 'ok'
                
        except Exception as e:
            print(f"Error verificando integridad: {e}")
            return False
    
    def _registrar_backup(self, tipo: str, estado: str, ubicacion: str, 
                         descripcion: str, usuario_id: int):
        """Registra el backup en la tabla backup_log"""
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO backup_log (
                    tipo_backup, estado_backup, ubicacion_archivo_backup,
                    descripcion_backup, usuario_responsable
                ) VALUES (?, ?, ?, ?, ?)
            """, (tipo, estado, ubicacion, descripcion, usuario_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error registrando backup en log: {e}")
    
    def limpiar_backups_antiguos(self):
        """Elimina backups anteriores a la fecha de retención"""
        try:
            fecha_limite = datetime.now() - timedelta(days=self.dias_retencion)
            eliminados = 0
            
            for archivo in os.listdir(self.backup_dir):
                if not archivo.startswith('minimarket_'):
                    continue
                
                ruta_completa = os.path.join(self.backup_dir, archivo)
                fecha_archivo = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                
                if fecha_archivo < fecha_limite:
                    os.remove(ruta_completa)
                    eliminados += 1
                    print(f"Backup antiguo eliminado: {archivo}")
            
            return eliminados
        except Exception as e:
            print(f"Error limpiando backups antiguos: {e}")
            return 0
    
    def listar_backups(self) -> List[dict]:
        """Lista todos los backups disponibles"""
        try:
            backups = []
            
            for archivo in os.listdir(self.backup_dir):
                if not archivo.startswith('minimarket_'):
                    continue
                
                ruta_completa = os.path.join(self.backup_dir, archivo)
                stat = os.stat(ruta_completa)
                
                backups.append({
                    'nombre': archivo,
                    'ruta': ruta_completa,
                    'tamanio_mb': stat.st_size / (1024 * 1024),
                    'fecha': datetime.fromtimestamp(stat.st_mtime),
                    'tipo': 'manual' if 'manual' in archivo else 'automatico',
                    'comprimido': archivo.endswith('.gz')
                })
            
            # Ordenar por fecha (más recientes primero)
            backups.sort(key=lambda x: x['fecha'], reverse=True)
            
            return backups
        except Exception as e:
            print(f"Error listando backups: {e}")
            return []
    
    def restaurar_backup(self, ruta_backup: str, id_usuario: int = 1) -> Tuple[bool, str]:
        """
        Restaura la base de datos desde un backup
        
        Args:
            ruta_backup: Ruta del archivo de backup
            id_usuario: ID del usuario que solicita la restauración
        
        Returns:
            Tupla (success, mensaje)
        """
        try:
            if not os.path.exists(ruta_backup):
                return False, "Archivo de backup no encontrado"
            
            # Verificar integridad antes de restaurar
            if not self._verificar_integridad(ruta_backup):
                return False, "El backup está corrupto o no es válido"
            
            # Crear backup de seguridad de la BD actual
            backup_seguridad = os.path.join(
                self.backup_dir,
                f"minimarket_pre_restauracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db.gz"
            )
            self._backup_comprimido(backup_seguridad)
            
            # Descomprimir si es necesario
            if ruta_backup.endswith('.gz'):
                temp_db = os.path.join(BASE_DIR, 'db', 'minimarket_temp.db')
                
                with gzip.open(ruta_backup, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Cerrar todas las conexiones
                db._connection = None
                
                # Reemplazar BD actual
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                shutil.move(temp_db, self.db_path)
            else:
                # Cerrar conexiones
                db._connection = None
                
                # Reemplazar BD actual
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                shutil.copy2(ruta_backup, self.db_path)
            
            # Registrar restauración
            self._registrar_backup(
                tipo='restauracion',
                estado='exitoso',
                ubicacion=ruta_backup,
                descripcion=f'Base de datos restaurada desde backup',
                usuario_id=id_usuario
            )
            
            return True, "Base de datos restaurada exitosamente. Reinicie la aplicación."
            
        except Exception as e:
            return False, f"Error al restaurar backup: {str(e)}"
    
    # ==================== BACKUP AUTOMÁTICO ====================
    
    def iniciar_backup_automatico(self):
        """Inicia el servicio de backup automático en segundo plano"""
        if self.running:
            return False, "El servicio de backup automático ya está en ejecución"
        
        self.running = True
        self.thread = threading.Thread(target=self._bucle_backup_automatico, daemon=True)
        self.thread.start()
        
        return True, f"Backup automático iniciado (diario a las {self.hora_backup})"
    
    def detener_backup_automatico(self):
        """Detiene el servicio de backup automático"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True, "Servicio de backup automático detenido"
    
    def _bucle_backup_automatico(self):
        """Bucle principal del servicio de backup automático"""
        print(f"Servicio de backup automático iniciado")
        ultimo_backup_fecha = None
        
        while self.running:
            try:
                ahora = datetime.now()
                hora_actual = ahora.strftime("%H:%M")
                fecha_actual = ahora.date()
                
                # Verificar si es hora de hacer backup
                if hora_actual == self.hora_backup and ultimo_backup_fecha != fecha_actual:
                    print(f"Iniciando backup automático...")
                    
                    timestamp = ahora.strftime('%Y%m%d_%H%M%S')
                    nombre_archivo = f"minimarket_auto_{timestamp}.db"
                    
                    if self.compresion:
                        nombre_archivo += ".gz"
                    
                    ruta_backup = os.path.join(self.backup_dir, nombre_archivo)
                    
                    # Realizar backup
                    if self.compresion:
                        success = self._backup_comprimido(ruta_backup)
                    else:
                        success = self._backup_simple(ruta_backup)
                    
                    if success and self._verificar_integridad(ruta_backup):
                        tamanio_mb = os.path.getsize(ruta_backup) / (1024 * 1024)
                        
                        self._registrar_backup(
                            tipo='completo',
                            estado='exitoso',
                            ubicacion=ruta_backup,
                            descripcion=f'Backup automático diario ({tamanio_mb:.2f} MB)',
                            usuario_id=1  # Sistema
                        )
                        
                        print(f"Backup automático completado: {nombre_archivo} ({tamanio_mb:.2f} MB)")
                        
                        # Limpiar backups antiguos
                        eliminados = self.limpiar_backups_antiguos()
                        if eliminados > 0:
                            print(f"Eliminados {eliminados} backups antiguos")
                    else:
                        self._registrar_backup(
                            tipo='completo',
                            estado='fallido',
                            ubicacion=ruta_backup,
                            descripcion='Backup automático falló o no pasó verificación',
                            usuario_id=1
                        )
                        print("Backup automático falló")
                    
                    ultimo_backup_fecha = fecha_actual
                
                # Esperar 1 minuto antes de verificar de nuevo
                time.sleep(60)
                
            except Exception as e:
                print(f"Error en bucle de backup automático: {e}")
                time.sleep(300)  # Esperar 5 minutos en caso de error
        
        print("Servicio de backup automático detenido")


# Instancia global del servicio
backup_service = BackupService()
