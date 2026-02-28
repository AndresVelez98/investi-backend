from ai_advisor import extract_ticker_from_message
import re

# Mock the logic found in main.py to see full flow
def test_full_flow(message: str):
    print(f"\n--- Testing: '{message}' ---")
    
    # Logic from main.py
    clean_msg = re.sub(r'[¿?¡!.,]', '', message).strip()
    print(f"Cleaned message: '{clean_msg}'")
    
    try:
        ticker = extract_ticker_from_message(clean_msg)
        print(f"Extracted ticker (from Module): '{ticker}'")
    except Exception as e:
        print(f"Module extraction failed: {e}")
        ticker = None

    palabras_ruido = ["hoy", "ahora", "precio", "de", "la", "accion", "como", "esta"]
    
    # Logic from main.py
    if not ticker or ticker == "UNKNOWN" or ticker.lower() in palabras_ruido:
        print("Falling back to manual logic in main.py...")
        palabras = clean_msg.lower().split()
        filtradas = [p for p in palabras if p not in palabras_ruido]
        ticker = filtradas[-1] if filtradas else clean_msg
        print(f"Final Ticker (Manual Fallback): '{ticker}'")
    else:
        print(f"Final Ticker (AI): '{ticker}'")

if __name__ == "__main__":
    test_full_flow("como esta la acción de tesla hoy")
    test_full_flow("como esta la acción de tesla")
    test_full_flow("precio de bitcoin ahora")
