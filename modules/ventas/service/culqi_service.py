"""
Servicio de integracion con Culqi - Pasarela de Pagos
Maneja la creacion de tokens, cargos y consultas de transacciones
Implementacion directa con requests (sin SDK de culqi)
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# → Servicio de Culqi para procesar pagos
class CulqiService:
# → Inicializa el servicio con las credenciales desde .env    
    def __init__(self):
        self.public_key = os.getenv('CULQI_PUBLIC_KEY')
        self.secret_key = os.getenv('CULQI_SECRET_KEY')
        self.environment = os.getenv('CULQI_ENVIRONMENT', 'test')
        self.api_url = os.getenv('CULQI_API_URL', 'https://api.culqi.com/v2/')
        
    # Validar que las credenciales existan
        if not self.public_key or not self.secret_key:
            raise ValueError("Credenciales de Culqi no configuradas en .env")
    # → Log de inicializacion        
        print(f"[CulqiService] Inicializado en modo: {self.environment.upper()}")
    
# → Crea un cargo en Culqi usando API REST    
    def crear_cargo(self, token_id, monto, email, descripcion="Venta en Minimarket"):
        """
        Args:
            token_id (str): Token generado desde el frontend
            monto (float): Monto en soles (se convierte a centavos)
            email (str): Email del cliente
            descripcion (str): Descripcion de la compra            
        Returns:
            dict: Resultado del cargo con estado y detalles
        """
        try:
            # Convertir monto a centavos (Culqi trabaja en centavos)
            amount_centavos = int(monto * 100)
            
            # Headers de autenticacion
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            # Payload del cargo
            payload = {
                'amount': amount_centavos,
                'currency_code': 'PEN',
                'email': email,
                'source_id': token_id,
                'description': descripcion
            }
            
            # Realizar peticion POST
            response = requests.post(
                f'{self.api_url}charges',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            cargo = response.json()
            
            # Procesar respuesta
            if response.status_code == 201 and cargo.get('object') == 'charge':
                return {
                    'success': True,
                    'charge_id': cargo.get('id'),
                    'amount': cargo.get('amount') / 100,  # Convertir de centavos a soles
                    'currency': cargo.get('currency_code'),
                    'email': cargo.get('email'),
                    'creation_date': cargo.get('creation_date'),
                    'reference_code': cargo.get('reference_code'),
                    'estado': 'aprobado',
                    'mensaje': 'Pago procesado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'estado': 'rechazado',
                    'mensaje': cargo.get('user_message', cargo.get('merchant_message', 'Error al procesar el pago'))
                }
                
        except requests.exceptions.RequestException as e:
            print(f"[CulqiService] Error de conexion: {str(e)}")
            return {
                'success': False,
                'estado': 'error',
                'mensaje': f'Error de conexion: {str(e)}'
            }
        except Exception as e:
            print(f"[CulqiService] Error al crear cargo: {str(e)}")
            return {
                'success': False,
                'estado': 'error',
                'mensaje': f'Error en la transaccion: {str(e)}'
            }
    
    
    def consultar_cargo(self, charge_id):
        """
        Consultar el estado de un cargo usando API REST
        
        Args:
            charge_id (str): ID del cargo a consultar
            
        Returns:
            dict: Informacion del cargo
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.api_url}charges/{charge_id}',
                headers=headers,
                timeout=10
            )
            
            cargo = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'charge_id': cargo.get('id'),
                    'amount': cargo.get('amount') / 100,
                    'currency': cargo.get('currency_code'),
                    'email': cargo.get('email'),
                    'estado': cargo.get('outcome', {}).get('type', 'unknown'),
                    'creation_date': cargo.get('creation_date'),
                    'reference_code': cargo.get('reference_code')
                }
            else:
                return {
                    'success': False,
                    'mensaje': cargo.get('merchant_message', 'Error al consultar transaccion')
                }
            
        except Exception as e:
            print(f"[CulqiService] Error al consultar cargo: {str(e)}")
            return {
                'success': False,
                'mensaje': f'Error al consultar transaccion: {str(e)}'
            }
    
    
    def crear_token_test(self, card_number, cvv, expiration_month, expiration_year, email):
        """
        SOLO PARA PRUEBAS: Crear token de tarjeta usando API REST
        En produccion esto se hace desde el frontend por seguridad
        
        Args:
            card_number (str): Numero de tarjeta
            cvv (str): CVV
            expiration_month (str): Mes de expiracion (MM)
            expiration_year (str): Año de expiracion (YYYY)
            email (str): Email del titular
            
        Returns:
            dict: Token generado o error
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.public_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'card_number': card_number,
                'cvv': cvv,
                'expiration_month': expiration_month,
                'expiration_year': expiration_year,
                'email': email
            }
            
            response = requests.post(
                f'{self.api_url}tokens',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            token = response.json()
            
            if response.status_code == 201 and token.get('object') == 'token':
                return {
                    'success': True,
                    'token_id': token.get('id'),
                    'mensaje': 'Token generado correctamente'
                }
            else:
                return {
                    'success': False,
                    'mensaje': token.get('user_message', token.get('merchant_message', 'Error al generar token'))
                }
                
        except Exception as e:
            print(f"[CulqiService] Error al crear token: {str(e)}")
            return {
                'success': False,
                'mensaje': f'Error al procesar tarjeta: {str(e)}'
            }
    
    
    def validar_conexion(self):
        """
        Validar que la conexion con Culqi funciona
        
        Returns:
            bool: True si la conexion es exitosa
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.secret_key}',
                'Content-Type': 'application/json'
            }
            
            # Intentar listar los ultimos cargos como prueba de conexion
            response = requests.get(
                f'{self.api_url}charges',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"[CulqiService] Error de conexion: {str(e)}")
            return False
    
    
    def get_public_key(self):
        """Obtener la clave publica para uso en frontend"""
        return self.public_key
