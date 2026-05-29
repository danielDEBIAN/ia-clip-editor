# test_step2.py
from pathlib import Path
import config
from src.audio.extractor import extract_audio
from src.ai.transcriber import transcribe_local_audio
from src.ai.orchestrator import analyze_transcript_for_clip

def main():
    print("🚀 Iniciando prueba del Paso 2 (Audio + Transcripción + LLM Local)...\n")

    # Buscamos el video en input
    videos_disponibles = list(config.INPUT_DIR.glob("*.mp4"))

    if not videos_disponibles:
        print(f"⚠️ No se encontraron videos (.mp4) en: {config.INPUT_DIR}")
        return

    video_prueba = videos_disponibles[0]
    audio_temporal = config.TEMP_DIR / f"{video_prueba.stem}_temp.wav"

    # 1. Extraer Audio
    if not extract_audio(video_prueba, audio_temporal):
        return

    print("-" * 50)

    # 2. Transcribir con faster-whisper
    datos_transcripcion = transcribe_local_audio(audio_temporal)
    if not datos_transcripcion:
        return

    print("-" * 50)

    # 3. Analizar y obtener los timestamps del mejor clip con Ollama
    decision_clip = analyze_transcript_for_clip(datos_transcripcion)

    if decision_clip:
        print("🎉 ¡Pipeline de Inteligencia Artificial completado con éxito!")
        print(f"Listo para enviar estos tiempos al módulo de edición de video: {decision_clip.get('inicio')} a {decision_clip.get('fin')}")

if __name__ == "__main__":
    main()
