"""
Service de Integración con Nubefact
Sistema de Facturación Electrónica - API Nubefact
Documentación: https://nubefact.com/api
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core.database import db

# → Servicio para integración con Nubefact
class NubefactService:
# → Inicializa el servicio cargando credenciales desde .env
    def __init__(self):
        self.config = self._cargar_configuracion()
        self.token = self.config.get('NUBEFACT_API_KEY', '')
        self.ruc_empresa = self.config.get('NUBEFACT_RUC_EMPRESA', '')
        self.modo_produccion = self.config.get('NUBEFACT_MODO_PRODUCCION', '0') == '1'
        
        # URL base (incluye el merchant token en la URL)
        self.base_url = self.config.get('NUBEFACT_API_URL', '')
        
        # Series de comprobantes
        self.serie_boleta = self.config.get('NUBEFACT_SERIE_BOLETA', 'B001')
        self.serie_factura = self.config.get('NUBEFACT_SERIE_FACTURA', 'F001')
        self.serie_nota_credito = self.config.get('NUBEFACT_SERIE_NOTA_CREDITO', 'BC01')
        
        # Endpoints (mantener para compatibilidad con test)
        self.endpoint_boleta = '/boleta'
        self.endpoint_factura = '/factura'

# → Obtiene el siguiente número de serie y correlativo para un tipo de comprobante    
    def _cargar_configuracion(self) -> Dict[str, str]:
        try:
            from core.config import BASE_DIR
            ruta_env = os.path.join(BASE_DIR, '.env')
            
            if not os.path.exists(ruta_env):
                print("ADVERTENCIA: Archivo .env no encontrado")
                return {}
            
            config = {}
            with open(ruta_env, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorar comentarios y líneas vacías
                    if not line or line.startswith('#'):
                        continue
                    
                    # Manejar líneas multi-línea (RSA keys)
                    if '="' in line:
                        key, value = line.split('="', 1)
                        value = value.rstrip('"')
                        config[key.strip()] = value
                    elif '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
            
            return config
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return {}
    
# → Genera headers para peticiones HTTP
    def _headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

# → Obtiene el siguiente número de serie y correlativo para un tipo de comprobante    
    def _obtener_datos_empresa(self) -> Dict[str, str]:
        conn = db.get_connection()
        cur = conn.cursor()
        
        datos = {
            'ruc': self.ruc_empresa,
            'razon_social': 'Minimarket Don Manuelito',
            'direccion': 'Av. Principal 123',
            'ubigeo': '150101',  # Lima-Lima-Lima por defecto
            'urbanizacion': '-',
            'distrito': 'Lima',
            'provincia': 'Lima',
            'departamento': 'Lima'
        }
        
        # Intentar obtener de BD
        try:
            cur.execute("SELECT clave, valor FROM configuracion WHERE clave IN (?, ?, ?, ?)",
                       ('ruc_empresa', 'nombre_empresa', 'direccion_empresa', 'ubigeo_empresa'))
            rows = cur.fetchall()
            for row in rows:
                if row[0] == 'ruc_empresa':
                    datos['ruc'] = row[1]
                elif row[0] == 'nombre_empresa':
                    datos['razon_social'] = row[1]
                elif row[0] == 'direccion_empresa':
                    datos['direccion'] = row[1]
                elif row[0] == 'ubigeo_empresa':
                    datos['ubigeo'] = row[1]
        except Exception as e:
            print(f"Error obteniendo datos de empresa: {e}")
        finally:
            conn.close()
        
        return datos
    
# → Obtiene los items de una venta para el detalle del comprobante
    def _obtener_detalle_venta(self, venta_id: str) -> List[Dict]:
        # Mapeo de unidades de medida a códigos SUNAT
        unidad_map = {
            'unidad': 'NIU',
            'unidades': 'NIU',
            'und': 'NIU',
            'kilogramo': 'KGM',
            'kilogramos': 'KGM',
            'kg': 'KGM',
            'gramo': 'GRM',
            'gramos': 'GRM',
            'litro': 'LTR',
            'litros': 'LTR',
            'metro': 'MTR',
            'metros': 'MTR',
            'caja': 'BX',
            'cajas': 'BX',
            'paquete': 'PK',
            'paquetes': 'PK',
            'docena': 'DZN',
            'docenas': 'DZN'
        }
        
        conn = db.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    p.id_producto,
                    p.nombre_producto,
                    um.nombre_unidad,
                    dv.cantidad_detalle,
                    dv.precio_unitario_detalle,
                    dv.subtotal_detalle,
                    COALESCE(dv.descuento_aplicado, 0) as descuento
                FROM detalle_venta dv
                JOIN productos p ON dv.id_producto = p.id_producto
                JOIN unidad_medida um ON p.id_unidad_medida = um.id_unidad_medida
                WHERE dv.id_venta = ?
            """, (venta_id,))
            
            rows = cur.fetchall()
            
            items = []
            for idx, row in enumerate(rows, start=1):
                # Calcular IGV (18% en Perú)
                valor_unitario = float(row[4]) / 1.18  # Precio sin IGV
                igv_unitario = float(row[4]) - valor_unitario
                valor_total = valor_unitario * float(row[3])
                igv_total = igv_unitario * float(row[3])
                
                # Convertir unidad de medida a código SUNAT
                unidad_nombre = (row[2] or '').lower().strip()
                codigo_unidad = unidad_map.get(unidad_nombre, 'NIU')  # Default: NIU (Unidad)
                
                # Descuento: string vacío si es 0, número si tiene valor
                descuento = float(row[6])
                descuento_str = '' if descuento == 0 else round(descuento, 2)
                
                item = {
                    'unidad_de_medida': codigo_unidad,
                    'codigo': row[0] or f'PROD{idx:04d}',
                    'descripcion': row[1],
                    'cantidad': float(row[3]),
                    'valor_unitario': round(valor_unitario, 2),
                    'precio_unitario': round(float(row[4]), 2),
                    'descuento': descuento_str,
                    'subtotal': round(valor_total, 2),
                    'tipo_de_igv': 1,
                    'igv': round(igv_total, 2),
                    'total': round(float(row[5]), 2),
                    'anticipo_regularizacion': False
                }
                items.append(item)
            
            return items
        except Exception as e:
            print(f"Error obteniendo detalle de venta: {e}")
            return []
        finally:
            conn.close()
    
    def emitir_boleta(self, venta_id: str, datos_cliente: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Args:
            venta_id: ID de la venta en BD local
            datos_cliente: {'dni': '12345678', 'nombre_completo': 'Juan Pérez'}
        
        Returns:
            (success, data, error)
        """
        try:
            # Obtener datos de la venta
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT total_venta, fecha_venta, descuento_venta
                FROM ventas 
                WHERE id_venta = ?
            """, (venta_id,))
            venta = cur.fetchone()
            conn.close()
            
            if not venta:
                return False, None, "Venta no encontrada"
            
            total_venta = float(venta[0])
            fecha_emision = venta[1]
            descuento_global = float(venta[2]) if venta[2] else 0.0
            
            # Obtener siguiente número de serie
            serie, correlativo = self._obtener_siguiente_numero('boleta')
            
            print(f"🔍 DEBUG: Emitiendo boleta con serie={serie}, correlativo={correlativo}")
            
            # Datos de la empresa
            empresa = self._obtener_datos_empresa()
            
            # Validar datos del cliente
            dni_cliente = datos_cliente.get('dni', '00000000')
            nombre_cliente = datos_cliente.get('nombre_completo', 'CLIENTE')
            
            if not dni_cliente or dni_cliente == '':
                dni_cliente = '00000000'
            if not nombre_cliente or len(nombre_cliente) < 3:
                nombre_cliente = 'CLIENTE GENERICO'
            
            print(f"🔍 DEBUG Cliente: DNI={dni_cliente}, Nombre={nombre_cliente}")
            
            # Detalle de items
            items = self._obtener_detalle_venta(venta_id)
            if not items:
                return False, None, "No se encontraron items en la venta"
            
            # Calcular totales con IGV
            gravada = total_venta / 1.18
            igv = total_venta - gravada
            
            # Construir payload para Nubefact (formato exacto SUNAT)
            payload = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': 2,
                'serie': serie,
                'numero': correlativo,
                'sunat_transaction': 1,
                'cliente_tipo_de_documento': 1,
                'cliente_numero_de_documento': dni_cliente,
                'cliente_denominacion': nombre_cliente,
                'cliente_direccion': '',
                'cliente_email': '',
                'fecha_de_emision': fecha_emision[:10] if isinstance(fecha_emision, str) else fecha_emision.strftime('%d-%m-%Y'),
                'moneda': 1,
                'porcentaje_de_igv': 18.00,
                'descuento_global': '',
                'total_descuento': '',
                'total_gravada': round(gravada, 2),
                'total_igv': round(igv, 2),
                'total': round(total_venta, 2),
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': False,
                'items': items
            }
            
            # Realizar petición a Nubefact
            url = self.base_url
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            
            print(f"Nubefact Response Status: {response.status_code}")
            print(f"Nubefact Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Consultar comprobante para obtener enlaces PDF/XML/CDR
                success_consulta, data_consulta, error_consulta = self.consultar_comprobante('boleta', serie, correlativo)
                if success_consulta and data_consulta:
                    # Actualizar data con enlaces de la consulta
                    data['enlace_del_pdf'] = data_consulta.get('enlace_del_pdf', '')
                    data['enlace_del_xml'] = data_consulta.get('enlace_del_xml', '')
                    data['enlace_del_cdr'] = data_consulta.get('enlace_del_cdr', '')
                
                # Guardar en BD local
                self._guardar_comprobante_local(
                    venta_id=venta_id,
                    tipo='boleta',
                    serie=serie,
                    numero=correlativo,
                    monto_total=total_venta,
                    datos_cliente=datos_cliente,
                    respuesta_sunat=data
                )
                
                return True, data, None
            else:
                error_msg = f"Error HTTP {response.status_code}: {response.text}"
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            return False, None, "Timeout: La API de Nubefact tardó demasiado en responder"
        except requests.exceptions.ConnectionError:
            return False, None, "Error de conexión con Nubefact"
        except Exception as e:
            return False, None, f"Error inesperado: {str(e)}"
    
    def emitir_factura(self, venta_id: str, datos_cliente: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Emite una factura electrónica en Nubefact
        
        Args:
            venta_id: ID de la venta en BD local
            datos_cliente: {'ruc': '20123456789', 'razon_social': 'Empresa SAC', 'direccion': '...'}
        
        Returns:
            (success, data, error)
        """
        try:
            # Obtener datos de la venta
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT total_venta, fecha_venta, descuento_venta
                FROM ventas 
                WHERE id_venta = ?
            """, (venta_id,))
            venta = cur.fetchone()
            conn.close()
            
            if not venta:
                return False, None, "Venta no encontrada"
            
            total_venta = float(venta[0])
            fecha_emision = venta[1]
            descuento_global = float(venta[2]) if venta[2] else 0.0
            
            # Obtener siguiente número de serie
            serie, correlativo = self._obtener_siguiente_numero('factura')
            
            # Datos de la empresa
            empresa = self._obtener_datos_empresa()
            
            # Detalle de items
            items = self._obtener_detalle_venta(venta_id)
            if not items:
                return False, None, "No se encontraron items en la venta"
            
            # Calcular totales con IGV
            gravada = total_venta / 1.18
            igv = total_venta - gravada
            
            # Construir payload para Nubefact (formato exacto SUNAT - factura requiere dirección)
            payload = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': 1,
                'serie': serie,
                'numero': correlativo,
                'sunat_transaction': 1,
                'cliente_tipo_de_documento': 6,
                'cliente_numero_de_documento': datos_cliente.get('ruc', ''),
                'cliente_denominacion': datos_cliente.get('razon_social', ''),
                'cliente_direccion': datos_cliente.get('direccion', ''),
                'cliente_email': datos_cliente.get('email', ''),
                'fecha_de_emision': fecha_emision[:10] if isinstance(fecha_emision, str) else fecha_emision.strftime('%d-%m-%Y'),
                'moneda': 1,
                'porcentaje_de_igv': 18.00,
                'descuento_global': '',
                'total_descuento': '',
                'total_gravada': round(gravada, 2),
                'total_igv': round(igv, 2),
                'total': round(total_venta, 2),
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': False,
                'items': items
            }
            
            # Realizar petición a Nubefact
            url = self.base_url
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            
            print(f"Nubefact Response Status: {response.status_code}")
            print(f"Nubefact Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Consultar comprobante para obtener enlaces PDF/XML/CDR
                success_consulta, data_consulta, error_consulta = self.consultar_comprobante('factura', serie, correlativo)
                if success_consulta and data_consulta:
                    # Actualizar data con enlaces de la consulta
                    data['enlace_del_pdf'] = data_consulta.get('enlace_del_pdf', '')
                    data['enlace_del_xml'] = data_consulta.get('enlace_del_xml', '')
                    data['enlace_del_cdr'] = data_consulta.get('enlace_del_cdr', '')
                
                # Guardar en BD local
                self._guardar_comprobante_local(
                    venta_id=venta_id,
                    tipo='factura',
                    serie=serie,
                    numero=correlativo,
                    monto_total=total_venta,
                    datos_cliente=datos_cliente,
                    respuesta_sunat=data
                )
                
                return True, data, None
            else:
                error_msg = f"Error HTTP {response.status_code}: {response.text}"
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            return False, None, "Timeout: La API de Nubefact tardó demasiado en responder"
        except requests.exceptions.ConnectionError:
            return False, None, "Error de conexión con Nubefact"
        except Exception as e:
            return False, None, f"Error inesperado: {str(e)}"
    
    def emitir_nota_credito(self, venta_id: str, motivo: str, tipo_nota: str = '01') -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Emite una nota de crédito electrónica en Nubefact
        
        Args:
            venta_id: ID de la venta original
            motivo: Motivo de la nota de crédito
            tipo_nota: Código de tipo (01=Anulación, 07=Devolución, etc.)
        
        Returns:
            (success, data, error)
        """
        try:
            # Obtener comprobante original
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT tipo_comprobante, serie_comprobante, numero_comprobante, monto_total_comprobante
                FROM comprobante
                WHERE id_venta = ?
                ORDER BY id_comprobante DESC
                LIMIT 1
            """, (venta_id,))
            comprobante = cur.fetchone()
            
            if not comprobante:
                conn.close()
                return False, None, "Comprobante original no encontrado"
            
            tipo_original = comprobante[0]
            serie_original = comprobante[1]
            numero_original = comprobante[2]
            monto = float(comprobante[3])
            
            # Obtener fecha de venta
            cur.execute("SELECT fecha_venta FROM ventas WHERE id_venta = ?", (venta_id,))
            fecha_venta = cur.fetchone()[0]
            conn.close()
            
            # Determinar tipo de comprobante para nota de crédito
            tipo_comprobante = 7 if tipo_original == 'boleta' else 8  # 7=NC Boleta, 8=NC Factura
            
            # Obtener siguiente número
            serie_nc, correlativo_nc = self._obtener_siguiente_numero('nota_credito')
            
            # Detalle de items (los mismos de la venta original)
            items = self._obtener_detalle_venta(venta_id)
            
            # Calcular totales
            gravada = monto / 1.18
            igv = monto - gravada
            
            payload = {
                'operacion': 'generar_comprobante',
                'tipo_de_comprobante': tipo_comprobante,
                'serie': serie_nc,
                'numero': correlativo_nc,
                'sunat_transaction': 1,
                'fecha_de_emision': datetime.now().strftime('%Y-%m-%d'),
                'moneda': 1,
                'porcentaje_de_igv': 18.00,
                'total_gravada': round(gravada, 2),
                'total_igv': round(igv, 2),
                'total': round(monto, 2),
                'documento_que_se_modifica_tipo': '03' if tipo_original == 'boleta' else '01',
                'documento_que_se_modifica_serie': serie_original,
                'documento_que_se_modifica_numero': numero_original,
                'tipo_de_nota_de_credito': tipo_nota,
                'motivo_o_sustento_de_nota': motivo,
                'enviar_automaticamente_a_la_sunat': True,
                'enviar_automaticamente_al_cliente': False,
                'items': items
            }
            
            url = self.base_url
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data, None
            else:
                return False, None, f"Error HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def consultar_comprobante(self, tipo: str, serie: str, numero: int) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Consulta el estado de un comprobante en Nubefact
        
        Args:
            tipo: 'boleta', 'factura', 'nota_credito'
            serie: Serie del comprobante
            numero: Número correlativo
        
        Returns:
            (success, data, error)
        """
        try:
            tipo_map = {
                'boleta': 2,
                'factura': 1,
                'nota_credito': 7
            }
            
            payload = {
                'operacion': 'consultar_comprobante',
                'tipo_de_comprobante': tipo_map.get(tipo, 3),
                'serie': serie,
                'numero': numero
            }
            
            url = self.base_url
            response = requests.post(url, json=payload, headers=self._headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, data, None
            else:
                return False, None, f"Error HTTP {response.status_code}"
                
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def _obtener_siguiente_numero(self, tipo: str) -> Tuple[str, int]:
        """
        Obtiene la siguiente serie y número para un tipo de comprobante
        
        Args:
            tipo: 'boleta', 'factura', 'nota_credito', 'nota_debito'
        
        Returns:
            (serie, correlativo)
        """
        serie_map = {
            'boleta': self.serie_boleta,
            'factura': self.serie_factura,
            'nota_credito': self.serie_nota_credito,
            'nota_debito': 'BD01'
        }
        
        serie = serie_map.get(tipo, self.serie_boleta)
        
        conn = db.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT COALESCE(MAX(CAST(numero_comprobante AS INTEGER)), 0)
                FROM comprobante
                WHERE serie_comprobante = ?
            """, (serie,))
            ultimo = cur.fetchone()[0]
            return serie, ultimo + 1
        except Exception as e:
            print(f"Error obteniendo siguiente número: {e}")
            return serie, 1
        finally:
            conn.close()
    
    def _guardar_comprobante_local(self, venta_id: str, tipo: str, serie: str, numero: int,
                                    monto_total: float, datos_cliente: Dict, respuesta_sunat: Dict):
        """
        Guarda el comprobante emitido en la base de datos local
        
        Args:
            venta_id: ID de la venta
            tipo: 'boleta' o 'factura'
            serie: Serie del comprobante
            numero: Número correlativo
            monto_total: Monto total del comprobante
            datos_cliente: Datos del cliente
            respuesta_sunat: Respuesta completa de Nubefact/SUNAT
        """
        conn = db.get_connection()
        cur = conn.cursor()
        
        try:
            # Extraer datos de la respuesta
            enlace_pdf = respuesta_sunat.get('enlace_del_pdf', '')
            enlace_xml = respuesta_sunat.get('enlace_del_xml', '')
            enlace_cdr = respuesta_sunat.get('enlace_del_cdr', '')
            aceptada_sunat = respuesta_sunat.get('aceptada_por_sunat', False)
            
            # Determinar datos del cliente según tipo
            if tipo == 'boleta':
                num_doc = datos_cliente.get('dni', '00000000')
                nombre_cliente = datos_cliente.get('nombre_completo', 'Cliente Genérico')
                razon_social = None
                direccion = None
            else:
                num_doc = datos_cliente.get('ruc', '')
                nombre_cliente = None
                razon_social = datos_cliente.get('razon_social', '')
                direccion = datos_cliente.get('direccion', '')
            
            cur.execute("""
                INSERT INTO comprobante (
                    tipo_comprobante, numero_comprobante, serie_comprobante,
                    monto_total_comprobante, ruc_emisor, razon_social, direccion_fiscal,
                    num_documento, nombre_cliente, xml_path, pdf_path, 
                    estado_sunat, id_venta, respuesta_api
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tipo, str(numero), serie, monto_total,
                self.ruc_empresa, razon_social, direccion,
                num_doc, nombre_cliente,
                enlace_xml, enlace_pdf,
                'aceptado' if aceptada_sunat else 'pendiente',
                venta_id,
                json.dumps(respuesta_sunat, ensure_ascii=False)
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error guardando comprobante local: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def validar_configuracion(self) -> Tuple[bool, str]:
        """
        Valida que la configuración de Nubefact esté completa
        
        Returns:
            (valida, mensaje)
        """
        if not self.token:
            return False, "Token de Nubefact no configurado"
        
        if not self.ruc_empresa:
            return False, "RUC de empresa no configurado"
        
        if not self.base_url:
            return False, "URL de API no configurada"
        
        return True, "Configuración válida"
