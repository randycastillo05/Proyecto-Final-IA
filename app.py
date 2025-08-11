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
        print("⚠️ Advertencia: No se encontró el archivo styles.css")
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
                <h1>🎵 Recomendador Musical Inteligente</h1>
                <p>Descubre la canción perfecta para tu estado de ánimo actual</p>
            </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💭 Comparte cómo te sientes")
                entrada = gr.Textbox(
                    placeholder="Ej: Me siento nostálgico pensando en mi infancia...",
                    label="Describe tu estado de ánimo",
                    lines=3
                )
                btn_buscar = gr.Button("🔍 Encontrar Mi Canción", variant="primary")
        
        gr.Markdown("---")
        
        with gr.Row():
            with gr.Column(scale=2):
                salida_descripcion = gr.Markdown(label="")
            with gr.Column(scale=1):
                salida_enlace = gr.Textbox(label="🎵 Enlace en Deezer", interactive=False)
                salida_youtube = gr.HTML("")  # Aquí pondremos el botón YouTube dinámicamente
        
        with gr.Row():
            with gr.Column(scale=1):
                salida_imagen = gr.Image(label="", height=300)
            with gr.Column(scale=1):
                salida_audio = gr.Audio(label="Escucha 30 segundos", type="filepath")
        
        def mostrar_resultado(texto_usuario):
            descripcion, enlace_deezer, imagen, preview, link_youtube = recomendador.analizar_emocion_y_recomendar(texto_usuario)
            boton_youtube = f'<a href="{link_youtube}" target="_blank"><button style="padding:10px;background-color:red;color:white;border:none;border-radius:5px;cursor:pointer;">▶️ Ver en YouTube</button></a>' if link_youtube else ""
            return descripcion, enlace_deezer, imagen, preview, boton_youtube
        
        btn_buscar.click(
            fn=mostrar_resultado,
            inputs=entrada,
            outputs=[salida_descripcion, salida_enlace, salida_imagen, salida_audio, salida_youtube]
        )
        
        entrada.submit(
            fn=mostrar_resultado,
            inputs=entrada,
            outputs=[salida_descripcion, salida_enlace, salida_imagen, salida_audio, salida_youtube]
        )
    
    return demo

def main():
    demo = crear_interfaz()
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860, inbrowser=True)

if __name__ == "__main__":
    main()
