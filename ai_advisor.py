"""
ai_advisor.py — Gemini-powered AI financial advisor with improved ticker extraction,
                Risk Profile Test logic, and contextual financial advice.
"""
import os
import re
import logging
import json
from typing import Optional
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from dotenv import load_dotenv  # type: ignore
from market_data import KEYWORD_TO_TICKER  # type: ignore

load_dotenv()

logger = logging.getLogger(__name__)
MODEL_NAME = "gemini-2.0-flash"

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
    """Returns a risk test question by index (0-based)."""
    if 0 <= question_number < len(RISK_QUESTIONS):
        remaining = len(RISK_QUESTIONS) - question_number
        return RISK_QUESTIONS[question_number] + f"\n\n*Pregunta {question_number + 1} de {len(RISK_QUESTIONS)}*"
    return ""


def evaluate_risk_profile(answers: list[str], user_name: Optional[str] = None) -> dict:
    """
    Passes user answers to Gemini to classify profile and return advice.
    Returns: {"profile": str, "explanation": str, "recommendations": str}
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        qa_text = "\n".join([
            f"P{i+1}: {RISK_QUESTIONS[i].split(chr(10))[0]}\nR{i+1}: {answers[i]}"
            for i in range(min(len(answers), 5))
        ])
        name_part = f"El usuario se llama {user_name}." if user_name else ""

        prompt = f"""
Actúa como un asesor financiero experto. {name_part}
El usuario ha respondido el Test de Perfil de Riesgo:

{qa_text}

TAREA: Analiza las respuestas y:
1. Clasifica al usuario como exactamente UNO de: **Conservador**, **Moderado**, o **Agresivo**
2. Explica brevemente por qué (2-3 oraciones, tono cálido y personalizado)
3. Da 2 recomendaciones de activos concretas y apropiadas para su perfil

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
        )
        text = response.text.strip()

        # Parse JSON from response
        import json
        # Clean up possible markdown code blocks
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

def get_unified_analysis(user_message: str, user_profile: str, market_data: Optional[dict] = None) -> str:
    """
    Main chat endpoint: generates a financial advisor response using Gemini.
    """
    try:

        market_context = (
            f"Datos de mercado en tiempo real:\n"
            f"  - Activo: {market_data.get('name', 'N/A')}\n"
            f"  - Precio actual: ${market_data.get('price', 'N/A')}\n"
            f"  - Cambio hoy: {market_data.get('change', 'N/A')} ({market_data.get('change_percent', 'N/A')})\n"
            if market_data and "error" not in market_data
            else "No hay datos de mercado específicos para este mensaje."
        )

        profile_guidance = {
            "Conservador": "El usuario prefiere seguridad. Prioriza productos de bajo riesgo (bonos, ETFs diversificados, depósitos).",
            "Moderado": "El usuario busca equilibrio riesgo/retorno. Acciones blue-chip, ETFs mixtos son adecuados.",
            "Agresivo": "El usuario tolera alta volatilidad a cambio de mayores retornos. Acciones individuales, cripto, sectores de crecimiento.",
        }.get(user_profile, "Perfil Moderado.")

        prompt = f"""
Eres Investi, un asesor financiero experto, humano y ético. Hablas siempre en español.

PERFIL DEL CLIENTE: {user_profile}
GUÍA DE PERFIL: {profile_guidance}

MENSAJE DEL USUARIO: "{user_message}"

{market_context}

INSTRUCCIONES:
- Responde de forma natural, cálida y directa (máximo 4-5 párrafos)
- Si hay datos de mercado, analízalos brevemente en el contexto del perfil del usuario
- Si no hay datos específicos, da consejos generales de inversión relevantes al mensaje
- Usa negrita (**texto**) para destacar datos clave
- Termina SIEMPRE con: "⚠️ *Este análisis es educativo y no constituye asesoría financiera oficial.*"
"""
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text

    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return f"Lo siento, tuve un problema procesando tu consulta. Por favor intenta de nuevo. (Error: {str(e)})"


# ─── Ticker Extraction ──────────────────────────────────────────────────────────

# Common Spanish/English stop words to ignore
STOP_WORDS = {
    "HOY", "COMO", "ESTA", "ACCION", "RIESGO", "BAJO", "INVERTIR",
    "SECTORES", "PRECIO", "PARA", "QUE", "UNA", "LAS", "LOS", "DEL",
    "CON", "POR", "MAS", "SUS", "HAY", "SON", "CUAL", "ESTA",
    "DEBO", "PUEDO", "DEBERIA", "QUIERO", "HACER", "TIENE", "TIENE",
    "CUANTO", "VALE", "COTIZA", "MERCADO", "BOLSA", "MEJOR", "PEOR"
}


def extract_ticker_from_message(message: str) -> str:
    """
    Extracts a ticker symbol from a user message.
    Priority:
    1. Keyword mapping (e.g. "apple" → "AAPL", "bitcoin" → "BTC-USD")
    2. Explicit ticker patterns (e.g. $AAPL or all-caps 2–5 letter words)
    3. Returns "UNKNOWN" if nothing found
    """
    words = re.sub(r"[¿?¡!.,;:\"'()\n]", " ", message).split()
    lower_msg = message.lower()

    # 1. Check keyword map (longest match wins)
    for keyword, ticker in KEYWORD_TO_TICKER.items():
        if keyword in lower_msg:
            return ticker

    # 2. Check for $TICKER pattern
    dollar_match = re.search(r"\$([A-Z]{1,5}(?:-USD)?)", message.upper())
    if dollar_match:
        return dollar_match.group(1)

    # 3. Check for uppercase ticker words (2–5 letters, not stop words)
    for word in words:
        clean = re.sub(r"[^A-Z]", "", word.upper())
        if 2 <= len(clean) <= 5 and clean not in STOP_WORDS:
            return clean

    return "UNKNOWN"


# Keep backward-compatible alias
def extract_ticker_simple(message: str) -> str:
    return extract_ticker_from_message(message)