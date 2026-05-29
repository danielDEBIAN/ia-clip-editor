import json
import requests
import sys
from pathlib import Path

# Salvavidas de rutas para importar config
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import config

def analyze_transcript_for_clip(transcript_data: list) -> dict:
    """
    Envía la transcripción a Ollama para que el LLM local analice el contenido
    y devuelva los timestamps de inicio y fin del mejor fragmento en formato JSON.
    """
    if not transcript_data:
        print("⚠️ No hay datos de transcripción para analizar.")
        return {}

    print(f"🧠 Conectando con Ollama usando el modelo '{config.OLLAMA_MODEL}'...")

    # Creamos el prompt del sistema estructurado
    prompt = f"""
Eres un editor de video experto en Shorts y TikToks. 
Tu tarea es analizar la siguiente transcripción, identificar el momento más interesante y seleccionar un fragmento continuo que dure entre 20 y 45 segundos en total. 

[REGLA CRÍTICA]: El fragmento DEBE incluir al menos 8 líneas consecutivas de la transcripción. NO elijas solo 2 o 3 líneas. La diferencia entre 'fin' e 'inicio' debe ser obligatoriamente mayor a 20.

Devuelve un objeto JSON con este formato exacto:
{{
  "inicio": <segundos_primera_linea>,
  "fin": <segundos_ultima_linea>,
  "gancho_detectado": "<texto_gancho>",
  "justificacion": "<explicacion_corta>"
}}

Transcripción:
{json.dumps(transcript_data, ensure_ascii=False, indent=2)}
"""

    # Configuración del payload para la API de Ollama
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  # Queremos la respuesta completa de un solo golpe
        "format": "json", # 👈 ESTO OBLIGA A OLLAMA A DEVOLVER SOLO JSON VÁLIDO
        "options": {
            "temperature": 0.2,   # Temperatura baja para mayor precisión
            "num_predict": 1024,  # 👈 Aumenta el límite de tokens de salida para que no se corte
            "num_ctx": 4096       # Aumenta el contexto para que lea bien la transcripción
        }
    }

    try:
        response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()

        raw_response = response.json().get("response", "").strip()

        # ---- PARCHE DE SEGURIDAD DEFINITIVO PARA JSON ----
        # 1. Eliminar bloques de código markdown si el modelo los metió
        if "```" in raw_response:
            raw_response = raw_response.split("```")[1]
            if raw_response.startswith("json"):
                raw_response = raw_response.replace("json", "", 1)

        # 2. Reemplazar espacios invisibles (\xa0) y normalizar caracteres problemáticos
        raw_response = raw_response.replace("\xa0", " ").replace("…", "...").strip()

        # 3. Intentar encontrar el inicio y fin de las llaves exactas
        start_idx = raw_response.find("{")
        end_idx = raw_response.rfind("}")
        if start_idx != -1 and end_idx != -1:
            raw_response = raw_response[start_idx:end_idx + 1]

        # Parseamos la respuesta limpia
        clip_decision = json.loads(raw_response)
        # ----------------------------------------------------

        print("\n✨ La IA ha tomado una decisión sobre el mejor clip:")
        print(f"⏱️  Corte: {clip_decision.get('inicio')}s -> {clip_decision.get('fin')}s")
        print(f"💡 Razón: {clip_decision.get('justificacion')}\n")

        return clip_decision

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar con Ollama.", file=sys.stderr)
        print("👉 Asegúrate de tener Ollama corriendo en segundo plano (`ollama serve`)", file=sys.stderr)
        print(f"👉 Y de haber descargado el modelo ejecutando: `ollama run {config.OLLAMA_MODEL}`", file=sys.stderr)
        return {}
    except json.JSONDecodeError:
        print("❌ Error: El LLM local no devolvió un formato JSON válido.", file=sys.stderr)
        print(f"Respuesta cruda de la IA: {raw_response}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al procesar la IA: {e}", file=sys.stderr)
        return {}