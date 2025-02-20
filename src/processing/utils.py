# src/processing/utils.py
import re
import unicodedata
import sys
import os

def normalize_text(text: str) -> str:
    """
    Convierte el texto a mayúsculas, elimina tildes, signos diacríticos,
    quita puntuación y espacios extras.
    """
    text = str(text).strip().upper()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_name(full_name: str):
    """
    Separa el string full_name en (apellido_1, apellido_2, nombres) usando la siguiente heurística:
      - 0 tokens: devuelve ("", "", "")
      - 1 token: se asume solo el nombre.
      - 2 tokens: se asume: primer token = nombre, segundo token = apellido_1.
      - 3 tokens: se asume: primer token = nombre, segundo token = apellido_1, tercer token = apellido_2.
      - 4 o más tokens: se asume que los dos últimos tokens son los apellidos y el resto forman los nombres.
    """
    tokens = full_name.strip().split()
    n = len(tokens)
    if n == 0:
        return "", "", ""
    elif n == 1:
        return "", "", tokens[0]
    elif n == 2:
        return tokens[1], "", tokens[0]
    elif n == 3:
        return tokens[1], tokens[2], tokens[0]
    else:
        given_names = " ".join(tokens[:-2])
        surname1 = tokens[-2]
        surname2 = tokens[-1]
        return surname1, surname2, given_names
    
def resource_path(relative_path):
    """
    Devuelve la ruta absoluta al recurso, compatible tanto en desarrollo
    como cuando la aplicación está empaquetada por PyInstaller.
    """
    try:
        # Cuando la aplicación está empaquetada, sys._MEIPASS contiene la carpeta temporal
        base_path = sys._MEIPASS
    except Exception:
        # En desarrollo, usamos el directorio actual
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)