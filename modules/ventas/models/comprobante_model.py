import sqlite3

class Comprobante:
    def __init__(self, id_comprobante, tipo_comprobante, numero_comprobante, serie_comprobante,
                 fecha_emision_comprobante, monto_total_comprobante, ruc_emisor,
                 razon_social, direccion_fiscal, num_documento, nombre_cliente, estado_sunat):
        self.id_comprobante = id_comprobante
        self.tipo_comprobante = tipo_comprobante
        self.numero_comprobante = numero_comprobante
        self.serie_comprobante = serie_comprobante
        self.fecha_emision_comprobante = fecha_emision_comprobante
        self.monto_total_comprobante = monto_total_comprobante
        self.ruc_emisor = ruc_emisor
        self.razon_social = razon_social
        self.direccion_fiscal = direccion_fiscal
        self.num_documento = num_documento
        self.nombre_cliente = nombre_cliente
        self.estado_sunat = estado_sunat

    def guardar_en_DB(self):
        conn = sqlite3.connect('sistema_minimarket.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comprobantes (id_comprobante, tipo_comprobante, numero_comprobante, serie_comprobante,
                                      fecha_emision_comprobante, monto_total_comprobante, ruc_emisor,
                                      razon_social, direccion_fiscal, num_documento, nombre_cliente, estado_sunat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (self.id_comprobante, self.tipo_comprobante, self.numero_comprobante,
                                                            self.serie_comprobante, self.fecha_emision_comprobante,
                                                            self.monto_total_comprobante, self.ruc_emisor,
                                                            self.razon_social, self.direccion_fiscal,
                                                            self.num_documento, self.nombre_cliente,
                                                            self.estado_sunat))
        conn.commit()
        conn.close()
    
    @staticmethod
    def obtener_por_id(id_comprobante):
        conn = sqlite3.connect('sistema_minimarket.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM comprobantes WHERE id_comprobante = ?', (id_comprobante,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Comprobante(*row)
        return None