# src/gui/dialogs.py
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap import ttk
import tkinter as tk
import pandas as pd
import os
from config import BASE_RESOURCE_PATH
import datetime
from processing.crypto_utils import encrypt_password




class NameDialog(tb.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🔑 Identificación del Validador")
        self.resizable(False, False)
        self.transient(parent)
        self.validator_name = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill='both', expand=True)

        lbl_instruction = ttk.Label(
            container,
            text="Ingrese su nombre completo (Formato: Nombre Apellido):",
            font=("Helvetica", 10),
            bootstyle="inverse-light"
        )
        lbl_instruction.pack(pady=5)

        self.entry = ttk.Entry(container, width=30, font=("Helvetica", 10))
        self.entry.pack(pady=10, ipady=3)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=5)
        ttk.Button(
            btn_frame,
            text="Confirmar",
            command=self.on_ok,
            bootstyle="success",
            width=12
        ).pack(side='left', padx=5)
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.on_close,
            bootstyle="danger-outline",
            width=12
        ).pack(side='left', padx=5)

        self.center_window(parent)

    def center_window(self, parent):
        parent.update_idletasks()
        width = 400
        height = 160
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def on_ok(self):
        name = self.entry.get().strip()
        parts = name.split()
        if len(parts) != 2:
            messagebox.showwarning("Error", "Debe ingresar EXACTAMENTE un nombre y un apellido.")
            return
        for part in parts:
            if not part[0].isupper():
                messagebox.showwarning("Error", "Cada parte del nombre debe iniciar con mayúscula.")
                return
        self.validator_name = name
        self.destroy()

    def on_close(self):
        self.validator_name = None
        self.destroy()

USERS_FILE = os.path.join(BASE_RESOURCE_PATH, "users", "users.xlsx")
class UserLoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Inicio de Sesión")
        self.resizable(False, False)
        self.transient(parent)
        self.logged_user = None

        container = ttk.Frame(self, padding=15)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text="Seleccione su nombre:", font=("Helvetica", 10)).pack(pady=5)
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(container, textvariable=self.user_var, state="readonly", width=30)
        self.user_combo.pack(pady=5)

        ttk.Label(container, text="Contraseña:", font=("Helvetica", 10)).pack(pady=5)
        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Iniciar Sesión", command=self.on_login, width=12).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Registrarse", command=self.on_register, width=12).pack(side='left', padx=5)

        self.load_users()
        self.center_window(parent)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def center_window(self, parent):
        parent.update_idletasks()
        width = 400
        height = 250
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_users(self):
        # Cargar usuarios desde el archivo; si no existe, la lista estará vacía
        try:
            df = pd.read_excel(USERS_FILE)
            users = df["Nombre"].tolist()
        except Exception:
            users = []
        self.user_combo['values'] = users
        if users:
            self.user_combo.current(0)

    def on_login(self):
        import pandas as pd
        from processing.crypto_utils import decrypt_password
        selected = self.user_var.get().strip()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario.")
            return
        password = self.password_entry.get().strip()
        if not password:
            messagebox.showwarning("Advertencia", "Ingrese su contraseña.")
            return
        try:
            df = pd.read_excel(USERS_FILE)
        except Exception:
            messagebox.showerror("Error", "No se pudo cargar el archivo de usuarios.")
            return
        user_record = df[df["Nombre"].str.upper() == selected.upper()]
        if user_record.empty:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        stored_encrypted = user_record.iloc[0]["Password"]
        try:
            stored_password = decrypt_password(stored_encrypted)
        except Exception:
            messagebox.showerror("Error", "Error al desencriptar la contraseña. Consulte al administrador.")
            return
        if password == stored_password:
            self.logged_user = selected
            self.destroy()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")

    def on_register(self):
        reg_dialog = UserRegistrationDialog(self)
        self.wait_window(reg_dialog)
        # Recargar la lista de usuarios después del registro
        self.load_users()

    def on_close(self):
        self.logged_user = None
        self.destroy()

class UserRegistrationDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registro de Usuario")
        self.resizable(False, False)
        self.transient(parent)

        container = ttk.Frame(self, padding=15)
        container.pack(fill='both', expand=True)

        ttk.Label(container, text="Nombre completo (Nombre Apellido):", font=("Helvetica", 10)).pack(pady=5)
        self.name_entry = ttk.Entry(container, width=30)
        self.name_entry.pack(pady=5)

        ttk.Label(container, text="Contraseña:", font=("Helvetica", 10)).pack(pady=5)
        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        ttk.Label(container, text="Confirmar Contraseña:", font=("Helvetica", 10)).pack(pady=5)
        self.confirm_entry = ttk.Entry(container, show="*", width=30)
        self.confirm_entry.pack(pady=5)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Registrar", command=self.on_register, width=12).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy, width=12).pack(side='left', padx=5)

        self.center_window(parent)

    def center_window(self, parent):
        parent.update_idletasks()
        width = 400
        height = 300
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def on_register(self):
        name = self.name_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        if not name or len(name.split()) != 2:
            messagebox.showwarning("Error", "Ingrese el nombre y apellido (exactamente dos palabras).")
            return
        if password == "" or password != confirm:
            messagebox.showwarning("Error", "Las contraseñas no coinciden o están vacías.")
            return
        encrypted = encrypt_password(password)
        # Registro: por defecto, rol "Usuario" y la fecha actual
        registro = {
            "Nombre": name.upper(),
            "Password": encrypted,
            "Rol": "Usuario",
            "FechaModificacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Intentar cargar el archivo de usuarios; si no existe, crearlo
        import pandas as pd
        import os
        if os.path.exists(USERS_FILE):
            df = pd.read_excel(USERS_FILE)
        else:
            df = pd.DataFrame(columns=["Nombre", "Password", "Rol", "FechaModificacion"])
        # Agregar el nuevo registro y guardar
        df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
        try:
            os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
            df.to_excel(USERS_FILE, index=False)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el usuario: {e}")