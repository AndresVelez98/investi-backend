"""
ai_advisor.py — Google Gemini 1.5 Flash powered AI financial advisor
"""
import os
import re
import json
import logging
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv  # type: ignore
from market_data import KEYWORD_TO_TICKER  # type: ignore

load_dotenv()

logger = logging.getLogger(__name__)
MODEL_NAME = "gemini-3-flash-preview"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ─── Risk Test Questions ────────────────────────────────────────────────────────

RISK_QUESTIONS = [
    "1️⃣ **¿Cuál es tu objetivo principal al invertir?**\n"
    "   a) Conservar mi dinero y protegerme de la inflación\n"
    "   b) Crecer moderadamente con riesgo controlado\n"
    "   c) Maximizar el crecimiento aunque implique alta volatilidad",

    "2️⃣ **Si tu inversión cayera un 20% en un mes, ¿qué harías?**\n"
    "   a) Vendería todo para evitar más pérdidas\n"
    "   b) Esperaría a que se recupere sin hacer nada\n"
    "   c) Compraría más, es una oportunidad de precio bajo",

    "3️⃣ **¿Cuánto tiempo planeas mantener tu inversión?**\n"
    "   a) Menos de 1 año\n"
    "   b) Entre 1 y 5 años\n"
    "   c) Más de 5 años",

    "4️⃣ **¿Con qué porcentaje de tus ahorros estás dispuesto a asumir riesgo?**\n"
    "   a) Menos del 20%\n"
    "   b) Entre el 20% y el 50%\n"
    "   c) Más del 50%, busco retornos altos",

    "5️⃣ **¿Cuál de estas frases describe mejor tu situación financiera?**\n"
    "   a) Tengo ingresos fijos y no puedo permitirme grandes pérdidas\n"
    "   b) Tengo estabilidad pero quiero hacer crecer mi patrimonio\n"
    "   c) Tengo ingresos variables y alta tolerancia a la incertidumbre",
]


def get_risk_question(question_number: int) -> str:
    if 0 <= question_number < len(RISK_QUESTIONS):
        return RISK_QUESTIONS[question_number] + f"\n\n*Pregunta {question_number + 1} de {len(RISK_QUESTIONS)}*"
    return ""


def evaluate_risk_profile(answers: list[str], user_name: Optional[str] = None) -> dict:
    try:
        qa_text = "\n".join([
            f"P{i+1}: {RISK_QUESTIONS[i].split(chr(10))[0]}\nR{i+1}: {answers[i]}"
            for i in range(min(len(answers), 5))
        ])
        name_part = f"El usuario se llama {user_name}." if user_name else ""

        prompt = f"""
Eres Santi, un asesor financiero cercano y experto. {name_part}
El usuario acaba de terminar el Test de Perfil de Riesgo:

{qa_text}

TAREA:
1. Clasifica al usuario como exactamente UNO de: Conservador, Moderado, o Agresivo
2. Explica el resultado de forma cálida y personalizada (2-3 oraciones), como si le hablaras de frente
3. Da 2 recomendaciones de activos concretas para su perfil, considerando que está en Colombia

Responde EXACTAMENTE en este formato JSON (sin markdown, solo JSON puro):
{{
  "profile": "Conservador|Moderado|Agresivo",
  "explanation": "Tu explicación aquí...",
  "recommendations": "Tus recomendaciones aquí..."
}}
"""
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        text = response.text.strip()
        text = re.sub(r"```json|```", "", text).strip()
        data = json.loads(text)

        return {
            "profile": data.get("profile", "Moderado"),
            "explanation": data.get("explanation", ""),
            "recommendations": data.get("recommendations", ""),
        }

    except Exception as e:
        logger.error(f"Risk test evaluation error: {e}")
        return {
            "profile": "Moderado",
            "explanation": "No pudimos procesar tu test completamente, pero te asignamos un perfil Moderado por defecto.",
            "recommendations": "Considera ETFs diversificados como SPY o QQQ como punto de partida.",
        }


# ─── Unified Chat Analysis ──────────────────────────────────────────────────────

def get_unified_analysis(
    user_message: str,
    user_profile: str,
    market_data: Optional[dict] = None,
    history: Optional[list] = None,
) -> str:
    try:
        market_context = (
            f"\n[DATOS EN TIEMPO REAL] {market_data.get('name')} ({market_data.get('ticker','')}): "
            f"${market_data.get('price')} USD · Cambio: {market_data.get('change')} ({market_data.get('change_percent')})\n"
            if market_data and "error" not in market_data
            else ""
        )

        profile_guidance = {
            "Conservador": "prefiere seguridad y capital protegido. CDTs, bonos, ETFs diversificados.",
            "Moderado": "busca balance riesgo/retorno. Acciones blue-chip, ETFs mixtos, fondos de inversión.",
            "Agresivo": "acepta alta volatilidad por mayor retorno. Acciones, cripto, sectores emergentes.",
        }.get(user_profile, "busca balance riesgo/retorno.")

        system_prompt = f"""Eres Santi, asesor financiero senior colombiano. Directo, cercano, como un colega experto — no un manual.

PERFIL: {user_profile} — el usuario {profile_guidance}{market_context}
REGLAS GENERALES:
- NUNCA abras con: "Me alegra", "¡Qué buena decisión!", "Es un gran paso", "Por supuesto", "Claro que sí", "Con gusto". Ve al punto.
- TONO DINÁMICO: pregunta técnica → responde como analista (breve, numérico). Duda emocional → responde como mentor (empático, práctico).
- SIN PAREDES DE TEXTO: máximo 3 párrafos cortos. Separa con línea en blanco. Negritas solo para cifras y activos clave.
- COLOMBIA SIEMPRE: menciona Trii, Tyba o XTB Colombia cuando sea útil, pero no repitas lo que ya explicaste antes.
- MONTOS EN COP: si el usuario menciona USD, convierte a COP (TRM ~$4.350). Usa formato: $100.000 COP.
- CIERRE: termina con UNA pregunta concreta que invite a actuar. Varía la pregunta cada vez.
- DISCLAIMER: última línea siempre: "⚠️ *Este análisis es educativo y no constituye asesoría financiera oficial.*"

REGLAS DE SALUDO Y CONTEXTO:
- Si el usuario solo saluda ("hola", "buenos días", "¿cómo estás?") responde brevemente y amigablemente SIN analizar ningún activo ni mostrar datos de mercado. Solo preséntate y pregunta en qué puedes ayudar.
- NO analices activos a menos que el usuario los mencione explícitamente (nombre, ticker o intención clara de análisis).
- COMPLETA SIEMPRE tus oraciones y párrafos. Nunca cortes una respuesta a la mitad. Si el análisis es largo, resume en lugar de truncar.
"""

        # Build conversation contents for Gemini
        # Gemini uses "user" and "model" roles (not "assistant")
        contents = []
        if history:
            for msg in history[-8:]:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append(
                    types.Content(role=role, parts=[types.Part(text=msg["content"])])
                )
        contents.append(
            types.Content(role="user", parts=[types.Part(text=user_message)])
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.75,
                max_output_tokens=2048,
            ),
        )
        return response.text

    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return f"Lo siento, tuve un problema procesando tu consulta. Por favor intenta de nuevo. (Error: {str(e)})"


# ─── Ticker Extraction ──────────────────────────────────────────────────────────

STOP_WORDS = {
    "HOY", "COMO", "ESTA", "ACCION", "RIESGO", "BAJO", "INVERTIR",
    "SECTORES", "PRECIO", "PARA", "QUE", "UNA", "LAS", "LOS", "DEL",
    "CON", "POR", "MAS", "SUS", "HAY", "SON", "CUAL", "ESTA",
    "DEBO", "PUEDO", "DEBERIA", "QUIERO", "HACER", "TIENE", "TIENE",
    "CUANTO", "VALE", "COTIZA", "MERCADO", "BOLSA", "MEJOR", "PEOR"
}


def extract_ticker_from_message(message: str) -> str:
    lower_msg = message.lower()

    # 1. Match known keywords (bitcoin, apple, tesla, etc.)
    for keyword, ticker in KEYWORD_TO_TICKER.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', lower_msg):
            return ticker

    # 2. Explicit $TICKER notation (e.g. $AAPL, $BTC-USD)
    dollar_match = re.search(r"\$([A-Z]{1,5}(?:-USD)?)", message.upper())
    if dollar_match:
        return dollar_match.group(1)

    # NOTE: Removed generic word fallback — it caused false positives on
    # greetings and common words (e.g. "Hola" → "HOLA" as ticker).
    return "UNKNOWN"


def extract_ticker_simple(message: str) -> str:
    return extract_ticker_from_message(message)
