from DB.conexion import get_connection

def debug_db():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 1. Ver usuarios y sus roles
            print("\n=== USUARIOS ===")
            cursor.execute("""
                SELECT u.id, u.nombre, u.email, r.nombre as rol_nombre 
                FROM usuarios u 
                LEFT JOIN roles r ON u.rol_id = r.id
            """)
            usuarios = cursor.fetchall()
            for u in usuarios:
                print(f"ID: {u['id']}, Nombre: {u['nombre']}, Rol: {u['rol_nombre']}")

            # 2. Ver grupos y sus admins
            print("\n=== GRUPOS ===")
            cursor.execute("""
                SELECT g.id, g.nombre, g.admin_id, u.nombre as admin_nombre
                FROM grupos g
                LEFT JOIN usuarios u ON g.admin_id = u.id
            """)
            grupos = cursor.fetchall()
            for g in grupos:
                print(f"ID: {g['id']}, Nombre: {g['nombre']}, Admin ID: {g['admin_id']} ({g['admin_nombre']})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    debug_db()
