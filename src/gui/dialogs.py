# src/gui/dialogs.py
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap import ttk

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
