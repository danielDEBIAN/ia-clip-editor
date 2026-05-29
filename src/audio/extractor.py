import subprocess
from pathlib import Path
import sys

def extract_audio(video_path: Path, output_audio_path: Path) -> bool:
    """
    Extrae el audio de un archivo de video y lo guarda como un archivo .wav 
    utilizando FFmpeg de forma directa y eficiente.
    """
    if not video_path.exists():
        print(f"❌ Error: El video no existe en la ruta: {video_path}")
        return False

    print(f"🎬 Extrayendo audio de: {video_path.name}...")

    # Comando FFmpeg optimizado: 
    # -vn: Desactiva el video.
    # -acodec pcm_s16le: Códec de audio sin compresión ideal para modelos de voz.
    # -ar 16000: Convierte a 16kHz (la frecuencia exacta que Whisper prefiere).
    # -ac 1: Convierte a canal Mono (reduce espacio y facilita análisis).
    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path),
        "-y" # Sobrescribe el archivo si ya existe
    ]

    try:
        # Ejecutamos el comando ocultando la salida masiva de logs de ffmpeg a menos que falle
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"🎵 Audio extraído exitosamente en: {output_audio_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar FFmpeg: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("❌ Error: FFmpeg no está instalado en tu sistema. Asegúrate de tenerlo en tu PATH.", file=sys.stderr)
        return False
