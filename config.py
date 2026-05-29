import os
from pathlib import Path

# Rutas Base del Proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"

# Crear las carpetas automáticamente si no existen al iniciar
for folder in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Configuraciones de IA Local
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # O el modelo ligero que elijas (ej. phi3)
WHISPER_MODEL_SIZE = "small"  # Puedes cambiar a 'medium' si tienes buena VRAM
