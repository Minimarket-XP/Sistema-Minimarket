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

def _cargar_env():
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

def consulta_dni_api(numero):
    try:
        import json
        from urllib import request
        env = _cargar_env()
        url = env.get("DNI_API_URL", "").strip()
        key = env.get("DNI_API_KEY", "").strip()
        if not url or not key:
            return None
        payload = json.dumps({"dni": str(numero)}).encode("utf-8")
        req = request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {key}")
        with request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception:
        return None

def consulta_ruc_api(numero):
    try:
        import json
        from urllib import request
        env = _cargar_env()
        url = env.get("RUC_API_URL", "").strip()
        key = env.get("DNI_API_KEY", "").strip()
        if not url or not key:
            return None
        payload = json.dumps({"ruc": str(numero)}).encode("utf-8")
        req = request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {key}")
        with request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception:
        return None
