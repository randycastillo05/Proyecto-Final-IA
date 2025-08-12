# 🎵 Recomendador Musical Inteligente

## Nombre Randy Castillo

## Matrícula 21-EISN-2-007



Este proyecto es una aplicación web que **analiza las emociones del usuario y recomienda una canción perfecta para su estado de ánimo**, pudiendo también filtrar por **artista** si lo mencionas.  
Utiliza **OpenAI** para el análisis de emociones y la selección de canciones, y **YouTube API** para mostrar el video recomendado.

---

## ✨ Características

- **Análisis emocional** usando IA de OpenAI.
- **Detección automática** de:
  - Emoción principal.
  - Artista (si el usuario lo menciona).
  - Género musical.
- **Recomendación precisa** de una canción que encaje con la emoción y/o artista.
- **Miniatura y enlace directo** al video en YouTube.
- **Interfaz amigable** construida con Gradio y CSS personalizado.
- Soporte para entradas como:
  - `"Quiero una canción triste de Eladio Carrión"`
  - `"Necesito música motivadora para entrenar"`
  - `"Ponme algo romántico de Shakira"`

---

## 📂 Estructura del proyecto

```
.
├── scripts/
│   └── analisis_emocional.py  # Lógica del análisis y recomendación
├── app.py                     # Interfaz principal en Gradio
├── styles.css                 # Estilos personalizados
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Variables de entorno (API Keys)
└── README.md                  # Documentación del proyecto
```

---

## ⚙️ Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/randycastillo05/Proyecto-Final-IA.git
   cd recomendador-musical
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las API Keys** en un archivo `.env`:
   ```env
   OPENAI_API_KEY=tu_api_key_de_openai
   YOUTUBE_API_KEY=tu_api_key_de_youtube
   ```

---

## 🚀 Ejecución

Inicia la aplicación con:

```bash
python app.py
```

La aplicación se abrirá automáticamente en tu navegador y también generará un enlace público para compartir.

---

## 🛠 Tecnologías usadas

- **Python 3.10+**
- **Gradio** → Interfaz web.
- **OpenAI GPT-4o-mini** → Análisis emocional y recomendación.
- **YouTube Data API v3** → Búsqueda de videos.
- **CSS personalizado** → Estilo visual.

---

## 📌 Ejemplos de uso

- **Entrada**: `"Quiero una canción feliz de Bad Bunny"`
- **Salida**:  
  - Descripción de la canción recomendada.
  - Miniatura del video.
  - Botón "Ver en YouTube".

---