# app.py
# Autor: [Randy Castillo]
# Matrícula: [21-EISN-2-007]

import gradio as gr
from scripts.analisis_emocional import extraer_emocion
from scripts.generador_muical import generar_musica

def interfaz_musical(entrada_usuario):
    emocion = extraer_emocion(entrada_usuario)
    if emocion is None:
        return "No se reconoció ninguna emoción clara. Intenta con: feliz, triste, ansioso...", None
    ruta_audio = generar_musica(emocion)
    return f"Emoción detectada: {emocion}", ruta_audio

with gr.Blocks() as demo:
    gr.Markdown("## 🎵 Generador de Música por Emociones 🎵")
    entrada = gr.Textbox(label="¿Cómo te sientes hoy?")
    salida_texto = gr.Textbox(label="Resultado")
    salida_audio = gr.Audio(label="Tu música generada", type="filepath")
    btn = gr.Button("Generar Música")

    btn.click(fn=interfaz_musical, inputs=entrada, outputs=[salida_texto, salida_audio])

if __name__ == "__main__":
    demo.launch()