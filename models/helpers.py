## Funciones auxiliares y utilidades del sistema - PyQt5 Version OPTIMIZADO

contador_id = 0

def generar_id(prefijo): # → Genera un ID único con prefijo
    global contador_id
    contador_id += 1
    return f"{prefijo}{contador_id:04d}"

def cargar_categorias(): # → Cargar desde la BD o devuelve por defecto
    try:
        from db.database import db
        query = "SELECT nombre FROM categorias ORDER BY nombre"
        result = db.execute_query(query)
        categorias = [row[0] for row in result]
        return categorias if categorias else get_categorias_default()
    except Exception as e:
        print(f"Error cargando categorías: {e}")
        return get_categorias_default()

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
