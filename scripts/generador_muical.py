# generador_musical
# Autor: [Randy Castillo]
# Matrícula: [21-EISN-2-007]

import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

# Cargar modelo una vez
musicgen = MusicGen.get_pretrained('facebook/musicgen-small')
musicgen.set_generation_params(duration=10)  # duración de la música (segundos)

def generar_musica(descripcion: str, nombre_archivo: str = "musica_emocion") -> str:
    print(f"Generando música para: {descripcion}")
    wav = musicgen.generate([descripcion])
    ruta = f"outputs/{nombre_archivo}"
    audio_write(ruta, wav[0].cpu(), musicgen.sample_rate, strategy="loudness")
    return ruta + ".wav"