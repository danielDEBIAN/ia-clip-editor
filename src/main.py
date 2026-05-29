import sys
from pathlib import Path

# Asegurar rutas
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import config
from src.audio.extractor import extract_audio
from src.ai.transcriber import transcribe_local_audio
from src.ai.orchestrator import analyze_transcript_for_clips
from src.video.editor import cut_video_clip, create_subtitles_txt

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

    # 3. Análisis de Contenido (Ollama ahora devuelve una lista de clips)
    # Nota: Si cambiaste el nombre en orchestrator, actualízalo aquí también
    lista_decisiones = analyze_transcript_for_clips(transcripcion)

    if not lista_decisiones or not isinstance(lista_decisiones, list):
        print("❌ La IA no devolvió una lista válida de clips o no encontró momentos clave.")
        return

    print(f"🎬 ¡La IA encontró {len(lista_decisiones)} clips potenciales para editar!")
    print("\n" + "-"*40)

    # 4. Bucle de Corte, Renderizado y generación de TXT
    clips_creados = 0
    for indice, decision in enumerate(lista_decisiones, start=1):
        inicio = decision.get("inicio")
        fin = decision.get("fin")
        justificacion = decision.get("justificacion")

        # Definimos los nombres de los archivos finales
        nombre_salida_video = f"clip_{indice}_{video_objetivo.stem}.mp4"
        nombre_salida_txt = f"clip_{indice}_{video_objetivo.stem}_subtitulos.txt"
        ruta_txt_completa = config.OUTPUT_DIR / nombre_salida_txt

        print(f"\n🎥 Procesando Clip #{indice} de {len(lista_decisiones)}...")
        print(f"💡 Razón de la IA: {justificacion}")

        # 1. Cortamos el video físico
        exito_video = cut_video_clip(video_objetivo, inicio, fin, nombre_salida_video)

        if exito_video:
            # 2. Si el video se creó bien, generamos su TXT de subtítulos usando la transcripción que ya tenemos
            create_subtitles_txt(transcripcion, inicio, fin, ruta_txt_completa)
            clips_creados += 1

    print("==================================================")
    if clips_creados > 0:
        print(f"🏁 PIPELINE COMPLETADO. Se generaron {clips_creados} clips exitosamente.")
        print(f"📁 Revisa tus archivos terminados en: data/output/")
    else:
        print("❌ No se pudo renderizar ningún clip.")
    print("==================================================")

if __name__ == "__main__":
    main()