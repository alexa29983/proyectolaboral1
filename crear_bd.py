import sqlite3

# Conectar a la base de datos (se creará el archivo si no existe)
conexion = sqlite3.connect('laboral.db')
cursor = conexion.cursor()

# Leer el archivo SQL del maestro
with open('laboral.sql', 'r', encoding='utf-8') as archivo_sql:
    sql_script = archivo_sql.read()

# Executar los comandos para crear las tablas
try:
    cursor.executescript(sql_script)
    conexion.commit()
    print("¡Base de datos y tablas creadas con éxito!")
except sqlite3.OperationalError as e:
    print(f"Hubo un detalle al crear las tablas: {e}")
finally:
    conexion.close()