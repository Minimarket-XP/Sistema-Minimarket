from core.base_model import BaseModel
import re

class ClienteModel(BaseModel):
    def __init__(self):
        columns = ['id', 'tipo_documento', 'num_documento', 'nombre', 'direccion', 'telefono', 'email', 'activo']
        super().__init__('clientes', columns)

    def validar_documento(self, tipo_doc, num_doc):
        t = (tipo_doc or '').strip().upper()
        n = (num_doc or '').strip()
        if t == 'DNI':
            return bool(re.fullmatch(r"\d{8}", n))
        if t == 'RUC':
            return bool(re.fullmatch(r"\d{11}", n))
        if t == 'GENERICO':
            return True
        return False

    def crear_cliente(self, tipo_doc, num_doc, nombre, direccion='', telefono='', email=''):
        if not nombre or not nombre.strip():
            raise ValueError('El nombre es obligatorio')
        if not self.validar_documento(tipo_doc, num_doc):
            raise ValueError('Documento inválido')
        if self.contarRegistro('num_documento = ?', (num_doc,)) > 0:
            raise ValueError('El documento ya existe')
        data = {
            'tipo_documento': tipo_doc.strip().upper(),
            'num_documento': num_doc.strip(),
            'nombre': nombre.strip(),
            'direccion': (direccion or '').strip(),
            'telefono': (telefono or '').strip(),
            'email': (email or '').strip(),
            'activo': 1
        }
        return self.crearRegistro(data)

    def obtener_cliente(self, num_documento):
        rows = self.get_all('num_documento = ?', (num_documento,))
        return rows[0] if rows else None

    def listar_clientes_activos(self):
        return self.get_all('activo = 1')

    def actualizar_cliente(self, cliente_id, datos):
        if 'nombre' in datos and not (datos['nombre'] or '').strip():
            raise ValueError('El nombre es obligatorio')
        if 'tipo_documento' in datos or 'num_documento' in datos:
            tipo = datos.get('tipo_documento')
            numero = datos.get('num_documento')
            current = self.obtenerRegistro(cliente_id)
            tipo = (tipo if tipo is not None else current.get('tipo_documento'))
            numero = (numero if numero is not None else current.get('num_documento'))
            if not self.validar_documento(tipo, numero):
                raise ValueError('Documento inválido')
            if numero != current.get('num_documento'):
                if self.contarRegistro('num_documento = ? AND id != ?', (numero, cliente_id)) > 0:
                    raise ValueError('El documento ya existe')
        return self.actualizarRegistroID(cliente_id, datos)

    def desactivar_cliente(self, cliente_id):
        return self.actualizarRegistroID(cliente_id, {'activo': 0})

    def buscar_clientes(self, termino):
        return self.buscarRegistro(termino, ['nombre', 'num_documento'])