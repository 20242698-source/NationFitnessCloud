import sqlite3
import os

if not os.path.exists('bd'):
    os.makedirs('bd')

DB_PATH = "bd/gimnasio.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabla de Socios
    cursor.execute('''CREATE TABLE IF NOT EXISTS socios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        clave TEXT, nombre TEXT, paterno TEXT, materno TEXT,
                        telefono TEXT, email TEXT, observaciones TEXT,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. Tabla de Registro de Membresías (Historial de pagos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS registro_membresias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_socio INTEGER,
                        tipo_membresia TEXT,
                        fecha_inicio TEXT,
                        vencimiento TEXT,
                        precio REAL,
                        horas TEXT, 
                        estado TEXT, 
                        observaciones TEXT,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(id_socio) REFERENCES socios(id))''')

    # 3. Tabla de Catálogo (Precios configurables)
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalogo_membresias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT UNIQUE,
                        costo REAL)''')

    # 4. Tabla de Egresos (Gastos del gimnasio)
    cursor.execute('''CREATE TABLE IF NOT EXISTS egresos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        concepto TEXT, 
                        monto REAL, 
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
        # 5. Tabla de Usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        clave TEXT,
                        rol TEXT DEFAULT 'recepcionista')''')
    # Insertar admin por defecto si no existe
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES ('admin', '1', 'administrador')")
    
    conn.commit()
    conn.close()

def crear_tabla_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        clave TEXT,
                        rol TEXT DEFAULT 'recepcionista')''')
    # Insertar admin por defecto si no existe
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES ('admin', '1', 'administrador')")
    conn.commit()
    conn.close()

# --- Funciones de Socios ---
def obtener_socios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, clave, nombre, paterno, materno, telefono, email, observaciones, fecha_creacion FROM socios")
    datos = cursor.fetchall()
    conn.close()
    return datos

def insertar_socio(datos):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO socios (clave, nombre, paterno, materno, telefono, email, observaciones) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', datos)
    conn.commit()
    conn.close()

def buscar_socios_filtro(termino):
    """Busca socios por nombre, apellidos o clave"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Usamos OR para que busque en cualquiera de esas columnas
    query = """
        SELECT * FROM socios 
        WHERE nombre LIKE ? 
        OR paterno LIKE ? 
        OR materno LIKE ? 
        OR clave LIKE ?
    """
    
    # El término se repite 4 veces, una para cada columna
    filtro = f"%{termino}%"
    cursor.execute(query, (filtro, filtro, filtro, filtro))
    
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

# --- Funciones de Membresías ---
def asignar_membresia(datos):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # Hay 8 signos de interrogación para los 8 datos
        cursor.execute('''INSERT INTO registro_membresias 
                          (id_socio, tipo_membresia, fecha_inicio, vencimiento, precio, horas, estado, observaciones)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', datos)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error en asignar_membresia: {e}") # Esto saldrá en tu terminal de VS Code
        return False
    finally:
        conn.close()

def obtener_historial_membresias(id_socio):
    conn = conectar()
    cursor = conn.cursor()
    # Ajustado para que coincida con las columnas de tu Treeview
    cursor.execute('''SELECT id, fecha_inicio, vencimiento, tipo_membresia, precio, estado 
                      FROM registro_membresias WHERE id_socio = ?''', (id_socio,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def eliminar_membresia(id_membresia):
    conn = conectar()
    cursor = conn.cursor()
    try:
        # El error suele estar aquí, asegúrate que diga 'registro_membresias'
        cursor.execute("DELETE FROM registro_membresias WHERE id = ?", (id_membresia,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return False
    finally:
        conn.close()

def agregar_plan_membresia(nombre, costo):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO catalogo_membresias (nombre, costo) VALUES (?, ?)", (nombre, costo))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al agregar plan: {e}")
        return False
    finally:
        conn.close()

def actualizar_plan_membresia(id_plan, nuevo_nombre, nuevo_costo):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE catalogo_membresias SET nombre = ?, costo = ? WHERE id = ?",
                       (nuevo_nombre, nuevo_costo, id_plan))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar plan: {e}")
        return False
    finally:
        conn.close()

def obtener_planes_membresia():
    conn = conectar()
    cursor = conn.cursor()
    # Asegúrate de que el nombre de la tabla sea 'catalogo_membresias' o el que uses
    cursor.execute("SELECT id, nombre, costo FROM catalogo_membresias")
    planes = cursor.fetchall()
    conn.close()
    return planes

def eliminar_plan_membresia(id_plan):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM catalogo_membresias WHERE id = ?", (id_plan,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar plan: {e}")
        return False
    finally:
        conn.close()

# --- Catálogo ---
def obtener_catalogo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, costo FROM catalogo_membresias")
    res = cursor.fetchall()
    conn.close()
    return res

# Asegúrate de llamar a esta función al iniciar el programa para crear la tabla si no existe
def crear_tabla_egresos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS egresos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       concepto TEXT, 
                       monto REAL, 
                       fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def registrar_egreso(concepto, monto):
    try:
        conn = conectar()  # <--- antes estaba sqlite3.connect("bd/gimnasio.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO egresos (concepto, monto) VALUES (?, ?)", (concepto, monto))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error en database_manager (registrar_egreso): {e}")
        return False

def obtener_egresos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, concepto, monto, fecha FROM egresos ORDER BY fecha ASC")
    datos = cursor.fetchall()
    conn.close()
    return datos

def actualizar_egreso(id_egreso, nuevo_concepto, nuevo_monto):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE egresos SET concepto = ?, monto = ? WHERE id = ?",
                       (nuevo_concepto, nuevo_monto, id_egreso))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar egreso: {e}")
        return False
    finally:
        conn.close()

def eliminar_egreso(id_egreso):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM egresos WHERE id = ?", (id_egreso,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar egreso: {e}")
        return False
    finally:
        conn.close()

def obtener_ingresos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""SELECT r.id, s.clave, s.nombre, r.tipo_membresia, r.precio, r.fecha_inicio 
                      FROM registro_membresias r 
                      JOIN socios s ON r.id_socio = s.id""")
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_ingresos_filtrados(desde=None, hasta=None):
    """Obtiene ingresos filtrados por rango de fecha (fecha_inicio)."""
    conn = conectar()
    cursor = conn.cursor()
    query = """SELECT r.id, s.clave, s.nombre, r.tipo_membresia, r.precio, r.fecha_inicio 
               FROM registro_membresias r 
               JOIN socios s ON r.id_socio = s.id"""
    params = ()
    if desde and hasta:
        query += " WHERE r.fecha_inicio BETWEEN ? AND ?"
        params = (desde, hasta)
    elif desde:
        query += " WHERE r.fecha_inicio >= ?"
        params = (desde,)
    elif hasta:
        query += " WHERE r.fecha_inicio <= ?"
        params = (hasta,)
    query += " ORDER BY r.fecha_inicio ASC"
    cursor.execute(query, params)
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_egresos_filtrados(desde=None, hasta=None):
    conn = conectar()
    cursor = conn.cursor()
    query = "SELECT id, concepto, monto, fecha FROM egresos"
    params = ()
    condiciones = []
    if desde:
        condiciones.append("date(fecha) >= ?")
        params += (desde,)
    if hasta:
        condiciones.append("date(fecha) <= ?")
        params += (hasta,)
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    query += " ORDER BY fecha ASC"
    cursor.execute(query, params)
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_total_socios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM socios")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def obtener_membresias_por_vencer(dias=7):
    """Retorna lista de (nombre_socio, tipo_membresia, vencimiento) que vencen en los próximos 'dias' días."""
    conn = conectar()
    cursor = conn.cursor()
    # Calcula la fecha límite en formato YYYY-MM-DD
    from datetime import datetime, timedelta
    limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    cursor.execute("""SELECT s.nombre, r.tipo_membresia, r.vencimiento
                      FROM registro_membresias r
                      JOIN socios s ON r.id_socio = s.id
                      WHERE r.estado = 'Activo' AND r.vencimiento <= ?
                      ORDER BY r.vencimiento ASC""", (limite,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_plan_por_nombre(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, costo FROM catalogo_membresias WHERE nombre=?", (nombre,))
    plan = cursor.fetchone()
    conn.close()
    return plan  # (id, nombre, costo) o None

def obtener_ingresos_mes_actual():
    """Suma de ingresos del mes actual."""
    from datetime import datetime
    conn = conectar()
    cursor = conn.cursor()
    inicio = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute("SELECT COALESCE(SUM(precio), 0) FROM registro_membresias WHERE fecha_inicio >= ?", (inicio,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def obtener_egresos_mes_actual():
    """Suma de egresos del mes actual."""
    from datetime import datetime
    conn = conectar()
    cursor = conn.cursor()
    inicio = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM egresos WHERE fecha >= ?", (inicio,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def obtener_ultimos_pagos(limite=5):
    """Últimos pagos registrados (membresías) con nombre del socio."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""SELECT s.nombre, r.tipo_membresia, r.precio, r.fecha_inicio
                      FROM registro_membresias r
                      JOIN socios s ON r.id_socio = s.id
                      ORDER BY r.fecha_registro DESC LIMIT ?""", (limite,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_socios_con_estado():
    """Retorna (id, clave, nombre, paterno, materno, teléfono, email, observaciones, fecha_creacion, estado, vencimiento)
    El 'estado' se calcula según la fecha de vencimiento de la membresía más reciente de cada socio.
    """
    from datetime import datetime
    conn = conectar()
    cursor = conn.cursor()
    # Obtener todos los socios
    cursor.execute("SELECT id, clave, nombre, paterno, materno, telefono, email, observaciones, fecha_creacion FROM socios ORDER BY id")
    socios = cursor.fetchall()
    resultado = []
    hoy = datetime.now().date()
    for s in socios:
        id_s = s[0]
        # Membresía más reciente (con vencimiento más cercano al futuro o más reciente en general)
        cursor.execute("""SELECT vencimiento, estado 
                          FROM registro_membresias 
                          WHERE id_socio = ? 
                          ORDER BY vencimiento DESC LIMIT 1""", (id_s,))
        row = cursor.fetchone()
        if row:
            vencimiento_str, estado_db = row
            try:
                vencimiento = datetime.strptime(vencimiento_str, "%Y-%m-%d").date()
                if vencimiento < hoy:
                    estado_calculado = "Vencida"
                elif (vencimiento - hoy).days <= 7:
                    estado_calculado = "Por vencer"
                else:
                    estado_calculado = "Vigente"
            except:
                # Si el formato de fecha no es válido, asumir estado original
                estado_calculado = estado_db if estado_db else "Sin datos"
        else:
            vencimiento_str = None
            estado_calculado = "Sin membresía"
        resultado.append((s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], estado_calculado, vencimiento_str))
    conn.close()
    return resultado

def eliminar_socio(id_socio):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM socios WHERE id = ?", (id_socio,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar socio: {e}")
        return False
    finally:
        conn.close()

def actualizar_socio(id_socio, datos):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE socios SET clave=?, nombre=?, paterno=?, materno=?, telefono=?, email=?, observaciones=?
                          WHERE id=?''', (*datos, id_socio))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar socio: {e}")
        return False
    finally:
        conn.close()

def existe_socio_duplicado(clave, nombre, paterno, materno, id_socio=None):
    conn = conectar()
    cursor = conn.cursor()
    if id_socio:  # modo edición: excluye el propio registro
        cursor.execute("SELECT id FROM socios WHERE clave=? AND nombre=? AND paterno=? AND materno=? AND id != ?",
                       (clave, nombre, paterno, materno, id_socio))
    else:
        cursor.execute("SELECT id FROM socios WHERE clave=? AND nombre=? AND paterno=? AND materno=?",
                       (clave, nombre, paterno, materno))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def existe_egreso_duplicado(concepto, monto, id_egreso=None):
    conn = conectar()
    cursor = conn.cursor()
    if id_egreso:
        cursor.execute("SELECT id FROM egresos WHERE concepto=? AND monto=? AND id != ?",
                       (concepto, monto, id_egreso))
    else:
        cursor.execute("SELECT id FROM egresos WHERE concepto=? AND monto=?",
                       (concepto, monto))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def validar_usuario(usuario, clave):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT rol FROM usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, rol FROM usuarios")
    datos = cursor.fetchall()
    conn.close()
    return datos

def agregar_usuario(usuario, clave, rol):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?)", (usuario, clave, rol))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def eliminar_usuario(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conn.commit()
    conn.close()

crear_tablas()