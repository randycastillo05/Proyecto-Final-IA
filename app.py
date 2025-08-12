import gradio as gr
import os
from scripts.analisis_emocional import crear_recomendador

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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"
)

def cargar_css():
    try:
        with open('styles.css', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(" Advertencia: No se encontró el archivo styles.css")
        return ""

def crear_interfaz():
    recomendador = crear_recomendador(OPENAI_API_KEY)
    css_personalizado = cargar_css()

    with gr.Blocks(
        css=css_personalizado,
        theme=gr.themes.Soft(),
        title="🎵 Recomendador Musical Inteligente"
    ) as demo:

        gr.HTML("""
            <div class="header-container">
                <h1>Recomendador Musical Inteligente</h1>
                <p>Descubre la canción perfecta para tu estado de ánimo</p>
            </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Comparte cómo te sientes (puedes mencionar artista o género)")
                entrada = gr.Textbox(
                    placeholder="Ej: Quiero una salsa feliz de Marc Anthony...",
                    label="Describe tu estado de ánimo",
                    lines=3
                )
                btn_buscar = gr.Button("Encontrar Mi Canción", variant="primary")

        gr.Markdown("---")

        with gr.Row():
            with gr.Column(scale=2):
                salida_descripcion = gr.Markdown(label="")
            with gr.Column(scale=1):
                salida_youtube = gr.HTML("")  # Botón YouTube

        with gr.Row():
            with gr.Column(scale=1):
                salida_imagen = gr.Image(label="", height=300)
            with gr.Column(scale=1):
                salida_audio = gr.Audio(label="Escucha 30 segundos", type="filepath")

        def mostrar_resultado(texto_usuario):
            descripcion, enlace_youtube, imagen, preview, _ = recomendador.analizar_emocion_y_recomendar(texto_usuario)
            boton_youtube = f'<a href="{enlace_youtube}" target="_blank"><button class="youtube-button"> Ver en YouTube</button></a>' if enlace_youtube else ""
            return descripcion, boton_youtube, imagen, preview

        btn_buscar.click(
            fn=mostrar_resultado,
            inputs=entrada,
            outputs=[salida_descripcion, salida_youtube, salida_imagen, salida_audio]
        )

        entrada.submit(
            fn=mostrar_resultado,
            inputs=entrada,
            outputs=[salida_descripcion, salida_youtube, salida_imagen, salida_audio]
        )

    return demo

def main():
    demo = crear_interfaz()
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860, inbrowser=True)

if __name__ == "__main__":
    main()