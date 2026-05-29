# IA Clip Editor

Editor de clips basado en IA local para extraer audio de videos, transcribirlo y analizar la transcripción con un LLM local para detectar el mejor fragmento.

## Descripción

Este proyecto está pensado como un prototipo de pipeline de edición automática:

- Extrae audio de videos en `data/input/` usando `ffmpeg`
- Transcribe el audio con `faster-whisper`
- Analiza la transcripción con un modelo local ejecutado por Ollama
- Devuelve los timestamps de inicio/fin del mejor clip para edición posterior

## Estructura del proyecto

- `config.py`: configuración general, rutas y parámetros de los modelos
- `test_step1.py`: prueba de extracción de audio + transcripción
- `test_step2.py`: prueba completa con transcripción y análisis del LLM
- `src/audio/extractor.py`: extrae audio de archivos de video
- `src/ai/transcriber.py`: transcribe audio con `faster-whisper`
- `src/ai/orchestrator.py`: llama a Ollama y obtiene los timestamps del clip
- `data/`: carpeta para datos de entrada, salida y archivos temporales

## Requisitos

- Python 3.11+ (recomendado)
- `ffmpeg` instalado y disponible en PATH
- `ollama` instalado y corriendo localmente
- Modelo de Ollama descargado y disponible para ejecución
- Paquetes Python:
  - `faster-whisper`
  - `requests`

## Instalación

1. Crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. Instalar `ffmpeg` si no está disponible:

```bash
sudo apt install ffmpeg
```

4. Ejecutar Ollama localmente y cargar el modelo elegido:

```bash
ollama serve
ollama run llama3
```

## Uso

1. Copia uno o más archivos `.mp4` a `data/input/`
2. Ejecuta el paso 1 para extraer audio y transcribirlo:

```bash
source .venv/bin/activate
python test_step1.py
```

3. Ejecuta el paso 2 para extraer audio, transcribir y analizarlo con Ollama:

```bash
source .venv/bin/activate
python test_step2.py
```

4. Si quieres reiniciar la carpeta temporal:

```bash
rm -rf data/temp/*
```

## Configuración

Las rutas y algunos parámetros se controlan desde `config.py`:

- `INPUT_DIR`: carpeta de videos de entrada
- `OUTPUT_DIR`: carpeta de salida
- `TEMP_DIR`: carpeta temporal
- `OLLAMA_API_URL`: URL de la API local de Ollama
- `OLLAMA_MODEL`: nombre del modelo de Ollama
- `WHISPER_MODEL_SIZE`: tamaño de modelo Whisper (`small`, `medium`, etc.)

### Ejemplo: configuración para CPU

En `src/ai/transcriber.py`, la configuración por defecto es:

```python
model = WhisperModel(
    config.WHISPER_MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)
```

Esto es ideal si no cuentas con GPU o si estás probando el proyecto en una máquina local.

### Ejemplo: configuración para GPU

Si tienes una GPU NVIDIA con CUDA, puedes cambiar el bloque a:

```python
model = WhisperModel(
    config.WHISPER_MODEL_SIZE,
    device="cuda",
    compute_type="float16"
)
```

Usar GPU acelera la transcripción y puede mejorar el rendimiento en modelos más grandes.

## Observaciones

- El proyecto no contiene datos personales ni credenciales dentro del código.
- `data/` está ignorado en `.gitignore`, por lo que los videos y archivos temporales no se versionan.
- Si deseas usar GPU, ajusta `device` y `compute_type` en `src/ai/transcriber.py`.

## Solución de problemas

### Error: `ffmpeg` no encontrado

Si el script falla con un mensaje similar a `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`:

```bash
sudo apt install ffmpeg
```

Y luego verifica con:

```bash
ffmpeg -version
```

### Error: no se puede conectar a Ollama

Si `test_step2.py` falla al conectarse a Ollama, asegúrate de que el servidor esté activo:

```bash
ollama serve
```

Y que el modelo esté disponible:

```bash
ollama run llama3
```

### Error: respuesta JSON no válida de Ollama

Si ves un error en `json.loads` o el script imprime `No se pudo devolver un formato JSON válido`, revisa:

- que el modelo seleccionado sea compatible con la API de Ollama
- que no haya prompts o configuraciones no válidas en `src/ai/orchestrator.py`

### Problema de rendimiento en CPU

Si el procesamiento es demasiado lento en CPU, prueba:

- cambiar el modelo de Whisper a `small` en `config.py`
- usar `device="cuda"` y `compute_type="float16"` si tienes GPU NVIDIA

## Mejora futura

- Añadir módulo de edición de video para recortar el clip con los timestamps devueltos.
- Añadir validación de JSON más robusta y manejo de errores de Ollama.
- Añadir requerimientos formales `requirements.txt`.
