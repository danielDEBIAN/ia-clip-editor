import sys
from pathlib import Path

# Asegurar rutas
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import config
from src.audio.extractor import extract_audio
from src.ai.transcriber import transcribe_local_audio
from src.ai.orchestrator import analyze_transcript_for_clip
from src.video.editor import cut_video_clip

def main():
    print("==================================================")
    # Buscamos si hay videos en la carpeta de entrada
    videos = list(config.INPUT_DIR.glob("*.mp4"))

    if not videos:
        print(f"⚠️  No se encontraron videos en: {config.INPUT_DIR}")
        print("👉 Coloca un archivo .mp4 ahí para comenzar.")
        return

    # Procesamos el primer video de la lista
    video_objetivo = videos[0]
    audio_temporal = config.TEMP_DIR / f"{video_objetivo.stem}_temp.wav"
    nombre_salida = f"clip_{video_objetivo.stem}.mp4"

    print(f"🚀 INICIANDO AUTOMATIZACIÓN PARA: {video_objetivo.name}")
    print("==================================================")

    # 1. Extracción de Audio (FFmpeg)
    if not extract_audio(video_objetivo, audio_temporal):
        return

    print("\n" + "-"*40)

    # 2. Transcripción Local (faster-whisper)
    transcripcion = transcribe_local_audio(audio_temporal)
    if not transcripcion:
        return

    print("\n" + "-"*40)

    # 3. Análisis de Contenido (Ollama + LLM)
    decision = analyze_transcript_for_clip(transcripcion)
    if not decision:
        return

    inicio = decision.get("inicio")
    fin = decision.get("fin")

    print("\n" + "-"*40)

    # 4. Corte y Renderizado Final (MoviePy)
    exito = cut_video_clip(video_objetivo, inicio, fin, nombre_salida)

    print("==================================================")
    if exito:
        print("🏁 PIPELINE COMPLETADO AL 100% SIN COSTAR UN SOLO CENTAVO.")
        print(f"📁 Revisa tu clip terminado en: data/output/{nombre_salida}")
    else:
        print("❌ El proceso terminó con errores en la fase de video.")
    print("==================================================")

if __name__ == "__main__":
    main()