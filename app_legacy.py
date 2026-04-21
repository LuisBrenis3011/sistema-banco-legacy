import customtkinter as ctk
import requests
import uuid
from dao_legacy import DAOLegacy
import tkinter.messagebox as messagebox

class DispositivoRAM:
    def __init__(self):
        self.token_hardware = str(uuid.uuid4())[:8]
        self.dni_vinculado = None
        self.id_cliente_vinculado = None # Nuevo: Guardamos el ID interno

memoria_local = DispositivoRAM()

class BancoLegacyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Legacy Bank - Localhost:8080 | Device: {memoria_local.token_hardware}")
        self.geometry("400x550")
        self.evaluar_estado_dispositivo()

    def limpiar_pantalla(self):
        for widget in self.winfo_children(): widget.destroy()

    def evaluar_estado_dispositivo(self):
        self.limpiar_pantalla()
        if memoria_local.dni_vinculado:
            self.mostrar_login_rapido()
        else:
            self.mostrar_login_completo()

    # --- VISTA 1: EL DISPOSITIVO ES NUEVO ---
    def mostrar_login_completo(self):
        ctk.CTkLabel(self, text="🏛️ SISTEMA CORE BANCO", font=("Arial", 22, "bold")).pack(pady=30)
        self.entry_dni = ctk.CTkEntry(self, placeholder_text="DNI / RUT", width=250)
        self.entry_dni.pack(pady=10)
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=250)
        self.entry_pass.pack(pady=10)
        
        # Botón de Login Normal
        ctk.CTkButton(self, text="Validar y Vincular (Login)", command=self.ejecutar_login_real).pack(pady=(20, 10))
        # Botón Nuevo para Registrar
        ctk.CTkButton(self, text="Crear Cuenta Nueva", fg_color="gray", hover_color="darkgray", command=self.ejecutar_registro_real).pack(pady=5)

    def ejecutar_login_real(self):
        dni = self.entry_dni.get()
        password = self.entry_pass.get()
        
        resultado = DAOLegacy.validar_usuario(dni, password)
        
        if resultado:
            memoria_local.dni_vinculado = dni
            memoria_local.id_cliente_vinculado = resultado['ID_CLIENTE']
            messagebox.showinfo("Éxito", "Dispositivo vinculado correctamente.")
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Error", "Credenciales inválidas en el Sistema Core.")

    def ejecutar_registro_real(self):
        dni = self.entry_dni.get()
        password = self.entry_pass.get()
        
        if not dni or not password:
            messagebox.showwarning("Atención", "Debes ingresar DNI y Contraseña para registrarte.")
            return
            
        exito = DAOLegacy.registrar_usuario(dni, password)
        
        if exito:
            messagebox.showinfo("Éxito", "¡Usuario creado en el Banco Legacy!\nAhora dale a 'Validar y Vincular' para entrar.")
        else:
            messagebox.showerror("Error", "No se pudo registrar. Quizás el DNI ya existe.")

    def mostrar_login_rapido(self):
        ctk.CTkLabel(self, text=f"Bienvenido, {memoria_local.dni_vinculado}", font=("Arial", 18)).pack(pady=20)
        self.entry_pass_rapido = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=250)
        self.entry_pass_rapido.pack(pady=10)
        
        ctk.CTkButton(self, text="Entrar", command=self.mostrar_dashboard).pack(pady=10)
        # BOTÓN QUE CONECTARÁ CON EL MICROSERVICIO
        ctk.CTkButton(self, text="  Acceso Biométrico", fg_color="#27ae60", command=self.peticion_biometrica).pack(pady=10)

    def peticion_biometrica(self):
        # 1. Preparamos el sobre con la información (El JSON)
        url_microservicio = "http://127.0.0.1:5000/api/biometria"
        datos_a_enviar = {
            "id_cliente": memoria_local.id_cliente_vinculado
        }
        
        try:
            # 2. Enviamos el paquete por la red interna (Localhost)
            print("Enviando petición a la cámara...")
            respuesta = requests.post(url_microservicio, json=datos_a_enviar)
            
            # 3. Leemos lo que nos respondió el Microservicio
            datos_respuesta = respuesta.json()
            
            if datos_respuesta.get("acceso_concedido") == True:
                messagebox.showinfo("Biometría", datos_respuesta.get("mensaje"))
                self.mostrar_dashboard()
            else:
                messagebox.showerror("Error", "Rostro no coincide.")
                
        except requests.exceptions.ConnectionError:
            # Si el archivo servidor_api.py está apagado, salta este error
            messagebox.showerror("Error Crítico", "El Servidor Biométrico está apagado o no responde en el puerto 5000.")
    

    def mostrar_dashboard(self):
        self.limpiar_pantalla()
        ctk.CTkLabel(self, text="PANEL DE CONTROL LEGACY", font=("Arial", 20, "bold")).pack(pady=40)
        ctk.CTkLabel(self, text=f"ID Cliente: {memoria_local.id_cliente_vinculado}").pack()
        ctk.CTkButton(self, text="Cerrar Sesión", command=self.evaluar_estado_dispositivo).pack(pady=30)

if __name__ == "__main__":
    app = BancoLegacyApp()
    app.mainloop()