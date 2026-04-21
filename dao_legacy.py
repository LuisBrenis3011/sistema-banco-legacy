from conexion_legacy import obtener_conexion_legacy
import random

class DAOLegacy:
    @staticmethod
    def validar_usuario(dni, password):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Buscamos el ID_CLIENTE si el DNI y Pass coinciden
            query = "SELECT ID_CLIENTE FROM CLIENTES_CORE WHERE DNI_RUT = %s AND PASSWORD_HASH = %s"
            cursor.execute(query, (dni, password))
            resultado = cursor.fetchone()
            conexion.close()
            return resultado # Retorna {'ID_CLIENTE': 1001} o None
        return None

    @staticmethod
    def registrar_usuario(dni, password):
        conexion = obtener_conexion_legacy()
        if conexion:
            try:
                cursor = conexion.cursor()
                # 1. Generamos un ID interno al azar para el nuevo cliente (ej. 5034)
                id_cliente = random.randint(2000, 9999)
                
                # 2. Insertamos en la tabla principal
                query_core = "INSERT INTO CLIENTES_CORE (ID_CLIENTE, DNI_RUT, PASSWORD_HASH) VALUES (%s, %s, %s)"
                cursor.execute(query_core, (id_cliente, dni, password))
                
                # 3. Insertamos en la tabla de sesiones
                query_sesion = "INSERT INTO ESTADO_SESIONES (ID_CLIENTE, SESION_ACTIVA) VALUES (%s, FALSE)"
                cursor.execute(query_sesion, (id_cliente,))
                
                # Guardamos los cambios
                conexion.commit()
                conexion.close()
                return True
            except Exception as e:
                print(f"Error al registrar en BD: {e}")
                conexion.rollback() # Si falla, deshacemos los cambios
                conexion.close()
                return False
        return False