# Analisis_Emocional
# Autor: [Randy Castillo ]
# Matrícula: [21-EISN-2-007]

from typing import Optional
import re

# Modelo de emociones base permitidas 
EMOCIONES_VALIDAS = {
    "feliz": "happy",
    "triste": "sad",
    "relajado": "relaxing",
    "ansioso": "tense",
    "enojado": "angry",
    "nostálgico": "nostalgic",
    "emocionado": "excited"
}

def extraer_emocion(texto_usuario: str) -> Optional[str]:
    texto = texto_usuario.lower()
    for esp, eng in EMOCIONES_VALIDAS.items():
        if re.search(rf"\b{esp}\b", texto):
            return eng
    return None