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