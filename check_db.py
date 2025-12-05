from core.database import db

conn = db.get_connection()
cursor = conn.cursor()

print("=== EMPLEADOS ===")
cursor.execute("SELECT id_empleado, nombre_empleado, apellido_empleado FROM empleado")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Nombre: {row[1]} {row[2]}")

print("\n=== USUARIOS ===")
cursor.execute("SELECT id_usuario, username, id_empleado FROM usuario")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}, EmpleadoID: {row[2]}")

print("\n=== ROLES ===")
cursor.execute("SELECT id_rol, nombre_rol FROM rol")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Rol: {row[1]}")

print("\n=== PRODUCTOS ===")
cursor.execute("SELECT id_producto, nombre_producto, precio_producto FROM productos")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Producto: {row[1]}, Precio: {row[2]}")

conn.close()
