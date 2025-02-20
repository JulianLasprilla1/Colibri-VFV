# src/processing/file_cleaner.py
import pandas as pd
import re

class FileCleaner:
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Subclasses must implement the process() method.")

class FalabellaCleaner(FileCleaner):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        required = ["Customer Email", "National Registration Number",
                    "Shipping Name", "Shipping Address", "Shipping City", "Shipping Region"]
        for col in required:
            if col not in df.columns:
                df[col] = ""
            else:
                if col == "Customer Email":
                    df[col] = df[col].astype(str).str.lower()
                else:
                    df[col] = df[col].astype(str).str.upper()
        for col in ["Tipo Documento", "Validado", "ValidadoPor", "FechaValidacion"]:
            if col not in df.columns:
                df[col] = "NO" if col == "Validado" else ""
        df.drop_duplicates(subset=["National Registration Number"], inplace=True)
        return df


class MercadoLibreCleaner(FileCleaner):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        # Eliminar filas completamente en blanco
        df = df.dropna(how='all')
        # Eliminar registros donde "Tipo y número de documento" esté vacío o contenga solo espacios
        df = df[df["Tipo y número de documento"].notna() & (df["Tipo y número de documento"].astype(str).str.strip() != "")]
        
        # Renombrar columnas fijas
        df = df.rename(columns={
            "Datos personales o de empresa": "Shipping Name",
            "Dirección": "Shipping Address",
            "Municipio o ciudad capital": "Shipping City"
        })
        
        # Si "Shipping Address" (antes Dirección) está vacío, usar el valor de "Domicilio" si existe
        if "Domicilio" in df.columns:
            df["Shipping Address"] = df.apply(
                lambda row: row["Domicilio"] if not str(row["Shipping Address"]).strip() else row["Shipping Address"],
                axis=1
            )
        
        # Manejar duplicidad en "Estado": buscar columnas cuyo nombre base sea "Estado"
        estado_cols = [col for col in df.columns if col.split('.')[0] == "Estado"]
        if len(estado_cols) >= 2:
            # Tomar la segunda aparición
            df["Shipping Region"] = df[estado_cols[1]]
        else:
            df["Shipping Region"] = df["Estado"] if "Estado" in df.columns else ""
        
        # Procesar "Tipo y número de documento" para extraer el número y el tipo
        def extract_document_info(value):
            if pd.isna(value):
                return "", ""
            match = re.match(r'([A-Za-z]+)\s*(\d+)', str(value).strip())
            if match:
                doc_type = match.group(1).upper()  # Ejemplo: "CC"
                doc_number = match.group(2)          # Ejemplo: "1001886492"
                return doc_number, doc_type
            else:
                return str(value).strip(), ""
        
        extracted = df["Tipo y número de documento"].apply(lambda x: extract_document_info(x))
        df["National Registration Number"] = extracted.apply(lambda x: x[0])
        df["Tipo Documento"] = extracted.apply(lambda x: x[1])
        
        # Inicializar "Documento Val" igual a "National Registration Number"
        df["Documento Val"] = df["National Registration Number"]

        # Asegurar que existan las columnas adicionales requeridas
        if "Customer Email" not in df.columns:
            df["Customer Email"] = "facturann@jd-market.com"
        if "Validado" not in df.columns:
            df["Validado"] = "NO"
        if "Observación" not in df.columns:
            df["Observación"] = ""
            
        # Convertir a mayúsculas (excepto el email, que se pasa a minúsculas)
        for col in ["Shipping Name", "National Registration Number", "Documento Val", 
                    "Shipping Address", "Shipping City", "Shipping Region", "Tipo Documento", 
                    "Validado", "Observación"]:
            df[col] = df[col].astype(str).str.upper()
        df["Customer Email"] = df["Customer Email"].astype(str).str.lower()

        # Eliminar duplicados basados en "National Registration Number"
        df.drop_duplicates(subset=["National Registration Number"], inplace=True)
        return df