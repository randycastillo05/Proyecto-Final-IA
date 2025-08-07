# app.py
# Autor: [Randy Castillo]
# Matrícula: [21-EISN-2-007]

import gradio as gr
from scripts.analisis_emocional import extraer_emocion
from googleapiclient.discovery import build
import requests
YOUTUBE_API_KEY = "AIzaSyCwZZbnsUyonbP4e6M1NB6uHqxeaD-d5qE"

def buscar_cancion_por_emocion(texto_usuario):
    emocion = extraer_emocion(texto_usuario)
    if emocion is None:
        return "No se reconoció ninguna emoción clara.", None

    query = f"canción {emocion} emocional"
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&type=video&maxResults=1"

    response = requests.get(url)
    if response.status_code != 200:
        return "Error al acceder a la API de YouTube.", None

    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        video_id = data["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return f"Canción sugerida para la emoción '{emocion}'", video_url
    else:
        return "No se encontró ninguna canción.", None

with gr.Blocks() as demo:
    gr.Markdown("## 🎶 Buscador de Canciones por Emoción (YouTube)")
    entrada = gr.Textbox(label="¿Cómo te sientes hoy?")
    salida_texto = gr.Textbox(label="Resultado")
    salida_video = gr.Video(label="Video sugerido")

    btn = gr.Button("Buscar Canción")
    btn.click(fn=buscar_cancion_por_emocion, inputs=entrada, outputs=[salida_texto, salida_video])

if __name__ == "__main__":
    demo.launch(share=True)
