## Service de Comprobantes - Sistema Minimarket
## Maneja la emisión de boletas/facturas y consultas de DNI/RUC

import os
import json
import requests
import sqlite3
from datetime import datetime
from core.database import db

class ComprobanteService:
    def __init__(self):
        # Cargarmos las credenciales desde el .env 
        env = self._cargar_env()

        # Asignamos las variables de configuración de la API
        self.NUBEFACT_API_URL = env.get("NUBEFACT_API_URL", "").strip()
        self.NUBEFACT_API_KEY = env.get("NUBEFACT_API_KEY", "").strip()

        self.FACTILIZA_API_DNI_URL = env.get("FACTILIZA_API_DNI_URL", "").strip()
        self.FACTILIZA_API_RUC_URL = env.get("FACTILIZA_API_RUC_URL", "").strip()
        self.FACTILIZA_API_KEY = env.get("FACTILIZA_API_KEY", "").strip()
        
        # Crear carpeta para comprobantes
        self.COMPROBANTES_DIR = self._crear_carpeta_comprobantes()

# → Carga las credenciales de API desde .env
    def _cargar_env(self):
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
    
# → Crea carpeta para guardar comprobantes
    def _crear_carpeta_comprobantes(self):
        try:
            # Obtener ruta del escritorio
            import os
            escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
            carpeta_comprobantes = os.path.join(escritorio, "Comprobantes_Minimarket")
            
            # Crear carpeta si no existe
            if not os.path.exists(carpeta_comprobantes):
                os.makedirs(carpeta_comprobantes)
            
            return carpeta_comprobantes
        except Exception as e:
            print(f"Error creando carpeta de comprobantes: {e}")
            # Fallback a carpeta del proyecto
            from core.config import BASE_DIR
            carpeta_fallback = os.path.join(BASE_DIR, "comprobantes")
            if not os.path.exists(carpeta_fallback):
                os.makedirs(carpeta_fallback)
            return carpeta_fallback

# → Consulta DNI en API - FACTILIZA
    def consultar_dni_api(self, numero):
        try:
            # URL correcta para FACTILIZA DNI
            url = f"https://api.factiliza.com/v1/dni/info/{numero}"
            headers = {
                "Authorization": f"Bearer {self.FACTILIZA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            print(f"Consultando DNI: {numero}")
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Log de depuración
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            # Validar respuesta HTTP
            if response.status_code != 200:
                return None, f"Error HTTP {response.status_code}: {response.text}"
            
            # Validar JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                return None, f"Respuesta no válida (JSON): {str(e)}"
            
            # Validar estructura de respuesta
            if not isinstance(data, dict):
                return None, "Respuesta no es un objeto JSON válido"
            
            if data.get('success') and data.get('status') == 200:
                datos = data.get('data', {})
                if not datos:
                    return None, "No se encontraron datos en la respuesta"
                return datos, None
            else:
                message = data.get('message', 'Error desconocido en API')
                return None, message
                
        except requests.exceptions.Timeout:
            return None, "Timeout: La API tardó demasiado en responder"
        except requests.exceptions.ConnectionError:
            return None, "Error de conexión: No se pudo conectar a la API"
        except requests.exceptions.RequestException as e:
            return None, f"Error de request: {str(e)}"
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"

# → Consulta RUC en API - FACTILIZA    
    def consultar_ruc_api(self, numero):
        try:
            # URL correcta para FACTILIZA RUC
            url = f"https://api.factiliza.com/v1/ruc/info/{numero}"
            headers = {
                "Authorization": f"Bearer {self.FACTILIZA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            print(f"Consultando RUC: {numero}")
            print(f"URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Log de depuración
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            # Validar respuesta HTTP
            if response.status_code != 200:
                return None, f"Error HTTP {response.status_code}: {response.text}"
            
            # Validar JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                return None, f"Respuesta no válida (JSON): {str(e)}"
            
            # Validar estructura de respuesta
            if not isinstance(data, dict):
                return None, "Respuesta no es un objeto JSON válido"
            
            if data.get('success') and data.get('status') == 200:
                datos = data.get('data', {})
                if not datos:
                    return None, "No se encontraron datos en la respuesta"
                return datos, None
            else:
                message = data.get('message', 'Error desconocido en API')
                return None, message
                
        except requests.exceptions.Timeout:
            return None, "Timeout: La API tardó demasiado en responder"
        except requests.exceptions.ConnectionError:
            return None, "Error de conexión: No se pudo conectar a la API"
        except requests.exceptions.RequestException as e:
            return None, f"Error de request: {str(e)}"
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"

# → Obtiene datos de DNI/RUC desde cache o API
    def obtener_datos_documento(self, numero, tipo):
        conn = db.get_connection()
        cur = conn.cursor()

        # Buscar en caché
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

            if tipo == 'DNI':
                nombre_completo = f"{row[1]} {row[2]} {row[3]}".strip()
                return {'success': True, 'nombre_completo': nombre_completo, 'num_documento': numero, 'tipo': 'boleta', 'origen': 'cache'}
            else:  # RUC
                return {'success': True, 'razon_social': row[4], 'direccion': row[5], 'ruc': numero, 'tipo': 'factura', 'origen': 'cache'}

        # Si no está en caché, consultamos la API
        if tipo == 'DNI':
            data, error = self.consultar_dni_api(numero)
            if error:
                conn.close()
                return {'success': False, 'error': error}
            if data:
                try:
                    # Usar el formato de la nueva API FACTILIZA
                    nombres = data.get('nombres', '')
                    apellido_paterno = data.get('apellido_paterno', '')
                    apellido_materno = data.get('apellido_materno', '')
                    nombre_completo = data.get('nombre_completo', f"{apellido_paterno} {apellido_materno}, {nombres}".strip())
                    
                    cur.execute("""
                        INSERT INTO cache_documentos (numero_documento, tipo_documento, nombres, apellido_paterno, apellido_materno)
                        VALUES (?, 'DNI', ?, ?, ?)
                    """, (numero, nombres, apellido_paterno, apellido_materno))
                    conn.commit()
                except:
                    pass  # Si ya existe, ignorar
                conn.close()
                
                return {'success': True, 'nombre_completo': nombre_completo, 'num_documento': numero, 'tipo': 'boleta', 'origen': 'api'}
        elif tipo == 'RUC':
            data, error = self.consultar_ruc_api(numero)
            if error:
                conn.close()
                return {'success': False, 'error': error}
            if data:
                try:
                    cur.execute("""
                        INSERT INTO cache_documentos (numero_documento, tipo_documento, razon_social, direccion, departamento, provincia, distrito, estado, condicion)
                        VALUES (?, 'RUC', ?, ?, ?, ?, ?, ?, ?)
                    """, (numero, data.get('nombre_o_razon_social', ''), data.get('direccion', ''), data.get('departamento', ''), data.get('provincia', ''), data.get('distrito', ''), data.get('estado', ''), data.get('condicion', '')))
                    conn.commit()
                except:
                    pass  # Si ya existe, ignorar
                conn.close()
                return {'success': True, 'razon_social': data.get('nombre_o_razon_social', ''), 'direccion': data.get('direccion', ''), 'ruc': numero, 'tipo': 'factura', 'origen': 'api'}

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

    def emitir_comprobante(self, venta_id, tipo, datos_cliente=None, metodo_pago='efectivo'):
        """
        Emite un comprobante (boleta o factura) y genera archivos PDF y XML
        datos_cliente: dict con num_documento, nombre_completo para boleta
                      o ruc, razon_social, direccion para factura
        metodo_pago: yape, plin, transferencia, efectivo
        """
        tipo_norm = str(tipo).lower()
        serie, numero = self._siguiente_numero(tipo_norm)
        ruc_emisor = self._ruc_emisor()

        conn = db.get_connection()
        cur = conn.cursor()

        # Obtener datos de la venta
        cur.execute("""
            SELECT v.total_venta, v.fecha_venta, v.id_empleado
            FROM ventas v
            WHERE v.id_venta = ?
        """, (venta_id,))
        venta_row = cur.fetchone()
        if not venta_row:
            conn.close()
            return {'success': False, 'error': 'Venta no encontrada'}
        
        monto_total = float(venta_row[0])
        fecha_emision = venta_row[1]

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
                if datos_cliente.get('ruc'):
                    num_doc = datos_cliente.get('ruc')
        else:
            # Valores por defecto
            if tipo_norm == 'boleta':
                num_doc = '00000000'
                nombre_cli = 'Cliente Genérico'

        # Generar código del comprobante
        codigo_comprobante = f"{serie}-{str(numero).zfill(8)}"
        
        # Generar archivos PDF y XML
        pdf_path = None
        xml_path = None
        try:
            pdf_path = self._generar_pdf_comprobante(
                codigo_comprobante, tipo_norm, serie, numero,
                fecha_emision, num_doc, nombre_cli, razon_social,
                direccion, monto_total, metodo_pago, venta_id
            )
            xml_path = self._generar_xml_comprobante(
                codigo_comprobante, tipo_norm, serie, numero,
                fecha_emision, num_doc, nombre_cli, razon_social,
                direccion, monto_total, metodo_pago, venta_id
            )
        except Exception as e:
            print(f"Error generando archivos: {e}")

        # Insertar comprobante en BD
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
                xml_path or '', pdf_path or '', 'emitido', venta_id
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
            'codigo': codigo_comprobante,
            'pdf_path': pdf_path,
            'xml_path': xml_path
        }
    
    def _generar_pdf_comprobante(self, codigo, tipo, serie, numero, fecha, num_doc,
                                  nombre_cli, razon_social, direccion, monto_total,
                                  metodo_pago, venta_id):
        """Genera el archivo PDF del comprobante"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            
            # Nombre del archivo
            filename = f"{tipo.upper()}_{codigo}.pdf"
            filepath = os.path.join(self.COMPROBANTES_DIR, filename)
            
            # Crear documento
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            titulo = f"{tipo.upper()} ELECTRÓNICA"
            elements.append(Paragraph(titulo, styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Información del comprobante
            info_data = [
                ['Serie:', serie, 'Número:', str(numero).zfill(8)],
                ['Código:', codigo, 'Fecha:', fecha[:10] if isinstance(fecha, str) else fecha.strftime('%Y-%m-%d')],
                ['Método de Pago:', metodo_pago.upper(), '', '']
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # Datos del cliente
            cliente_titulo = Paragraph('<b>DATOS DEL CLIENTE</b>', styles['Heading3'])
            elements.append(cliente_titulo)
            elements.append(Spacer(1, 6))
            
            if tipo == 'boleta':
                cliente_data = [
                    ['DNI:', num_doc or '00000000'],
                    ['Nombre:', nombre_cli or 'Cliente Genérico']
                ]
            else:  # factura
                cliente_data = [
                    ['RUC:', num_doc or ''],
                    ['Razón Social:', razon_social or ''],
                    ['Dirección:', direccion or '']
                ]
            
            cliente_table = Table(cliente_data, colWidths=[2*inch, 5*inch])
            cliente_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(cliente_table)
            elements.append(Spacer(1, 20))
            
            # Detalle de productos
            detalle_titulo = Paragraph('<b>DETALLE DE LA VENTA</b>', styles['Heading3'])
            elements.append(detalle_titulo)
            elements.append(Spacer(1, 6))
            
            # Obtener detalles de la venta
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.nombre_producto, dv.cantidad_detalle, dv.precio_unitario_detalle, dv.subtotal_detalle
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE dv.id_venta = ?
            """, (venta_id,))
            detalles = cur.fetchall()
            conn.close()
            
            # Tabla de productos
            productos_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
            for det in detalles:
                productos_data.append([
                    det[0],
                    f"{det[1]:.2f}",
                    f"S/ {det[2]:.2f}",
                    f"S/ {det[3]:.2f}"
                ])
            
            productos_table = Table(productos_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            productos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(productos_table)
            elements.append(Spacer(1, 20))
            
            # Total
            total_data = [['TOTAL:', f"S/ {monto_total:.2f}"]]
            total_table = Table(total_data, colWidths=[5*inch, 2*inch])
            total_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            elements.append(total_table)
            
            # Construir PDF
            doc.build(elements)
            
            return filepath
        except Exception as e:
            print(f"Error generando PDF: {e}")
            return None
    
    def _generar_xml_comprobante(self, codigo, tipo, serie, numero, fecha, num_doc,
                                  nombre_cli, razon_social, direccion, monto_total,
                                  metodo_pago, venta_id):
        """Genera el archivo XML del comprobante"""
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            # Nombre del archivo
            filename = f"{tipo.upper()}_{codigo}.xml"
            filepath = os.path.join(self.COMPROBANTES_DIR, filename)
            
            # Crear estructura XML
            root = ET.Element('Comprobante')
            root.set('tipo', tipo.upper())
            root.set('version', '2.1')
            
            # Datos del comprobante
            datos = ET.SubElement(root, 'DatosComprobante')
            ET.SubElement(datos, 'Serie').text = serie
            ET.SubElement(datos, 'Numero').text = str(numero).zfill(8)
            ET.SubElement(datos, 'FechaEmision').text = fecha[:10] if isinstance(fecha, str) else fecha.strftime('%Y-%m-%d')
            ET.SubElement(datos, 'MetodoPago').text = metodo_pago.upper()
            
            # Datos del cliente
            cliente = ET.SubElement(root, 'Cliente')
            if tipo == 'boleta':
                ET.SubElement(cliente, 'TipoDocumento').text = 'DNI'
                ET.SubElement(cliente, 'NumeroDocumento').text = num_doc or '00000000'
                ET.SubElement(cliente, 'NombreCompleto').text = nombre_cli or 'Cliente Genérico'
            else:
                ET.SubElement(cliente, 'TipoDocumento').text = 'RUC'
                ET.SubElement(cliente, 'NumeroDocumento').text = num_doc or ''
                ET.SubElement(cliente, 'RazonSocial').text = razon_social or ''
                ET.SubElement(cliente, 'Direccion').text = direccion or ''
            
            # Detalle de productos
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.nombre_producto, p.id_producto, dv.cantidad_detalle, 
                       dv.precio_unitario_detalle, dv.subtotal_detalle
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE dv.id_venta = ?
            """, (venta_id,))
            detalles = cur.fetchall()
            conn.close()
            
            items = ET.SubElement(root, 'Items')
            for det in detalles:
                item = ET.SubElement(items, 'Item')
                ET.SubElement(item, 'Codigo').text = det[1]
                ET.SubElement(item, 'Descripcion').text = det[0]
                ET.SubElement(item, 'Cantidad').text = f"{det[2]:.2f}"
                ET.SubElement(item, 'PrecioUnitario').text = f"{det[3]:.2f}"
                ET.SubElement(item, 'Subtotal').text = f"{det[4]:.2f}"
            
            # Totales
            totales = ET.SubElement(root, 'Totales')
            ET.SubElement(totales, 'Total').text = f"{monto_total:.2f}"
            
            # Formatear XML con indentación
            xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            
            # Guardar archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml_string)
            
            return filepath
        except Exception as e:
            print(f"Error generando XML: {e}")
            return None