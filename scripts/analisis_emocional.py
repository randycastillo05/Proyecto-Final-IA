# Analisis_Emocional
# Autor: [Randy Castillo ]
# Matrícula: [21-EISN-2-007]

from typing import Optional
import re
import certifi
import httpx
client = httpx.AsyncClient(verify=certifi.where())

## scripts/analisis_emocional.py
EMOCIONES_VALIDAS = {
    "feliz": "happy",
    "triste": "sad",
    "relajado": "relaxing",
    "ansioso": "tense",
    "enojado": "angry",
    "nostálgico": "nostalgic",
    "emocionado": "excited"
}

def extraer_emocion(texto_usuario: str):
    texto = texto_usuario.lower()
    for esp, eng in EMOCIONES_VALIDAS.items():
        if esp in texto:
            return eng
    return None