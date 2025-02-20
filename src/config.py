# src/config.py
import os

# Ruta base para recursos (asumiendo que el directorio "resources" está al mismo nivel que "src")
BASE_RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources')
DEPARTAMENTOS_PATH = os.path.join(BASE_RESOURCE_PATH, "codigos_municipios", "codigos_departamentos.xlsx")
MUNICIPIOS_PATH = os.path.join(BASE_RESOURCE_PATH, "codigos_municipios", "codigos_municipios_dian.xlsx")
