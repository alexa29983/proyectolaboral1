import sqlite3
from flask import Flask, redirect, render_template, request, url_for, session
from functools import wraps


app = Flask(__name__)


# CLAVE SECRETA PARA SESIONES
app.secret_key = "clave_secreta_para_ecoruta_2026"




# ========================================================
# CONEXIÓN A BASE DE DATOS
# ========================================================


def conectar_bd():


    conexion = sqlite3.connect(
        "laboral.db",
        timeout=30,
        check_same_thread=False
    )


    conexion.row_factory = sqlite3.Row


    return conexion




# ========================================================
# DECORADOR DE ROLES
# ========================================================


def requerir_roles(*roles_permitidos):


    def decorador(funcion):


        @wraps(funcion)
        def funcion_decorada(*args, **kwargs):


            # SI NO HAY SESIÓN
            if "usuario" not in session:


                return redirect(url_for("usuario"))


            rol_usuario = str(
                session.get("rol", "")
            ).strip().lower()


            roles_validos = [
                rol.strip().lower()
                for rol in roles_permitidos
            ]


            # VALIDAR ROL
            if rol_usuario not in roles_validos:


                return """
                    <h1>Acceso Denegado</h1>


                    <p>
                        Tu rol no tiene permisos
                        para acceder a esta sección.
                    </p>


                    <a href='/index'>
                        Volver al Inicio
                    </a>
                """, 403


            return funcion(*args, **kwargs)


        return funcion_decorada


    return decorador




# ========================================================
# LOGIN
# ========================================================


@app.route("/", methods=["GET", "POST"])
@app.route("/usuario", methods=["GET", "POST"])
def usuario():


    if request.method == "POST":


        nombre = request.form.get("nombre")
        contrasena = request.form.get("contrasena")


        conexion = conectar_bd()
        cursor = conexion.cursor()


        cursor.execute("""
            SELECT *
            FROM usuario
            WHERE nombre = ?
            AND contrasena = ?
        """, (
            nombre,
            contrasena
        ))


        usuario_encontrado = cursor.fetchone()


        conexion.close()


        # LOGIN CORRECTO
        if usuario_encontrado:


            session["usuario"] = usuario_encontrado["nombre"]


            session["rol"] = str(
                usuario_encontrado["rol"]
            ).strip().lower()


            return redirect(url_for("inicio"))


        # LOGIN INCORRECTO
        else:


            return """
                <h1>Credenciales incorrectas</h1>


                <a href='/usuario'>
                    Intentar nuevamente
                </a>
            """


    return render_template("usuarios.html")




# ========================================================
# LOGOUT
# ========================================================


@app.route("/logout")
def logout():


    session.clear()


    return redirect(url_for("usuario"))




# ========================================================
# REGISTRO DE USUARIOS
# ========================================================


@app.route("/registro", methods=["GET", "POST"])
def registro():


    conexion = conectar_bd()
    cursor = conexion.cursor()


    if request.method == "POST":


        nombre = request.form.get("nombre")
        contrasena = request.form.get("contrasena")


        rol = str(
            request.form.get("rol")
        ).strip().lower()


        cursor.execute("""
            INSERT INTO usuario (
                nombre,
                contrasena,
                rol
            )
            VALUES (?, ?, ?)
        """, (
            nombre,
            contrasena,
            rol
        ))


        conexion.commit()


        conexion.close()


        return redirect(url_for("usuario"))


    conexion.close()


    return render_template("registro.html")




# ========================================================
# INDEX
# ========================================================


@app.route("/index")
def inicio():


    if "usuario" not in session:


        return redirect(url_for("usuario"))


    return render_template("index.html")




# ========================================================
# CRUD RUTAS
# TODOS PUEDEN VER
# SOLO ADMINISTRADOR MODIFICA
# ========================================================


@app.route("/ruta", methods=["GET", "POST"])
@requerir_roles(
    "administrador",
    "supervisor",
    "operador",
    "ciudadano"
)
def ruta():


    conexion = conectar_bd()
    cursor = conexion.cursor()


    # POST
    if request.method == "POST":


        if session.get("rol") != "administrador":


            conexion.close()


            return "No tienes permisos", 403


        id_ruta = request.form.get("id_ruta")


        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")


        # EDITAR
        if id_ruta:


            cursor.execute("""
                UPDATE ruta
                SET nombre = ?,
                    direccion = ?
                WHERE id_ruta = ?
            """, (
                nombre,
                direccion,
                id_ruta
            ))


        # INSERTAR
        else:


            cursor.execute("""
                INSERT INTO ruta (
                    nombre,
                    direccion
                )
                VALUES (?, ?)
            """, (
                nombre,
                direccion
            ))


        conexion.commit()


        conexion.close()


        return redirect(url_for("ruta"))


    # GET
    id_editar = request.args.get("editar")


    ruta_editando = None


    if (
        id_editar
        and session.get("rol") == "administrador"
    ):


        cursor.execute("""
            SELECT *
            FROM ruta
            WHERE id_ruta = ?
        """, (id_editar,))


        ruta_editando = cursor.fetchone()


    cursor.execute("""
        SELECT *
        FROM ruta
    """)


    rutas = cursor.fetchall()


    conexion.close()


    return render_template(
        "ruta.html",
        rutas=rutas,
        ruta_editando=ruta_editando
    )




# ELIMINAR RUTA
@app.route("/eliminar_ruta/<id_ruta>")
@requerir_roles("administrador")
def eliminar_ruta(id_ruta):


    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
        DELETE FROM ruta
        WHERE id_ruta = ?
    """, (id_ruta,))


    conexion.commit()


    conexion.close()


    return redirect(url_for("ruta"))




# ========================================================
# CRUD UNIDAD
# ADMINISTRADOR, SUPERVISOR Y OPERADOR VEN
# SOLO ADMINISTRADOR MODIFICA
# ========================================================


@app.route("/unidad", methods=["GET", "POST"])
@requerir_roles(
    "administrador",
    "supervisor",
    "operador"
)
def unidad():


    conexion = conectar_bd()
    cursor = conexion.cursor()


    # POST
    if request.method == "POST":


        if session.get("rol") != "administrador":


            conexion.close()


            return "No tienes permisos", 403


        placa = request.form.get("placa")


        id_unidad = request.form.get("id_unidad")


        # EDITAR
        if id_unidad:


            cursor.execute("""
                UPDATE unidad
                SET placa = ?
                WHERE id_unidad = ?
            """, (
                placa,
                id_unidad
            ))


        # INSERTAR
        else:


            cursor.execute("""
                INSERT INTO unidad (
                    placa
                )
                VALUES (?)
            """, (placa,))


        conexion.commit()


        conexion.close()


        return redirect(url_for("unidad"))


    # GET
    id_editar = request.args.get("editar")


    unidad_editando = None


    if (
        id_editar
        and session.get("rol") == "administrador"
    ):


        cursor.execute("""
            SELECT *
            FROM unidad
            WHERE id_unidad = ?
        """, (id_editar,))


        unidad_editando = cursor.fetchone()


    cursor.execute("""
        SELECT *
        FROM unidad
    """)


    unidades = cursor.fetchall()


    conexion.close()


    return render_template(
        "unidad.html",
        unidades=unidades,
        unidad_editando=unidad_editando
    )




# ELIMINAR UNIDAD
@app.route("/eliminar_unidad/<id_unidad>")
@requerir_roles("administrador")
def eliminar_unidad(id_unidad):


    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
        DELETE FROM unidad
        WHERE id_unidad = ?
    """, (id_unidad,))


    conexion.commit()


    conexion.close()


    return redirect(url_for("unidad"))




# ========================================================
# CRUD HORARIO
# TODOS PUEDEN VER
# SOLO ADMINISTRADOR MODIFICA
# ========================================================


@app.route("/horario", methods=["GET", "POST"])
@requerir_roles(
    "administrador",
    "supervisor",
    "operador",
    "ciudadano"
)
def horario():


    conexion = conectar_bd()
    cursor = conexion.cursor()


    # POST
    if request.method == "POST":


        if session.get("rol") != "administrador":


            conexion.close()


            return "No tienes permisos", 403


        id_horario = request.form.get("id_horario")


        hora_inicio = request.form.get("hora_inicio")
        hora_termino = request.form.get("hora_termino")


        id_ruta = request.form.get("id_ruta")
        id_unidad = request.form.get("id_unidad")


        # EDITAR
        if id_horario:


            cursor.execute("""
                UPDATE horario
                SET hora_inicio = ?,
                    hora_termino = ?,
                    id_ruta = ?,
                    id_unidad = ?
                WHERE id_horario = ?
            """, (
                hora_inicio,
                hora_termino,
                id_ruta,
                id_unidad,
                id_horario
            ))


        # INSERTAR
        else:


            cursor.execute("""
                INSERT INTO horario (
                    hora_inicio,
                    hora_termino,
                    id_ruta,
                    id_unidad
                )
                VALUES (?, ?, ?, ?)
            """, (
                hora_inicio,
                hora_termino,
                id_ruta,
                id_unidad
            ))


        conexion.commit()


        conexion.close()


        return redirect(url_for("horario"))


    # GET
    id_editar = request.args.get("editar")


    horario_editando = None


    if (
        id_editar
        and session.get("rol") == "administrador"
    ):


        cursor.execute("""
            SELECT *
            FROM horario
            WHERE id_horario = ?
        """, (id_editar,))


        horario_editando = cursor.fetchone()


    cursor.execute("""
        SELECT *
        FROM horario
    """)


    horarios = cursor.fetchall()


    conexion.close()


    return render_template(
        "horario.html",
        horarios=horarios,
        horario_editando=horario_editando
    )




# ELIMINAR HORARIO
@app.route("/eliminar_horario/<id_horario>")
@requerir_roles("administrador")
def eliminar_horario(id_horario):


    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
        DELETE FROM horario
        WHERE id_horario = ?
    """, (id_horario,))


    conexion.commit()


    conexion.close()


    return redirect(url_for("horario"))




# ========================================================
# CRUD OPERADOR
# ADMINISTRADOR Y SUPERVISOR VEN
# SOLO ADMINISTRADOR MODIFICA
# ========================================================


@app.route("/operador", methods=["GET", "POST"])
@requerir_roles(
    "administrador",
    "supervisor"
)
def operador():


    conexion = conectar_bd()
    cursor = conexion.cursor()


    # POST
    if request.method == "POST":


        if session.get("rol") != "administrador":


            conexion.close()


            return "No tienes permisos", 403


        id_operador = request.form.get("id_operador")


        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")


        id_unidad = request.form.get("id_unidad")


        # EDITAR
        if id_operador:


            cursor.execute("""
                UPDATE operador
                SET nombre = ?,
                    telefono = ?,
                    id_unidad = ?
                WHERE id_operador = ?
            """, (
                nombre,
                telefono,
                id_unidad,
                id_operador
            ))


        # INSERTAR
        else:


            cursor.execute("""
                INSERT INTO operador (
                    nombre,
                    telefono,
                    id_unidad
                )
                VALUES (?, ?, ?)
            """, (
                nombre,
                telefono,
                id_unidad
            ))


        conexion.commit()


        conexion.close()


        return redirect(url_for("operador"))


    # GET
    id_editar = request.args.get("editar")


    operador_editando = None


    if (
        id_editar
        and session.get("rol") == "administrador"
    ):


        cursor.execute("""
            SELECT *
            FROM operador
            WHERE id_operador = ?
        """, (id_editar,))


        operador_editando = cursor.fetchone()


    cursor.execute("""
        SELECT *
        FROM operador
    """)


    operadores = cursor.fetchall()


    conexion.close()


    return render_template(
        "operador.html",
        operadores=operadores,
        operador_editando=operador_editando
    )




# ELIMINAR OPERADOR
@app.route("/eliminar_operador/<id_operador>")
@requerir_roles("administrador")
def eliminar_operador(id_operador):


    conexion = conectar_bd()
    cursor = conexion.cursor()


    cursor.execute("""
        DELETE FROM operador
        WHERE id_operador = ?
    """, (id_operador,))


    conexion.commit()


    conexion.close()


    return redirect(url_for("operador"))




# ========================================================
# EJECUTAR APP
# ========================================================


if __name__ == "__main__":


    app.run(
        debug=True,
        use_reloader=True
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)