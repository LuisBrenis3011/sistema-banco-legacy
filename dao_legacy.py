from conexion_legacy import obtener_conexion_legacy
import random

class DAOLegacy:

    @staticmethod
    def validar_usuario(dni, password):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT ID_CLIENTE FROM CLIENTES_CORE WHERE DNI_RUT = %s AND PASSWORD_HASH = %s",
                (dni, password)
            )
            resultado = cursor.fetchone()
            conexion.close()
            return resultado
        return None

    @staticmethod
    def buscar_cliente_por_dni(dni):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT ID_CLIENTE FROM CLIENTES_CORE WHERE DNI_RUT = %s", (dni,))
            resultado = cursor.fetchone()
            conexion.close()
            return resultado
        return None

    @staticmethod
    def consultar_estado_sesion(id_cliente):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT SESION_ACTIVA, METODO_ACCESO FROM ESTADO_SESIONES WHERE ID_CLIENTE = %s",
                (id_cliente,)
            )
            resultado = cursor.fetchone()
            conexion.close()
            if resultado:
                # Conversion explicita para evitar ambiguedad con MySQL
                resultado['SESION_ACTIVA'] = bool(resultado['SESION_ACTIVA'])
                return resultado
        return None
    

    @staticmethod
    def actualizar_sesion(id_cliente, estado, metodo='NINGUNO'):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE ESTADO_SESIONES SET SESION_ACTIVA = %s, METODO_ACCESO = %s WHERE ID_CLIENTE = %s",
                (estado, metodo, id_cliente)
            )
            conexion.commit()
            conexion.close()

    @staticmethod
    def obtener_cuentas(id_cliente):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT ID_CUENTA, TIPO_CUENTA, SALDO, MONEDA FROM CUENTAS WHERE ID_CLIENTE = %s",
                (id_cliente,)
            )
            resultado = cursor.fetchall()
            conexion.close()
            return resultado
        return []

    @staticmethod
    def obtener_movimientos(id_cuenta):
        conexion = obtener_conexion_legacy()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT DESCRIPCION, MONTO, TIPO, FECHA 
                   FROM MOVIMIENTOS 
                   WHERE ID_CUENTA = %s 
                   ORDER BY FECHA DESC LIMIT 5""",
                (id_cuenta,)
            )
            resultado = cursor.fetchall()
            conexion.close()
            return resultado
        return []

    @staticmethod
    def registrar_usuario(dni, password):
        conexion = obtener_conexion_legacy()
        if conexion:
            try:
                cursor = conexion.cursor()
                id_cliente = random.randint(2000, 9999)
                cursor.execute(
                    "INSERT INTO CLIENTES_CORE (ID_CLIENTE, DNI_RUT, PASSWORD_HASH) VALUES (%s, %s, %s)",
                    (id_cliente, dni, password)
                )
                cursor.execute(
                    "INSERT INTO ESTADO_SESIONES (ID_CLIENTE, SESION_ACTIVA, METODO_ACCESO) VALUES (%s, FALSE, 'NINGUNO')",
                    (id_cliente,)
                )
                conexion.commit()
                conexion.close()
                return id_cliente
            except Exception as e:
                print(f"Error al registrar: {e}")
                conexion.rollback()
                conexion.close()
                return None
        return None