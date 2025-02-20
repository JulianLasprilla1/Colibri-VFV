# src/processing/file_cleaner.py
import pandas as pd

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
