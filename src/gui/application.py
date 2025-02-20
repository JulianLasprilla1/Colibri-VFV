# src/gui/application.py
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap import ttk
import pandas as pd
import re
import webbrowser
from datetime import datetime
import os
from processing.utils import resource_path

# Importar utilidades y procesadores
from processing.utils import normalize_text, split_name
from processing.file_cleaner import FalabellaCleaner
from gui.dialogs import NameDialog

class Application(tb.Window):
    def __init__(self, themename="yeti"):
        super().__init__(themename=themename)
        self.title("🧹 Validador de Datos JD")
        self.geometry("1280x800")
        self.center_main_window()

        # Variables de datos
        self.df_original = None
        self.df_work = None
        self.validator_name = None
        self.loaded_filename = ""

        # Cargar recursos (rutas relativas)
        try:
            self.dept_codes = pd.read_excel(resource_path(os.path.join("resources", "codigos_municipios", "codigos_departamentos.xlsx")))
            self.dept_codes["NOMBRE"] = self.dept_codes["NOMBRE"].apply(normalize_text)
            self.dept_codes = dict(zip(self.dept_codes["NOMBRE"], self.dept_codes["CODIGO"].astype(str).str.zfill(2)))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar codigos_departamentos.xlsx: {e}")
            self.dept_codes = {}

        try:
            self.df_muni = pd.read_excel(resource_path(os.path.join("resources", "codigos_municipios", "codigos_municipios_dian.xlsx")))
            self.df_muni["MUNICIPIO"] = self.df_muni["MUNICIPIO"].apply(normalize_text)
            self.df_muni["CODIGO"] = self.df_muni["CODIGO"].astype(str).str.zfill(5)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar codigos_municipios_dian.xlsx: {e}")
            self.df_muni = None

        self.style.configure('Card.TFrame', background='white', borderwidth=1, relief='groove')
        self.style.configure('Treeview', rowheight=25)
        self.style.map('Treeview', background=[('selected', '#007bff')])
        
        self.crear_main_menu()
        self.after(100, self.ask_validator_name)

    def center_main_window(self):
        self.update_idletasks()
        width = self.winfo_width() or 1280
        height = self.winfo_height() or 800
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def center_window(self, win):
        win.update_idletasks()
        w = win.winfo_width() or 400
        h = win.winfo_height() or 300
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        win.geometry(f"+{x}+{y}")

    # Métodos de utilidad (por ejemplo, para validación de NIT, etc.)...
    @staticmethod
    def normalizar_valor(valor):
        return re.sub(r'[\s\.-]', '', str(valor))

    @staticmethod
    def calcular_digito_verificador(base):
        multiplicadores = [41, 37, 29, 23, 19, 17, 13, 7, 3]
        n = len(base)
        mult = multiplicadores[-n:]
        suma = sum(int(d) * m for d, m in zip(base, mult))
        residuo = suma % 11
        return residuo if residuo < 2 else 11 - residuo

    @staticmethod
    def es_nit(numero):
        num = Application.normalizar_valor(numero)
        if len(num) != 10 or not num.isdigit():
            return False
        base = num[:-1]
        try:
            int(num[-1])
        except ValueError:
            return False
        return Application.calcular_digito_verificador(base) == int(num[-1])

    # Diálogo de Nombre del Validador
    def ask_validator_name(self):
        dialog = NameDialog(self)
        self.wait_window(dialog)
        if not dialog.validator_name:
            messagebox.showwarning("Advertencia", "Debe ingresar su nombre y apellido para continuar.")
            self.destroy()
        else:
            self.validator_name = dialog.validator_name

    # Cargar y Procesar Excel
    def cargar_excel(self):
        ruta = filedialog.askopenfilename(
            title="Cargar Falabella Fulfillment",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if ruta:
            self.loaded_filename = os.path.basename(ruta)
            try:
                df_local = pd.read_excel(ruta)
                cleaner = FalabellaCleaner()
                df_local = cleaner.process(df_local)
                return df_local
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return None

    def cargar_archivo(self):
        df = self.cargar_excel()
        if df is not None:
            df["Documento Val"] = df["National Registration Number"]
            if "Observación" not in df.columns:
                df["Observación"] = ""
            self.df_original = df.copy()
            self.df_work = df.copy()
            if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
                self.menu_frame.destroy()
            self.inicializar_interfaz()
        else:
            messagebox.showwarning("Advertencia", "No se ha cargado ningún archivo.")

    def cargar_archivo_ml(self):
        df = self.abrir_excel_ml()
        if df is not None:
            if "Observación" not in df.columns:
                df["Observación"] = ""
            self.df_original = df.copy()
            self.df_work = df.copy()
            if hasattr(self, 'menu_frame') and self.menu_frame.winfo_exists():
                self.menu_frame.destroy()
            self.inicializar_interfaz()
        else:
            messagebox.showwarning("Advertencia", "No se ha cargado ningún archivo.")

    def abrir_excel_ml(self):
        ruta = filedialog.askopenfilename(
            title="Cargar archivo Mercado Libre",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if ruta:
            self.loaded_filename = os.path.basename(ruta)
            try:
                # Se usa header=5 porque los datos comienzan en la fila 6
                df_local = pd.read_excel(ruta, header=5)
                from processing.file_cleaner import MercadoLibreCleaner
                cleaner = MercadoLibreCleaner()
                df_local = cleaner.process(df_local)
                return df_local
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return None

    # Menú Principal Mejorado
    def crear_main_menu(self):
        self.menu_frame = ttk.Frame(self, padding=30)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor='center')
        title_label = ttk.Label(
            self.menu_frame,
            text="Validador de Datos",
            font=("Helvetica", 30, "bold"),
            bootstyle="primary"
        )
        title_label.grid(row=0, column=0, pady=(0,10))
        subtitle_label = ttk.Label(
            self.menu_frame,
            text="Seleccione el tipo de archivo a cargar",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        subtitle_label.grid(row=1, column=0, pady=(0,20))
        button_frame = ttk.Frame(self.menu_frame)
        button_frame.grid(row=2, column=0, pady=(0,20))
        
        # Botón para Falabella
        btn_load = ttk.Button(
            button_frame,
            text="📂 Falabella",
            command=self.cargar_archivo,
            bootstyle="primary",
            width=30
        )
        btn_load.grid(row=0, column=0, padx=10, pady=10)
        
        # NUEVO: Botón para Mercado Libre
        btn_ml = ttk.Button(
            button_frame,
            text="📂 Mercado Libre",
            command=self.cargar_archivo_ml,
            bootstyle="primary",
            width=30
        )
        btn_ml.grid(row=0, column=1, padx=10, pady=10)
        
        footer_label = ttk.Label(
            self.menu_frame,
            text="v1.0.0 | © 2025 by Julián Lasprilla",
            font=("Helvetica", 8),
            bootstyle="secondary"
        )
        footer_label.grid(row=3, column=0, pady=(10,0))


    # Interfaz Principal: Cards y Treeview
    def inicializar_interfaz(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill="x")
        ttk.Button(
            top_bar,
            text="◀ Menú Principal",
            command=self.regresar_menu,
            bootstyle="light-outline"
        ).pack(side="left")
        # Mostrar el nombre del archivo cargado
        if self.loaded_filename:
            validando_label = ttk.Label(top_bar, text=f"Validando: {self.loaded_filename}", font=("Helvetica", 10), bootstyle="info")
            validando_label.pack(side="left", padx=10)
        cards_container = ttk.Frame(self, padding=10)
        cards_container.pack(fill="x", padx=10, pady=5)
        # Card de Detalles
        self.detail_frame = ttk.Frame(cards_container, style='Card.TFrame', padding=10)
        self.detail_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.card_text = tk.Text(self.detail_frame, height=8, width=50, font=("Helvetica", 10), wrap=tk.WORD, bg="white")
        self.card_text.tag_configure("bold", font=("Helvetica", 10, "bold"))
        self.card_text.config(state=tk.DISABLED)
        self.card_text.pack(padx=10, pady=10, fill="both", expand=True)
        # Card de Resumen
        self.stats_frame = ttk.Frame(cards_container, style='Card.TFrame', padding=5)
        self.stats_frame.pack(side="left", fill="y", padx=5)
        self.stats_label = ttk.Label(
            self.stats_frame,
            text="Resumen:\n",
            font=("Helvetica", 10, "bold"),
            foreground="#2c3e50",
            anchor="w",
            justify="left"
        )
        self.stats_label.pack(padx=5, pady=5)
        self.mostrar_barra_busqueda()
        # Treeview
        self.treeview = ttk.Treeview(
            self,
            columns=["National Registration Number", "Documento Val", "Shipping Name", "Customer Email",
                     "Shipping Address", "Shipping City", "Shipping Region",
                     "Tipo Documento", "Validado"],
            show="headings",
            selectmode="browse",
            bootstyle="secondary",
            height=15
        )
        columnas = {
            "National Registration Number": ("Documento", 140),
            "Documento Val": ("Documento Val", 140),
            "Shipping Name": ("Nombre", 180),
            "Customer Email": ("Correo", 200),
            "Shipping Address": ("Dirección", 220),
            "Shipping City": ("Ciudad", 120),
            "Shipping Region": ("Región", 100),
            "Tipo Documento": ("Tipo Doc.", 100),
            "Validado": ("Estado", 80)
        }
        for col, (texto, ancho) in columnas.items():
            self.treeview.heading(col, text=texto, anchor="w")
            self.treeview.column(col, width=ancho, anchor="w", stretch=True)
        self.treeview.pack(expand=True, fill="both", padx=10, pady=5)
        self.treeview.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.treeview.bind("<Double-Button-1>", lambda e: self.accion_editar())
        self.treeview.bind("<Double-Button-3>", lambda e: self.accion_validar())
        self.sidebar = ttk.Frame(self, padding=10)
        self.sidebar.pack(side="right", fill="y", padx=10, pady=5)
        acciones = [
            ("✏ Editar", self.accion_editar, 'warning'),
            ("📋 Copiar", self.accion_copiar, 'info'),
            ("✅ Validar", self.accion_validar, 'success')
        ]
        for texto, comando, estilo in acciones:
            ttk.Button(
                self.sidebar,
                text=texto,
                command=comando,
                bootstyle=f"{estilo}-outline",
                width=15
            ).pack(pady=5, fill="x")
        self.bottom_frame = ttk.Frame(self, padding=10)
        self.bottom_frame.pack(pady=10)
        botones_inferiores = [
            ("💾 Guardar", self.guardar_datos, 'success'),
            ("🌐 DIAN", self.abrir_dian, 'primary'),
            ("👮 Policía", self.abrir_policia, 'primary')
        ]
        for texto, comando, estilo in botones_inferiores:
            ttk.Button(
                self.bottom_frame,
                text=texto,
                command=comando,
                bootstyle=f"{estilo}-outline",
                width=15
            ).pack(side="left", padx=5)
        self.refrescar_treeview()

    def mostrar_barra_busqueda(self):
        self.search_frame = ttk.Frame(self, padding=10)
        self.search_frame.pack(fill="x")
        ttk.Label(
            self.search_frame, 
            text="🔍 Buscar:", 
            font=("Helvetica", 10)
        ).pack(side="left")
        self.busqueda_var = tk.StringVar()
        ttk.Entry(
            self.search_frame,
            textvariable=self.busqueda_var,
            font=("Helvetica", 10),
            width=40,
            bootstyle="primary"
        ).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(
            self.search_frame,
            text="Buscar",
            command=self.filtrar_registros,
            bootstyle="primary-outline"
        ).pack(side="left", padx=5)
        ttk.Button(
            self.search_frame,
            text="Limpiar",
            command=lambda: [self.busqueda_var.set(""), self.refrescar_treeview()],
            bootstyle="secondary-outline"
        ).pack(side="left", padx=5)

    def refrescar_treeview(self, data=None):
        if data is None:
            data = self.df_work
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for indice, fila in data.iterrows():
            tag = ("validado",) if fila["Validado"].strip().upper() == "SI" else ()
            self.treeview.insert("", "end", iid=indice, values=(
                fila["National Registration Number"],
                fila["Documento Val"],
                fila["Shipping Name"],
                fila["Customer Email"],
                fila["Shipping Address"],
                fila["Shipping City"],
                fila["Shipping Region"],
                fila["Tipo Documento"],
                fila["Validado"]
            ), tags=tag)
        self.treeview.tag_configure("validado", background="#d4edda")
        self.actualizar_stats()

    def filtrar_registros(self):
        texto = self.busqueda_var.get().strip().upper()
        if texto == "":
            self.refrescar_treeview()
        else:
            filtro = self.df_work.apply(
                lambda row: texto in row["National Registration Number"] or texto in row["Shipping Name"],
                axis=1
            )
            df_filtrado = self.df_work[filtro]
            self.refrescar_treeview(df_filtrado)

    def actualizar_tarjeta(self):
        seleccionado = self.treeview.focus()
        self.card_text.config(state=tk.NORMAL)
        self.card_text.delete("1.0", tk.END)
        if seleccionado:
            try:
                indice = int(seleccionado)
                registro = self.df_work.loc[indice]
                self.card_text.insert(tk.END, f"Documento: {registro['National Registration Number']}\n")
                self.card_text.insert(tk.END, f"Documento Val: {registro['Documento Val']}\n", "bold")
                self.card_text.insert(tk.END, f"Nombre: {registro['Shipping Name']}\n", "bold")
                self.card_text.insert(tk.END, f"Correo: {registro['Customer Email']}\n")
                self.card_text.insert(tk.END, f"Dirección: {registro['Shipping Address']}\n", "bold")
                self.card_text.insert(tk.END, f"Ciudad: {registro['Shipping City']}\n")
                self.card_text.insert(tk.END, f"Región: {registro['Shipping Region']}\n")
                self.card_text.insert(tk.END, f"Tipo Documento: {registro['Tipo Documento']}\n")
                self.card_text.insert(tk.END, f"Validado: {registro['Validado']}\n")
            except Exception as e:
                self.card_text.insert(tk.END, f"Error al obtener información: {e}")
        else:
            self.card_text.insert(tk.END, "Seleccione un registro para ver su información.")
        self.card_text.config(state=tk.DISABLED)

    def actualizar_stats(self):
        total = len(self.df_work)
        validos = (self.df_work["Validado"].str.upper() == "SI").sum()
        no_validos = total - validos
        cc = (self.df_work["Tipo Documento"].str.upper() == "CC").sum()
        nit = (self.df_work["Tipo Documento"].str.upper() == "NIT").sum()
        ce = (self.df_work["Tipo Documento"].str.upper() == "CE").sum()
        doc_nv = (self.df_work["Tipo Documento"].str.upper() == "DOCUMENTO NO VÁLIDO").sum()
        resumen = (
            f"Por validar: {no_validos}\n"
            f"Validados: {validos}\n"
            f"CC: {cc} | NIT: {nit} | CE: {ce} | Doc no válido: {doc_nv}"
        )
        self.stats_label.config(text="Resumen:\n" + resumen)

    def on_tree_select(self, event):
        self.actualizar_tarjeta()

    def accion_editar(self):
        seleccionado = self.treeview.focus()
        if seleccionado:
            self.editar_registro_por_id(int(seleccionado))
        else:
            messagebox.showwarning("Advertencia", "Seleccione un registro para editar.")

    def accion_copiar(self):
        seleccionado = self.treeview.focus()
        if seleccionado:
            self.copiar_identificacion_por_id(int(seleccionado))
        else:
            messagebox.showwarning("Advertencia", "Seleccione un registro para copiar el documento.")

    def accion_validar(self):
        seleccionado = self.treeview.focus()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un registro para validar.")
            return
        self.validar_registro_por_id(int(seleccionado))

    def editar_registro_por_id(self, indice):
        ventana_editar = tk.Toplevel(self)
        ventana_editar.title("Editar Registro")
        self.center_window(ventana_editar)
        ventana_editar.transient(self)
        ventana_editar.grab_set()
        ventana_editar.resizable(False, False)
        def on_unmap(event):
            if ventana_editar.state() == "iconic":
                ventana_editar.deiconify()
        ventana_editar.bind("<Unmap>", on_unmap)

        entradas = {}
        fields = [
            ("National Registration Number", "Documento", True),
            ("Documento Val", "Documento Val", False),
            ("Shipping Name", "Nombre", False),
            ("Customer Email", "Correo", False),
            ("Shipping Address", "Dirección", False),
            ("Shipping City", "Ciudad", False),
            ("Shipping Region", "Región", False),
            ("Observación", "Observación", False)
        ]
        for i, (campo, etiqueta, readonly) in enumerate(fields):
            tk.Label(ventana_editar, text=etiqueta, font=("Helvetica", 10))\
                .grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entrada = tk.Entry(ventana_editar, width=50, font=("Helvetica", 10))
            entrada.grid(row=i, column=1, padx=5, pady=5)
            value = str(self.df_work.loc[indice, campo]) if campo in self.df_work.columns else ""
            if campo == "Customer Email":
                value = value.lower()
            else:
                value = value.upper()
            entrada.insert(0, value)
            if readonly:
                entrada.config(state="readonly")
            entradas[campo] = entrada

        row_index = len(fields)
        tk.Label(ventana_editar, text="Tipo Documento", font=("Helvetica", 10))\
            .grid(row=row_index, column=0, padx=5, pady=5, sticky="w")
        var_tipo = tk.StringVar()
        combobox_tipo = ttk.Combobox(
            ventana_editar,
            textvariable=var_tipo,
            state="readonly",
            values=["CC", "NIT", "CE", "Documento no válido"]
        )
        combobox_tipo.grid(row=row_index, column=1, padx=5, pady=5)
        valor_actual = self.df_work.loc[indice, "Tipo Documento"]
        combobox_tipo.set(valor_actual.strip() if valor_actual.strip() else "")
        
        var_validado = tk.BooleanVar(value=(str(self.df_work.loc[indice, "Validado"]).strip().upper() == "SI"))
        tk.Checkbutton(
            ventana_editar,
            text="Validado",
            variable=var_validado,
            font=("Helvetica", 10)
        ).grid(row=row_index+1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(
            ventana_editar,
            text="Guardar",
            command=lambda: self.guardar_cambios_edicion(indice, entradas, var_tipo, var_validado, ventana_editar),
            bootstyle="flat-primary"
        ).grid(row=row_index+2, column=0, columnspan=2, pady=10)

        self.wait_window(ventana_editar)

    def guardar_cambios_edicion(self, indice, entradas, var_tipo, var_validado, ventana_editar):
        if not var_tipo.get().strip():
            messagebox.showwarning("Advertencia", "Debe seleccionar un tipo de documento.")
            return

        editable_fields = ["Documento Val", "Shipping Name", "Customer Email", 
                           "Shipping Address", "Shipping City", "Shipping Region", "Observación"]
        for campo in editable_fields:
            if campo == "Customer Email":
                self.df_work.loc[indice, campo] = entradas[campo].get().lower()
            elif campo == "Observación":
                self.df_work.loc[indice, campo] = entradas[campo].get()[:100]
            else:
                self.df_work.loc[indice, campo] = entradas[campo].get().upper()
        self.df_work.loc[indice, "Tipo Documento"] = var_tipo.get().upper()
        if var_validado.get():
            self.df_work.loc[indice, "Validado"] = "SI"
            self.df_work.loc[indice, "ValidadoPor"] = self.validator_name
            self.df_work.loc[indice, "FechaValidacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.df_work.loc[indice, "Validado"] = "NO"
        if self.busqueda_var.get().strip():
            self.filtrar_registros()
        else:
            self.refrescar_treeview()
        self.actualizar_tarjeta()
        ventana_editar.destroy()

    def copiar_identificacion_por_id(self, indice):
        valor = self.df_work.loc[indice, "National Registration Number"]
        self.clipboard_clear()
        self.clipboard_append(str(valor))
        messagebox.showinfo("Éxito", f"Documento '{valor}' copiado al portapapeles.")

    def validar_registro_por_id(self, indice):
        doc_tipo = self.df_work.loc[indice, "Tipo Documento"].strip().upper()
        if not doc_tipo:
            self.df_work.loc[indice, "Tipo Documento"] = "CC"
            doc_tipo = "CC"
        if doc_tipo not in ["CC", "NIT", "CE", "DOCUMENTO NO VÁLIDO"]:
            messagebox.showwarning("Advertencia", "El registro validado debe tener un tipo de documento válido.")
            return

        self.df_work.loc[indice, "Validado"] = "SI"
        self.df_work.loc[indice, "ValidadoPor"] = self.validator_name
        self.df_work.loc[indice, "FechaValidacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.busqueda_var.get().strip():
            self.filtrar_registros()
        else:
            self.refrescar_treeview()
        self.actualizar_tarjeta()
        messagebox.showinfo("Éxito", "Registro validado.")

    def abrir_dian(self):
        webbrowser.open("https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces")

    def abrir_policia(self):
        webbrowser.open("https://antecedentes.policia.gov.co:7005/WebJudicial/")

    def guardar_datos(self):
        if (self.df_work["Validado"].str.upper() != "SI").any():
            messagebox.showwarning("Advertencia", "No se puede guardar el archivo final sin que todos los registros estén validados.")
            return
        default_file_name = f"terceros_full_falabella_{self.validator_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta_guardado = filedialog.asksaveasfilename(
            initialfile=default_file_name,
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if ruta_guardado:
            try:
                registros = []
                for _, row in self.df_work.iterrows():
                    tipo_doc = row["Tipo Documento"].strip().upper()
                    if tipo_doc == "CC":
                        tipo_identificacion = "C"
                    elif tipo_doc == "NIT":
                        tipo_identificacion = "N"
                    else:
                        tipo_identificacion = tipo_doc
                    
                    if tipo_identificacion == "C":
                        tipo_tercero = "1"
                        a1, a2, nombres = split_name(row["Shipping Name"])
                        razon_social = ""
                    elif tipo_identificacion == "N":
                        tipo_tercero = "2"
                        razon_social = row["Shipping Name"]
                        a1, a2, nombres = "", "", ""
                    else:
                        tipo_tercero = ""
                        razon_social = ""
                        a1, a2, nombres = "", "", row["Shipping Name"]
                    
                    dept_nombre = normalize_text(row["Shipping Region"])
                    dept_code = self.dept_codes.get(dept_nombre, "")
                    
                    if dept_code == "11":
                        municipio_code = "001"
                    else:
                        muni_nombre = normalize_text(row["Shipping City"])
                        municipio_code = ""
                        if self.df_muni is not None and dept_code:
                            df_filtered = self.df_muni[self.df_muni["MUNICIPIO"] == muni_nombre]
                            if not df_filtered.empty:
                                for _, muni_row in df_filtered.iterrows():
                                    codigo_muni = str(muni_row["CODIGO"]).zfill(5)
                                    if codigo_muni.startswith(dept_code):
                                        municipio_code = codigo_muni[-3:]
                                        break
                        if municipio_code == "" and muni_nombre in ["BOGOTA", "BOGOTA DC"]:
                            municipio_code = "001"
                    
                    pais_codigo = "169"
                    
                    tel = str(row.get("telefono", "")).strip()
                    if not tel or tel.lower() == "nan":
                        tel = "7559242"
                    cel = str(row.get("celular", "")).strip()
                    if not cel or cel.lower() == "nan":
                        cel = "6017559242"
                    corr = str(row["Customer Email"]).strip()
                    if corr.lower() == "nan" or corr == "":
                        corr = "facturann@jd-market.com"
                    
                    registro = {
                        "identificacion_tercero": str(row["Documento Val"]),
                        "numero_identificacion_tercero": str(row["Documento Val"]),
                        "tipo_identificacion": tipo_identificacion,
                        "tipo_tercero_natural_1_juridica_2": tipo_tercero,
                        "razon_social": razon_social,
                        "apellido_1": a1,
                        "apellido_2": a2,
                        "nombres": nombres,
                        "contacto_nombre_completo_razon_social": row["Shipping Name"],
                        "direccion": row["Shipping Address"],
                        "pais_codigo": pais_codigo,
                        "departamento_codigo": dept_code,
                        "ciudad_codigo": municipio_code,
                        "telefono": tel,
                        "correo": corr,
                        "no_domiciliado_pais_1_si_0_no": "0",
                        "celular": cel,
                        "ValidadoPor": row["ValidadoPor"],
                        "FechaValidacion": row["FechaValidacion"],
                        "Observación": str(row.get("Observación", ""))[:100]
                    }
                    registros.append(registro)
                df_guardar = pd.DataFrame(registros)
                for col in df_guardar.columns:
                    df_guardar[col] = df_guardar[col].astype(str)
                df_guardar.to_excel(ruta_guardado, index=False)
                messagebox.showinfo("Éxito", "Datos guardados exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar el archivo: {e}")

    def regresar_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.crear_main_menu()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
