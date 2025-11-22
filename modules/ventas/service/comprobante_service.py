## Service de Comprobantes - Sistema Minimarket
## Maneja la emisión de boletas/facturas y consultas de DNI/RUC

from core.database import db
import json
from urllib import request

class ComprobanteService:

    def __init__(self):
        pass

    # ==================== CONSULTAS API ====================

    def _cargar_env(self):
        """Carga las credenciales de API desde .env"""
        try:
            import os
            from core.config import BASE_DIR
            ruta = os.path.join(BASE_DIR, ".env")
            if not os.path.exists(ruta):
                return {}
            env = {}
            with open(ruta, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip()
            return env
        except Exception:
            return {}

    def consultar_dni_api(self, numero):
        """Consulta DNI en API externa"""
        try:
            env = self._cargar_env()
            url = env.get("DNI_API_URL", "").strip()
            key = env.get("DNI_API_KEY", "").strip()

            if not url or not key:
                return None, "API no configurada"

            payload = json.dumps({"dni": str(numero)}).encode("utf-8")
            req = request.Request(url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            req.add_header("Authorization", f"Bearer {key}")

            with request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode("utf-8")
                resultado = json.loads(data)

                if resultado.get('success'):
                    return resultado['data'], None
                else:
                    return None, resultado.get('message', 'Error desconocido')

        except Exception as e:
            return None, f"Error de conexión: {str(e)}"

    def consultar_ruc_api(self, numero):
        """Consulta RUC en API externa"""
        try:
            env = self._cargar_env()
            url = env.get("RUC_API_URL", "").strip()
            key = env.get("DNI_API_KEY", "").strip()

            if not url or not key:
                return None, "API no configurada"

            payload = json.dumps({"ruc": str(numero)}).encode("utf-8")
            req = request.Request(url, data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            req.add_header("Authorization", f"Bearer {key}")

            with request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode("utf-8")
                resultado = json.loads(data)

                if resultado.get('success'):
                    return resultado['data'], None
                else:
                    return None, resultado.get('message', 'Error desconocido')

        except Exception as e:
            return None, f"Error de conexión: {str(e)}"

    # ==================== CACHE DE DOCUMENTOS ====================

    def obtener_datos_documento(self, numero, tipo):
        """
        Obtiene datos de DNI/RUC desde cache o API
        Retorna dict con datos formateados según tipo
        """
        conn = db.get_connection()
        cur = conn.cursor()

        # Buscar en cache
        cur.execute("""
            SELECT tipo_documento, nombres, apellido_paterno, apellido_materno,
                   razon_social, direccion
            FROM cache_documentos 
            WHERE numero_documento = ?
        """, (numero,))

        row = cur.fetchone()

        if row:
            # Actualizar última consulta
            cur.execute("""
                UPDATE cache_documentos 
                SET ultima_consulta = CURRENT_TIMESTAMP 
                WHERE numero_documento = ?
            """, (numero,))
            conn.commit()
            conn.close()

            # Formatear según tipo
            if tipo == 'DNI':
                nombre_completo = f"{row[1]} {row[2]} {row[3]}".strip()
                return {
                    'success': True,
                    'nombre_completo': nombre_completo,
                    'num_documento': numero,
                    'tipo': 'boleta',
                    'origen': 'cache'
                }
            else:  # RUC
                return {
                    'success': True,
                    'razon_social': row[4],
                    'direccion': row[5],
                    'ruc': numero,
                    'tipo': 'factura',
                    'origen': 'cache'
                }

        # No está en cache → Consultar API
        if tipo == 'DNI':
            data, error = self.consultar_dni_api(numero)
            if error:
                conn.close()
                return {'success': False, 'error': error}

            if data:
                try:
                    cur.execute("""
                        INSERT INTO cache_documentos 
                        (numero_documento, tipo_documento, nombres, apellido_paterno, apellido_materno)
                        VALUES (?, 'DNI', ?, ?, ?)
                    """, (numero, data.get('nombres', ''), data.get('apellido_paterno', ''),
                          data.get('apellido_materno', '')))
                    conn.commit()
                except:
                    pass  # Si ya existe, ignorar

                conn.close()
                nombre_completo = f"{data.get('nombres', '')} {data.get('apellido_paterno', '')} {data.get('apellido_materno', '')}".strip()
                return {
                    'success': True,
                    'nombre_completo': nombre_completo,
                    'num_documento': numero,
                    'tipo': 'boleta',
                    'origen': 'api'
                }

        elif tipo == 'RUC':
            data, error = self.consultar_ruc_api(numero)
            if error:
                conn.close()
                return {'success': False, 'error': error}

            if data:
                try:
                    cur.execute("""
                        INSERT INTO cache_documentos 
                        (numero_documento, tipo_documento, razon_social, direccion, 
                         departamento, provincia, distrito, estado, condicion)
                        VALUES (?, 'RUC', ?, ?, ?, ?, ?, ?, ?)
                    """, (numero, data.get('nombre_o_razon_social', ''), data.get('direccion', ''),
                          data.get('departamento', ''), data.get('provincia', ''),
                          data.get('distrito', ''), data.get('estado', ''), data.get('condicion', '')))
                    conn.commit()
                except:
                    pass  # Si ya existe, ignorar

                conn.close()
                return {
                    'success': True,
                    'razon_social': data.get('nombre_o_razon_social', ''),
                    'direccion': data.get('direccion', ''),
                    'ruc': numero,
                    'tipo': 'factura',
                    'origen': 'api'
                }

        conn.close()
        return {'success': False, 'error': 'No se pudo obtener información'}

    # ==================== EMISIÓN DE COMPROBANTES ====================

    def _ruc_emisor(self):
        """Obtiene el RUC del emisor desde configuración"""
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave = ?", ('ruc_empresa',))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ''

    def _siguiente_numero(self, tipo):
        """Calcula el siguiente número de comprobante"""
        tipo = str(tipo).lower()
        serie = 'B001' if tipo == 'boleta' else 'F001'
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(MAX(CAST(numero_comprobante AS INTEGER)), 0) FROM comprobante WHERE tipo_comprobante = ? AND serie_comprobante = ?",
            (tipo, serie)
        )
        last = cur.fetchone()[0]
        conn.close()
        return serie, int(last) + 1

    def emitir_comprobante(self, venta_id, tipo, datos_cliente=None):
        """
        Emite un comprobante (boleta o factura)
        datos_cliente: dict con num_documento, nombre_completo para boleta
                      o ruc, razon_social, direccion para factura
        """
        tipo_norm = str(tipo).lower()
        serie, numero = self._siguiente_numero(tipo_norm)
        ruc_emisor = self._ruc_emisor()

        conn = db.get_connection()
        cur = conn.cursor()

        # Obtener total de la venta
        cur.execute("SELECT total_venta FROM ventas WHERE id_venta = ?", (venta_id,))
        venta_row = cur.fetchone()
        monto_total = float(venta_row[0]) if venta_row else 0.0

        # Preparar datos según tipo
        num_doc = None
        nombre_cli = None
        razon_social = None
        direccion = None

        if datos_cliente:
            if tipo_norm == 'boleta':
                num_doc = datos_cliente.get('num_documento', '00000000')
                nombre_cli = datos_cliente.get('nombre_completo', 'Cliente Genérico')
            else:  # factura
                razon_social = datos_cliente.get('razon_social', '')
                direccion = datos_cliente.get('direccion', '')
                ruc_emisor = datos_cliente.get('ruc', '')
        else:
            # Valores por defecto
            if tipo_norm == 'boleta':
                num_doc = '00000000'
                nombre_cli = 'Cliente Genérico'

        # Insertar comprobante
        cur.execute(
            """
            INSERT INTO comprobante (
                tipo_comprobante, numero_comprobante, serie_comprobante,
                monto_total_comprobante, ruc_emisor, razon_social, direccion_fiscal,
                num_documento, nombre_cliente, xml_path, pdf_path, estado_sunat, id_venta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tipo_norm, str(numero), serie, monto_total, ruc_emisor if tipo_norm == 'factura' else None,
                razon_social, direccion, num_doc, nombre_cli,
                '', '', 'pendiente', venta_id
            )
        )

        cid = cur.lastrowid
        conn.commit()
        conn.close()

        return {
            'success': True,
            'id': cid,
            'tipo': tipo_norm.upper(),
            'serie': serie,
            'numero': numero,
            'codigo': f"{serie}-{str(numero).zfill(8)}"
        }

