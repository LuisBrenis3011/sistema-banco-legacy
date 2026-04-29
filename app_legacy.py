import customtkinter as ctk
import tkinter.messagebox as messagebox
from dao_legacy import DAOLegacy

INTERVALO_POLLING_MS = 2000

class BancoLegacyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Core Banco Legacy - Puerto 8080")
        self.geometry("500x620")
        self.resizable(False, False)
        self.id_cliente_actual = None
        self.dni_actual = None
        self.polling_activo = False
        self.metodo_acceso = None
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar_app)
        self.mostrar_pantalla_dni()
        
    
    def al_cerrar_app(self):
        if self.id_cliente_actual:
            DAOLegacy.actualizar_sesion(self.id_cliente_actual, False, 'NINGUNO')
        self.destroy()
    

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_pantalla_dni(self):
        self.polling_activo = False
        self.id_cliente_actual = None
        self.dni_actual = None
        self.metodo_acceso = None
        self.limpiar_pantalla()

        ctk.CTkLabel(self, text="SISTEMA CORE BANCO LEGACY", font=("Arial", 20, "bold")).pack(pady=30)
        ctk.CTkLabel(self, text="Ingrese su DNI para continuar", font=("Arial", 12)).pack()

        self.entry_dni = ctk.CTkEntry(self, placeholder_text="DNI / RUT", width=300)
        self.entry_dni.pack(pady=12)

        ctk.CTkButton(self, text="Continuar", width=300, command=self.buscar_cliente).pack(pady=6)
        ctk.CTkButton(
            self, text="Crear cuenta nueva", width=300,
            fg_color="gray", hover_color="darkgray",
            command=self.mostrar_registro
        ).pack(pady=6)

    def buscar_cliente(self):
        dni = self.entry_dni.get().strip()
        if not dni:
            messagebox.showwarning("Atencion", "Ingrese su DNI.")
            return

        resultado = DAOLegacy.buscar_cliente_por_dni(dni)
        if not resultado:
            messagebox.showerror("Error", "DNI no encontrado en el sistema.")
            return

        self.id_cliente_actual = resultado['ID_CLIENTE']
        self.dni_actual = dni
        self.mostrar_pantalla_login()

    def mostrar_pantalla_login(self):
        self.limpiar_pantalla()
        
        ctk.CTkLabel(self, text="SISTEMA CORE BANCO LEGACY", font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text=f"Cliente: {self.dni_actual}", font=("Arial", 14)).pack()

        ctk.CTkLabel(self, text="Ingrese su contrasena:", font=("Arial", 11)).pack(pady=(20, 4))
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contrasena", show="*", width=300)
        self.entry_pass.pack(pady=4)
        ctk.CTkButton(self, text="Entrar", width=300, command=self.login_tradicional).pack(pady=10)

        ctk.CTkLabel(
            self,
            text="Si usa el Kiosco Biometrico (ventana separada),\nel acceso se concedera automaticamente aqui.",
            font=("Arial", 10), text_color="gray"
        ).pack(pady=(15, 4))

        self.label_polling = ctk.CTkLabel(
            self, text="Escuchando acceso biometrico...",
            font=("Arial", 10), text_color="#888888"
        )
        self.label_polling.pack()

        ctk.CTkButton(
            self, text="Volver", width=300,
            fg_color="gray", hover_color="darkgray",
            command=self.mostrar_pantalla_dni
        ).pack(pady=15)

        self.polling_activo = True
        self.ciclo_polling()

    def ciclo_polling(self):
        if not self.polling_activo or self.id_cliente_actual is None:
            return

        resultado = DAOLegacy.consultar_estado_sesion(self.id_cliente_actual)
        print(f"Polling: {resultado}")  

        if resultado and resultado['SESION_ACTIVA']:
            self.polling_activo = False
            self.metodo_acceso = resultado.get('METODO_ACCESO', 'TRADICIONAL')
            self.mostrar_dashboard()
        else:
            self.after(INTERVALO_POLLING_MS, self.ciclo_polling)

    def login_tradicional(self):
        password = self.entry_pass.get()
        resultado = DAOLegacy.validar_usuario(self.dni_actual, password)

        if resultado:
            self.polling_activo = False
            self.metodo_acceso = 'TRADICIONAL'
            DAOLegacy.actualizar_sesion(self.id_cliente_actual, True, 'TRADICIONAL')
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Error", "Contrasena incorrecta.")

    def mostrar_registro(self):
        self.limpiar_pantalla()

        ctk.CTkLabel(self, text="CREAR CUENTA", font=("Arial", 18, "bold")).pack(pady=30)

        self.entry_dni_reg = ctk.CTkEntry(self, placeholder_text="DNI / RUT", width=300)
        self.entry_dni_reg.pack(pady=8)

        self.entry_pass_reg = ctk.CTkEntry(self, placeholder_text="Contrasena", show="*", width=300)
        self.entry_pass_reg.pack(pady=8)

        ctk.CTkButton(self, text="Registrarme", width=300, command=self.ejecutar_registro).pack(pady=10)
        ctk.CTkButton(
            self, text="Volver", width=300,
            fg_color="gray", hover_color="darkgray",
            command=self.mostrar_pantalla_dni
        ).pack(pady=5)

    def ejecutar_registro(self):
        dni = self.entry_dni_reg.get().strip()
        password = self.entry_pass_reg.get()

        if not dni or not password:
            messagebox.showwarning("Atencion", "Complete todos los campos.")
            return

        id_nuevo = DAOLegacy.registrar_usuario(dni, password)
        if id_nuevo:
            messagebox.showinfo("Exito", f"Cuenta creada correctamente.\nSu ID de cliente es: {id_nuevo}\nAhora puede iniciar sesion.")
            self.mostrar_pantalla_dni()
        else:
            messagebox.showerror("Error", "No se pudo registrar. El DNI ya existe.")

    def mostrar_dashboard(self):
        self.polling_activo = False
        self.limpiar_pantalla()

        # Encabezado
        ctk.CTkLabel(self, text="PANEL DE CONTROL", font=("Arial", 20, "bold")).pack(pady=(20, 4))
        ctk.CTkLabel(self, text=f"DNI: {self.dni_actual}   |   ID: {self.id_cliente_actual}", font=("Arial", 12)).pack()

        # Metodo de acceso
        if self.metodo_acceso == 'BIOMETRICO':
            color_metodo = "#27ae60"
            texto_metodo = "Sesion iniciada por reconocimiento facial - Sistema Biometrico Moderno"
        else:
            color_metodo = "#2980b9"
            texto_metodo = "Sesion iniciada por metodo tradicional (DNI / Contrasena)"

        ctk.CTkLabel(
            self, text=texto_metodo,
            font=("Arial", 10, "bold"), text_color=color_metodo
        ).pack(pady=(6, 14))

        # Cuentas
        ctk.CTkLabel(self, text="Mis Cuentas", font=("Arial", 14, "bold")).pack(anchor="w", padx=30)

        cuentas = DAOLegacy.obtener_cuentas(self.id_cliente_actual)

        if not cuentas:
            ctk.CTkLabel(self, text="No se encontraron cuentas asociadas.", font=("Arial", 11), text_color="gray").pack(pady=4)
        else:
            for cuenta in cuentas:
                frame_cuenta = ctk.CTkFrame(self, corner_radius=8)
                frame_cuenta.pack(fill="x", padx=30, pady=4)

                ctk.CTkLabel(
                    frame_cuenta,
                    text=f"{cuenta['TIPO_CUENTA']}",
                    font=("Arial", 12, "bold")
                ).pack(anchor="w", padx=12, pady=(8, 0))

                ctk.CTkLabel(
                    frame_cuenta,
                    text=f"Saldo: {cuenta['MONEDA']} {cuenta['SALDO']:,.2f}",
                    font=("Arial", 13), text_color="#27ae60"
                ).pack(anchor="w", padx=12)

                # Movimientos de esa cuenta
                movimientos = DAOLegacy.obtener_movimientos(cuenta['ID_CUENTA'])
                if movimientos:
                    ctk.CTkLabel(
                        frame_cuenta,
                        text="Ultimos movimientos:",
                        font=("Arial", 10), text_color="gray"
                    ).pack(anchor="w", padx=12, pady=(4, 0))

                    for mov in movimientos:
                        color_mov = "#27ae60" if mov['TIPO'] == 'INGRESO' else "#e74c3c"
                        signo = "+" if mov['TIPO'] == 'INGRESO' else "-"
                        fecha_str = mov['FECHA'].strftime("%d/%m/%Y")
                        ctk.CTkLabel(
                            frame_cuenta,
                            text=f"  {fecha_str}  {mov['DESCRIPCION']}   {signo}S/ {abs(mov['MONTO']):,.2f}",
                            font=("Arial", 10), text_color=color_mov
                        ).pack(anchor="w", padx=12)

                ctk.CTkLabel(frame_cuenta, text="").pack(pady=2)

        ctk.CTkButton(
            self, text="Cerrar Sesion", width=300,
            fg_color="#c0392b", hover_color="#922b21",
            command=self.cerrar_sesion
        ).pack(pady=16)
        
        self.polling_activo = True
        self.ciclo_polling_dashboard()
        
        
    def ciclo_polling_dashboard(self):
   
        if not self.polling_activo or self.id_cliente_actual is None:
            return

        resultado = DAOLegacy.consultar_estado_sesion(self.id_cliente_actual)

        if resultado and not resultado['SESION_ACTIVA']:
            self.polling_activo = False
            messagebox.showinfo(
                "Sesion cerrada",
                "La sesion fue cerrada desde el Kiosco Biometrico."
            )
            self.mostrar_pantalla_dni()
        else:
            self.after(INTERVALO_POLLING_MS, self.ciclo_polling_dashboard)
    

    def cerrar_sesion(self):
        if self.id_cliente_actual:
            DAOLegacy.actualizar_sesion(self.id_cliente_actual, False, 'NINGUNO')
        self.mostrar_pantalla_dni()

if __name__ == "__main__":
    app = BancoLegacyApp()
    app.mainloop()