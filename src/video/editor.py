import sys
from pathlib import Path

# Salvavidas de rutas para importar config
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import config
from moviepy.video.io.VideoFileClip import VideoFileClip

def cut_video_clip(video_path: Path, start_time: float, end_time: float, output_name: str) -> bool:
    """
    Toma un video original, lo corta entre start_time y end_time,
    y exporta el clip final a la carpeta de output.
    """
    if not video_path.exists():
        print(f"❌ Error: El video original no existe en {video_path}")
        return False

    output_path = config.OUTPUT_DIR / output_name
    print(f"🎬 Abriendo video original para cortar: {video_path.name}...")
    print(f"⏱️  Cortando fragmento: {start_time}s -> {end_time}s")

    try:
        # Cargamos el video en memoria
        with VideoFileClip(str(video_path)) as video:
            # 💡 CAMBIO AQUÍ: Usamos .subclipped en lugar de .subclip
            clip = video.subclipped(start_time, end_time)

            print("⏳ Renderizando el clip final localmente (esto consume CPU/GPU)...")
            # Exportamos el archivo
            clip.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                logger=None
            )

        print(f"🎉 ¡Clip editado con éxito! Guardado en: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error durante la edición/renderizado del video: {e}", file=sys.stderr)
        return False

def create_subtitles_txt(transcript_data: list, start_time: float, end_time: float, output_txt_path: Path):
    """
    Filtra la transcripción original y genera un archivo .txt con las frases 
    y marcas de tiempo que corresponden estrictamente al fragmento del clip.
    """
    def format_time(seconds: float) -> str:
        """Helper para convertir segundos (ej. 75.5) a formato de reloj (01:15)"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    print(f"📄 Generando archivo de texto para subtítulos...")

    try:
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(f"=== SUBTÍTULOS DEL CLIP ({format_time(start_time)} - {format_time(end_time)}) ===\n\n")

            for segment in transcript_data:
                seg_start = segment.get("start", 0)
                seg_end = segment.get("end", 0)
                text = segment.get("text", "")

                # Verificamos si el segmento cae dentro del rango del clip
                if seg_start >= start_time and seg_end <= end_time:
                    # Calculamos el tiempo relativo desde el inicio del CLIP (para que empiece en 00:00)
                    relative_start = format_time(seg_start - start_time)
                    relative_end = format_time(seg_end - start_time)

                    f.write(f"[{relative_start} -> {relative_end}] {text}\n")

        print(f"✅ Archivo de subtítulos guardado en: {output_txt_path.name}")
        return True
    except Exception as e:
        print(f"❌ Error al crear el archivo de texto de subtítulos: {e}")
        return False