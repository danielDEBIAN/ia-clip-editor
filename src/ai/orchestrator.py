import json
import requests
import sys
from pathlib import Path

# Salvavidas de rutas para importar config
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import config

def analyze_transcript_for_clips(transcript_data: list) -> list: # 👈 Cambiado a plural y retorna list
    if not transcript_data:
        print("⚠️ No hay datos de transcripción para analizar.")
        return []

    print(f"🧠 Conectando con Ollama usando el modelo '{config.OLLAMA_MODEL}'...")

    prompt = """
Eres un editor de video experto en crear contenido viral para TikTok, Instagram Reels y YouTube Shorts.

Tu tarea es analizar la transcripción completa de un video y extraer entre 2 y 4 momentos distintos que tengan alto potencial de volverse viral.

Cada fragmento debe:
- Durar entre 15 y 60 segundos (ideal: 20-40s).
- Tener un **gancho fuerte en los primeros 3 segundos** (pregunta intrigante, sorpresa, emoción, declaración impactante).
- Mantener coherencia: debe poder verse sin contexto previo.
- Incluir un momento de **emoción, humor, sorpresa, revelación o cierre fuerte** (risa, giro, enseñanza rápida, llamada a acción).
- Evitar fragmentos aburridos, transiciones lentas o contenido sin energía.

[REGLAS CRÍTICAS]:
1. Encuentra múltiples fragmentos (mínimo 2, máximo 5 si el video es largo).
2. Cada fragmento debe ser continuo y abarcar varias líneas consecutivas (que dure entre 20 y 50 segundos cada uno).
3. Los fragmentos NO deben encimarse o solaparse entre sí.
4. El gancho debe estar claramente identificado en la primera parte del fragmento.
5. El análisis debe basarse en el texto y los timestamps de la transcripción, no inventar información adicional.

[REGLAS DE FORMATO]:
- Responde **ÚNICAMENTE** con un array JSON válido. Nada de texto extra, markdown o explicaciones.
- Usa este formato exacto:
[
  {{
    "inicio": <segundos_inicio>,
    "fin": <segundos_fin>,
    "gancho_detectado": "<texto_gancho>",
    "justificacion": "<explicacion_corta>"
  }},
  {{
    "inicio": <segundos_inicio>,
    "fin": <segundos_fin>,
    "gancho_detectado": "<texto_gancho>",
    "justificacion": "<explicacion_corta>"
  }}
]

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
        data_parseada = json.loads(raw_response)

        # --- PARCHE DE ROBUSTEZ MULTI-CLIP ---
        # Si la IA envolvió la lista en un diccionario (ej. {"clips": [...] o "fragmentos": [...]})
        if isinstance(data_parseada, dict):
            # Buscamos si alguna de las llaves internas contiene la lista de clips
            for key, value in data_parseada.items():
                if isinstance(value, list):
                    data_parseada = value
                    break

            # Si sigue siendo un diccionario y no encontramos listas internas, lo envolvemos en una lista
            if isinstance(data_parseada, dict):
                data_parseada = [data_parseada]
        # -------------------------------------

        print(f"\n✨ La IA ha procesado el contenido y definió {len(data_parseada)} corte(s).")
        return data_parseada

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar con Ollama.", file=sys.stderr)
        print("👉 Asegúrate de tener Ollama corriendo en segundo plano (`ollama serve`)", file=sys.stderr)
        print(f"👉 Y de haber descargado el modelo ejecutando: `ollama run {config.OLLAMA_MODEL}`", file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print("❌ Error: El LLM local no devolvió un formato JSON válido.", file=sys.stderr)
        print(f"Respuesta cruda de la IA: {raw_response}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al procesar la IA: {e}", file=sys.stderr)
        return []