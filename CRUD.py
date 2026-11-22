import conexion

# -------------------------------------------------
# FUNCIONES GENERALES
# -------------------------------------------------

def consultar(sql, datos=()):
    conn = None
    cursor = None
    try:
        conn = conexion.conectar()
        cursor = conn.cursor()
        cursor.execute(sql, datos)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def ejecutar(sql, datos=()):
    conn = None
    cursor = None
    try:
        conn = conexion.conectar()
        cursor = conn.cursor()
        cursor.execute(sql, datos)
        conn.commit()
        return True
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------------------------------------------------
# COMPUTADORAS
# -------------------------------------------------

def obtener_computadoras():
    return consultar("SELECT id_computadora, nombre, fecha_armado FROM computadoras ORDER BY id_computadora")


def obtener_computadora(id_pc):
    return consultar("SELECT nombre, fecha_armado FROM computadoras WHERE id_computadora = %s", (id_pc,))


def crear_computadora(nombre, fecha):
    conn = None
    cursor = None
    try:
        conn = conexion.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO computadoras (nombre, fecha_armado) VALUES (%s, %s)", (nombre, fecha))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def eliminar_computadora(id_pc):
    ejecutar("DELETE FROM computadoras WHERE id_computadora = %s", (id_pc,))
    return True


def obtener_estado_piezas_pc(id_pc):
    componentes = consultar("SELECT categoria, estado FROM componentes WHERE id_computadora = %s", (id_pc,))
    perifericos = consultar("SELECT nombre, estado FROM perifericos WHERE id_computadora = %s", (id_pc,))
    return componentes, perifericos


def obtener_componentes_pc(id_pc):
    return consultar("SELECT id_componente, categoria, marca, nombre_tecnico, estado FROM componentes WHERE id_computadora = %s ORDER BY categoria, id_componente", (id_pc,))


def obtener_perifericos_pc(id_pc):
    return consultar("SELECT id_periferico, nombre, marca, estado FROM perifericos WHERE id_computadora = %s ORDER BY nombre, id_periferico", (id_pc,))


def contar_componentes_categoria(id_pc, categoria):
    return consultar("SELECT COUNT(*) FROM componentes WHERE id_computadora = %s AND categoria = %s", (id_pc, categoria))[0][0]


def contar_perifericos_tipo(id_pc, nombre):
    return consultar("SELECT COUNT(*) FROM perifericos WHERE id_computadora = %s AND nombre = %s", (id_pc, nombre))[0][0]


def obtener_componentes_disponibles(categoria):
    return consultar("SELECT id_componente, categoria, marca, nombre_tecnico, estado FROM componentes WHERE id_computadora IS NULL AND categoria = %s ORDER BY id_componente", (categoria,))


def obtener_perifericos_disponibles(nombre):
    return consultar("SELECT id_periferico, nombre, marca, estado FROM perifericos WHERE id_computadora IS NULL AND nombre = %s ORDER BY id_periferico", (nombre,))


def asignar_componente(id_pc, id_componente):
    ejecutar("UPDATE componentes SET id_computadora = %s, ubicacion_caja = NULL WHERE id_componente = %s AND id_computadora IS NULL", (id_pc, id_componente))
    return True


def asignar_periferico(id_pc, id_periferico):
    ejecutar("UPDATE perifericos SET id_computadora = %s, ubicacion_caja = NULL WHERE id_periferico = %s AND id_computadora IS NULL", (id_pc, id_periferico))
    return True


def devolver_componente_a_caja(id_componente):
    ejecutar("UPDATE componentes SET id_computadora = NULL WHERE id_componente = %s", (id_componente,))
    return True


def devolver_periferico_a_caja(id_periferico):
    ejecutar("UPDATE perifericos SET id_computadora = NULL WHERE id_periferico = %s", (id_periferico,))
    return True


# -------------------------------------------------
# LISTADOS GENERALES DE INVENTARIO
# -------------------------------------------------

def obtener_inventario_componentes():
    return consultar("""SELECT c.id_componente, IF(c.id_computadora IS NULL, 'En caja', pc.nombre),
        c.categoria, c.marca, c.nombre_tecnico, c.estado FROM componentes c
        LEFT JOIN computadoras pc ON pc.id_computadora = c.id_computadora
        ORDER BY c.id_computadora, c.categoria, c.id_componente""")


def obtener_inventario_perifericos():
    return consultar("""SELECT p.id_periferico, IF(p.id_computadora IS NULL, 'En caja', pc.nombre),
        p.nombre, p.marca, p.estado FROM perifericos p
        LEFT JOIN computadoras pc ON pc.id_computadora = p.id_computadora
        ORDER BY p.id_computadora, p.nombre, p.id_periferico""")


# -------------------------------------------------
# CRUD DE COMPONENTES
# -------------------------------------------------

def obtener_componentes_filtrados(ubicacion, categoria="Todas", estado="Todos"):
    sql = """SELECT c.id_componente,
                    IF(c.id_computadora IS NULL, 'En caja', pc.nombre),
                    c.categoria, c.marca, c.nombre_tecnico, c.estado
             FROM componentes c
             LEFT JOIN computadoras pc ON pc.id_computadora = c.id_computadora
             WHERE """
    condiciones = []
    datos = []

    if ubicacion == "En caja":
        condiciones.append("c.id_computadora IS NULL")
    else:
        condiciones.append("c.id_computadora IS NOT NULL")

    if categoria != "Todas":
        condiciones.append("c.categoria = %s")
        datos.append(categoria)

    if estado != "Todos":
        condiciones.append("c.estado = %s")
        datos.append(estado)

    sql += " AND ".join(condiciones)
    sql += " ORDER BY c.categoria, c.id_componente"
    return consultar(sql, tuple(datos))


def crear_componente(categoria, marca, nombre_tecnico, estado, ubicacion_caja):
    ejecutar(
        """INSERT INTO componentes
           (id_computadora, categoria, marca, nombre_tecnico, estado, ubicacion_caja)
           VALUES (NULL, %s, %s, %s, %s, %s)""",
        (categoria, marca, nombre_tecnico, estado, ubicacion_caja)
    )
    return True


def obtener_componente(id_componente):
    return consultar(
        """SELECT categoria, marca, nombre_tecnico, estado, ubicacion_caja
           FROM componentes WHERE id_componente = %s""",
        (id_componente,)
    )


def modificar_componente(id_componente, categoria, marca, nombre_tecnico, estado, ubicacion_caja):
    ejecutar(
        """UPDATE componentes
           SET categoria = %s, marca = %s, nombre_tecnico = %s,
               estado = %s, ubicacion_caja = %s
           WHERE id_componente = %s AND id_computadora IS NULL""",
        (categoria, marca, nombre_tecnico, estado, ubicacion_caja, id_componente)
    )
    return True


def eliminar_componente(id_componente):
    ejecutar("DELETE FROM componentes WHERE id_componente = %s AND id_computadora IS NULL", (id_componente,))
    return True
