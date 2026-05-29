# test_step1.py
from pathlib import Path
import config
from src.audio.extractor import extract_audio
from src.ai.transcriber import transcribe_local_audio

def main():
    print("🚀 Iniciando prueba del Paso 1 del Editor de Clips...\n")

    # 1. Busca cualquier video .mp4 en la carpeta data/input/
    videos_disponibles = list(config.INPUT_DIR.glob("*.mp4"))

    if not videos_disponibles:
        print(f"⚠️  No se encontraron videos (.mp4) en la carpeta: {config.INPUT_DIR}")
        print("👉 Por favor, arrastra un video corto de prueba ahí y vuelve a ejecutar el script.")
        return

    # Tomamos el primer video que encuentre
    video_prueba = videos_disponibles[0]
    audio_temporal = config.TEMP_DIR / f"{video_prueba.stem}_temp.wav"

    # Execución del Pipeline: Paso 1 (Extracción)
    if extract_audio(video_prueba, audio_temporal):
        print("-" * 50)
        # Execución del Pipeline: Paso 2 (Transcripción)
        datos_transcripcion = transcribe_local_audio(audio_temporal)

        print("\n🎉 ¡Éxito! Estructura de datos lista para el LLM:")
        # Mostramos los primeros 3 elementos del array resultante como ejemplo
        print(datos_transcripcion[:3])

if __name__ == "__main__":
    main()
