from pathlib import Path
from faster_whisper import WhisperModel
import config

def transcribe_local_audio(audio_path: Path) -> list:
    """
    Carga el modelo faster-whisper localmente y transcribe el audio,
    devolviendo una lista de diccionarios con el texto y sus timestamps.
    """
    if not audio_path.exists():
        print(f"❌ Error: El archivo de audio no existe: {audio_path}")
        return []

    print(f"🤖 Cargando modelo de IA Whisper ('{config.WHISPER_MODEL_SIZE}')...")
    
    # Configuración de aceleración de hardware:
    # Si tienes una GPU NVIDIA configurada con CUDA, usa device="cuda" y compute_type="float16"
    # Para probar de forma segura e inicial en cualquier procesador, dejamos "cpu" e "int8" (cuantizado)
    try:
        model = WhisperModel(
            config.WHISPER_MODEL_SIZE, 
            device="cpu",          # Cambia a "cuda" si tienes GPU dedicada con CUDA
            compute_type="int8"    # "int8" es ultra ligero para CPU. Usa "float16" para GPU.
        )
    except Exception as e:
        print(f"❌ No se pudo inicializar el modelo en el hardware seleccionado: {e}")
        return []

    print("🎙️ Transcribiendo audio en tiempo real (esto puede tomar un momento)...")
    
    # Ejecutamos la transcripción forzando el idioma español para ahorrar tiempo de cómputo
    segments, info = model.transcribe(str(audio_path), beam_size=5, language="es")
    
    print(f"📈 Idioma detectado de forma segura: {info.language} (Probabilidad: {info.language_probability:.2f})")

    transcripcion_estructurada = []

    # Iteramos sobre los segmentos detectados por la IA
    for segment in segments:
        # Formateamos los datos para que sean fáciles de leer por nuestro futuro LLM
        transcripcion_estructurada.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })
        # Imprime en consola un preview de lo que va escuchando la IA
        print(f"[{round(segment.start, 1)}s -> {round(segment.end, 1)}s] {segment.text}")

    print(f"✅ Transcripción completada. Se generaron {len(transcripcion_estructurada)} segmentos de texto.")
    return transcripcion_estructurada
