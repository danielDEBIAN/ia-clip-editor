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

    prompt = f"""
Eres un editor de video experto en Shorts y TikToks.
Tu tarea es analizar la siguiente transcripción completa y obligatoriamente extraer un listado con varios fragmentos distintos (busca al menos 2 o 3 momentos separados en el tiempo) de un video largo e identificar TODOS los momentos que sean interesantes, divertidos, coherentes o tengan potencial de ser un clip viral.

[REGLAS CRÍTICAS]:
1. Encuentra múltiples fragmentos (mínimo 2, máximo 5 si el video es largo).
2. Cada fragmento debe ser continuo y abarcar varias líneas consecutivas (que dure entre 20 y 50 segundos cada uno).
3. Los fragmentos NO deben encimarse o solaparse entre sí.

Debes responder **ÚNICAMENTE** con un array/lista de objetos JSON. No agregues introducciones ni formato markdown. Usa este formato estricto:
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
        return {}
    except json.JSONDecodeError:
        print("❌ Error: El LLM local no devolvió un formato JSON válido.", file=sys.stderr)
        print(f"Respuesta cruda de la IA: {raw_response}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al procesar la IA: {e}", file=sys.stderr)
        return {}