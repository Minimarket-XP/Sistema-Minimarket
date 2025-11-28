## Funciones auxiliares y utilidades del sistema - PyQt5 Version OPTIMIZADO

contador_id = 0

def generar_id(prefijo): # → Genera un ID único con prefijo
    global contador_id
    contador_id += 1
    return f"{prefijo}{contador_id:04d}"

def cargar_categorias(): # → Cargar desde la BD o devuelve por defecto
    try:
        from core.database import db
        query = "SELECT nombre_categoria FROM categoria_productos ORDER BY nombre_categoria"
        result = db.execute_query(query)
        categorias = [row[0] for row in result]
        return categorias if categorias else get_categorias_default()
    except Exception as e:
        print(f"Error cargando categorías: {e}")
        return get_categorias_default()

def cargar_tipos_productos(): # → Cargar tipos de productos desde la BD
    try:
        from core.database import db
        query = "SELECT nombre_tipo FROM tipo_productos ORDER BY nombre_tipo"
        result = db.execute_query(query)
        tipos = [row[0] for row in result]
        return tipos if tipos else ["Arroz", "Azúcar", "Aceite", "Leche", "Otros"]
    except Exception as e:
        print(f"Error cargando tipos de productos: {e}")
        return ["Arroz", "Azúcar", "Aceite", "Leche", "Otros"]

def cargar_unidades_medida(): # → Cargar unidades de medida desde la BD
    try:
        from core.database import db
        query = "SELECT nombre_unidad FROM unidad_medida ORDER BY nombre_unidad"
        result = db.execute_query(query)
        unidades = [row[0] for row in result]
        return unidades if unidades else ["Kilogramo", "Gramo", "Litro", "Unidad"]
    except Exception as e:
        print(f"Error cargando unidades de medida: {e}")
        return ["Kilogramo", "Gramo", "Litro", "Unidad"]

def cargar_tipos_corte(): # → Retorna los tipos de corte
    return ["", "Entero", "Bistec", "Molida", "Churrasco", "Costilla", 
            "Filete", "Pechuga", "Pierna", "Alitas", "Trozos", "Otros"]

def get_categorias_default(): # → Retorna las categorias por defecto
    return ["Abarrotes", "Bebidas", "Lácteos", "Carnes", "Frutas y Verduras", "Limpieza", "Panadería"]

def formatear_precio(precio): # → Formatea un precio con el simbolo de la moneda
    try:
        return f"S/. {float(precio):.2f}"
    except:
        return "S/. 0.00"

def validar_numero(valor, tipo="float"): # → Valida y convierte el valor a número
    try:
        return (int(valor), True) \
            if tipo == "int" \
            else (float(valor), True)
    except:
        return 0, False

def validar_dni(numero): # → Valida formato de DNI peruano (8 dígitos)
    """
    Valida que el DNI tenga exactamente 8 dígitos numéricos
    Retorna: (True/False, mensaje)
    """
    numero = str(numero).strip()
    if not numero:
        return False, "DNI no puede estar vacío"
    if not numero.isdigit():
        return False, "DNI debe contener solo números"
    if len(numero) != 8:
        return False, "DNI debe tener exactamente 8 dígitos"
    return True, "DNI válido"

def validar_ruc(numero): # → Valida formato de RUC peruano (11 dígitos)
    """
    Valida que el RUC tenga exactamente 11 dígitos numéricos
    y comience con 10, 15, 16, 17 o 20
    Retorna: (True/False, mensaje)
    """
    numero = str(numero).strip()
    if not numero:
        return False, "RUC no puede estar vacío"
    if not numero.isdigit():
        return False, "RUC debe contener solo números"
    if len(numero) != 11:
        return False, "RUC debe tener exactamente 11 dígitos"
    if not numero.startswith(('10', '15', '16', '17', '20')):
        return False, "RUC debe comenzar con 10, 15, 16, 17 o 20"
    return True, "RUC válido"

def formatear_documento(tipo, numero): # → Formatea DNI/RUC para mostrar
    """
    Formatea un número de documento para visualización
    DNI: 12345678 → 12345678
    RUC: 20123456789 → 20-12345678-9
    """
    numero = str(numero).strip()
    if tipo == 'DNI':
        return numero
    elif tipo == 'RUC' and len(numero) == 11:
        return f"{numero[:2]}-{numero[2:10]}-{numero[10]}"
    return numero
