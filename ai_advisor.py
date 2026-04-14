"""
ai_advisor.py — Groq-powered AI financial advisor
"""
import os
import re
import json
import logging
from typing import Optional
from groq import Groq  # type: ignore
from dotenv import load_dotenv  # type: ignore
from market_data import KEYWORD_TO_TICKER  # type: ignore

load_dotenv()

logger = logging.getLogger(__name__)
MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
Actúa como un asesor financiero experto. {name_part}
El usuario ha respondido el Test de Perfil de Riesgo:

{qa_text}

TAREA: Analiza las respuestas y:
1. Clasifica al usuario como exactamente UNO de: Conservador, Moderado, o Agresivo
2. Explica brevemente por qué (2-3 oraciones, tono cálido y personalizado)
3. Da 2 recomendaciones de activos concretas y apropiadas para su perfil

Responde EXACTAMENTE en este formato JSON (sin markdown, solo JSON puro):
{{
  "profile": "Conservador|Moderado|Agresivo",
  "explanation": "Tu explicación aquí...",
  "recommendations": "Tus recomendaciones aquí..."
}}
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()
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

        prompt = f"""Eres Santi, un asesor financiero senior colombiano, cercano y experto. Tu misión es guiar al usuario como un mentor de confianza, no solo dar datos fríos. Hablas siempre en español latino, con un tono cálido y natural, como si estuvieras tomando un café con el usuario.

PERFIL DEL CLIENTE: {user_profile}
GUÍA DE PERFIL: {profile_guidance}

MENSAJE DEL USUARIO: "{user_message}"

{market_context}

REGLAS DE PERSONALIDAD (síguelas siempre):
1. EMPATÍA REAL: Si el usuario da un paso hacia invertir, aunque sea pequeño, reconócelo genuinamente. No de forma exagerada, sino natural.
2. CONTEXTO COLOMBIA: El usuario está en Colombia. De forma proactiva y natural menciona opciones locales relevantes como Trii, Tyba, Adagio o fondos de pensiones voluntarias cuando aplique. No esperes a que te pregunten.
3. SIN LISTAS ABURRIDAS: No uses listas de 5 puntos con asteriscos. Habla en párrafos fluidos. Usa frases como "Mira, lo que yo haría en tu lugar es...", "Esto es interesante porque...", "Te cuento algo que poca gente sabe...".
4. CONSEJOS CONCRETOS: Responde ESPECÍFICAMENTE lo que pregunta. Si menciona $100.000 COP, habla de esa cifra exacta y qué puede hacer con ella hoy.
5. HONESTIDAD DE AMIGO: Si un activo es volátil o riesgoso para su perfil, adviértele como un amigo: "Ojo, esto se mueve mucho, asegúrate de que sea solo una parte pequeña de tu plan."
6. PREGUNTA FINAL: Termina SIEMPRE con una pregunta corta que invite a seguir la conversación y a tomar acción. Ejemplos: "¿Te gustaría que simulemos cuánto crecerían esos $100.000 en un año?", "¿Quieres que exploremos cómo abrir una cuenta en Trii paso a paso?"
7. LONGITUD: Máximo 3-4 párrafos. Conciso pero sustancioso.

Termina siempre con: "⚠️ *Este análisis es educativo y no constituye asesoría financiera oficial.*"
"""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

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
    words = re.sub(r"[¿?¡!.,;:\"'()\n]", " ", message).split()
    lower_msg = message.lower()

    for keyword, ticker in KEYWORD_TO_TICKER.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', lower_msg):
            return ticker

    dollar_match = re.search(r"\$([A-Z]{1,5}(?:-USD)?)", message.upper())
    if dollar_match:
        return dollar_match.group(1)

    for word in words:
        clean = re.sub(r"[^A-Z]", "", word.upper())
        if 2 <= len(clean) <= 5 and clean not in STOP_WORDS:
            return clean

    return "UNKNOWN"


def extract_ticker_simple(message: str) -> str:
    return extract_ticker_from_message(message)
