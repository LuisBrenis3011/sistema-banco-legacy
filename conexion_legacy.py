import mysql.connector
from mysql.connector import Error

def obtener_conexion_legacy():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root', 
            password='luismb', 
            database='db_banco_legacy'
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos legacy: {e}")
        return None