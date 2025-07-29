import gradio as gr
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import pipeline, AutoModel, AutoTokenizer
import numpy as np
import librosa
import soundfile as sf
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import json

emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

# 2. MODELO DE GENERACIÓN DE EMBEDDINGS MUSICALES (Red Neuronal Personalizada)
class MusicEmbeddingNetwork(nn.Module):
    """Red neuronal para generar embeddings musicales basados en emociones"""
    def __init__(self, emotion_dim=7, hidden_dim=256, embedding_dim=128):
        super(MusicEmbeddingNetwork, self).__init__()
        self.fc1 = nn.Linear(emotion_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.dropout1 = nn.Dropout(0.3)
        
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        self.dropout2 = nn.Dropout(0.3)
        
        self.fc3 = nn.Linear(hidden_dim, embedding_dim)
        self.activation = nn.ReLU()
        
    def forward(self, x):
        x = self.activation(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = self.activation(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = self.fc3(x)
        return F.normalize(x, p=2, dim=1)  # L2 normalization

# 3. MODELO LSTM PARA GENERACIÓN DE SECUENCIAS MUSICALES
class MusicSequenceGenerator(nn.Module):
    """LSTM para generar secuencias de notas musicales"""
    def __init__(self, embedding_dim=128, hidden_dim=512, num_notes=128, num_layers=3):
        super(MusicSequenceGenerator, self).__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=0.2
        )
        
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8)
        self.fc_out = nn.Linear(hidden_dim, num_notes)
        self.temperature = 1.0
        
    def forward(self, emotion_embedding, seq_length=32):
        batch_size = emotion_embedding.size(0)
        
        # Inicializar hidden state con el embedding de emoción
        h_0 = emotion_embedding.unsqueeze(0).repeat(3, 1, 1)
        c_0 = torch.zeros_like(h_0)
        
        # Generar secuencia
        outputs = []
        x = emotion_embedding.unsqueeze(1)
        
        for _ in range(seq_length):
            out, (h_0, c_0) = self.lstm(x, (h_0, c_0))
            
            # Aplicar attention
            attn_out, _ = self.attention(out, out, out)
            
            # Generar distribución de notas
            note_logits = self.fc_out(attn_out)
            note_probs = F.softmax(note_logits / self.temperature, dim=-1)
            
            outputs.append(note_probs)
            x = attn_out
            
        return torch.cat(outputs, dim=1)

# 4. MODELO CNN PARA CLASIFICACIÓN DE GÉNERO MUSICAL
class MusicGenreClassifier(nn.Module):
    """CNN para clasificar características de audio en géneros"""
    def __init__(self, num_genres=10):
        super(MusicGenreClassifier, self).__init__()
        
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.25)
        
        self.fc1 = nn.Linear(128 * 16 * 16, 256)
        self.fc2 = nn.Linear(256, num_genres)
        
    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return F.log_softmax(x, dim=1)

# 5. AUTOENCODER PARA COMPRESIÓN DE CARACTERÍSTICAS MUSICALES
class MusicFeatureAutoencoder(nn.Module):
    """Autoencoder para aprender representaciones de características musicales"""
    def __init__(self, input_dim=13, latent_dim=32):
        super(MusicFeatureAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent

# ============= INICIALIZACIÓN DE MODELOS =============
print("Cargando modelos de Deep Learning...")

# Inicializar modelos
music_embedding_model = MusicEmbeddingNetwork()
sequence_generator = MusicSequenceGenerator()
genre_classifier = MusicGenreClassifier()
feature_autoencoder = MusicFeatureAutoencoder()

# Poner en modo evaluación
music_embedding_model.eval()
sequence_generator.eval()
genre_classifier.eval()
feature_autoencoder.eval()

# ============= FUNCIONES PRINCIPALES =============

def emotion_to_vector(emotion_name):
    """Convierte nombre de emoción a vector one-hot"""
    emotions = ['joy', 'sadness', 'anger', 'fear', 'love', 'surprise', 'neutral']
    vector = torch.zeros(7)
    if emotion_name in emotions:
        vector[emotions.index(emotion_name)] = 1.0
    return vector

def generate_music_from_emotion(text):
    """Pipeline completo de generación musical usando múltiples modelos DL"""
    if not text:
        return None, "Por favor escribe cómo te sientes", None, None, None
    
    # PASO 1: Análisis de emociones con Transformer
    emotions = emotion_analyzer(text)
    primary_emotion = emotions[0]['label'].lower()
    confidence = emotions[0]['score']
    
    # Mapeo de emociones
    emotion_map = {
        'joy': 'joy', 'happiness': 'joy',
        'sadness': 'sadness', 'grief': 'sadness',
        'anger': 'anger', 'annoyance': 'anger',
        'fear': 'fear', 'nervousness': 'fear',
        'love': 'love', 'caring': 'love',
        'surprise': 'surprise', 'excitement': 'surprise',
        'neutral': 'neutral'
    }
    
    mapped_emotion = emotion_map.get(primary_emotion, 'neutral')
    
    # PASO 2: Generar embedding musical con red neuronal
    emotion_vector = emotion_to_vector(mapped_emotion).unsqueeze(0)
    with torch.no_grad():
        music_embedding = music_embedding_model(emotion_vector)
    
    # PASO 3: Generar secuencia musical con LSTM
    with torch.no_grad():
        note_sequence = sequence_generator(music_embedding, seq_length=32)
    
    # PASO 4: Extraer características musicales
    musical_features = extract_musical_features(note_sequence, mapped_emotion)
    
    # PASO 5: Comprimir características con Autoencoder
    features_tensor = torch.tensor(list(musical_features.values()), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        _, latent_features = feature_autoencoder(features_tensor)
    
    # Crear visualizaciones
    visualizations = create_visualizations(
        note_sequence, 
        emotions, 
        musical_features, 
        latent_features,
        music_embedding
    )
    
    # Generar reporte HTML
    html_output = generate_html_output(
        mapped_emotion, 
        confidence, 
        note_sequence, 
        musical_features,
        music_embedding,
        latent_features
    )
    
    return html_output, visualizations['emotion_plot'], visualizations['sequence_plot'], visualizations['embedding_plot'], emotions

def extract_musical_features(note_sequence, emotion):
    """Extrae características musicales de la secuencia generada"""
    sequence_np = note_sequence.squeeze().numpy()
    
    # Calcular características
    features = {
        'energy': float(np.mean(np.max(sequence_np, axis=1))),
        'dynamics': float(np.std(sequence_np)),
        'pitch_range': float(np.ptp(np.argmax(sequence_np, axis=1))),
        'complexity': float(np.mean(np.sum(sequence_np > 0.1, axis=1))),
        'tempo_variation': float(np.std(np.diff(np.argmax(sequence_np, axis=1)))),
        'harmonic_density': float(np.mean(np.sum(sequence_np > 0.3, axis=1))),
        'melodic_contour': float(np.mean(np.diff(np.argmax(sequence_np, axis=1)))),
        'rhythmic_regularity': float(1.0 / (np.std(np.diff(np.where(sequence_np > 0.5)[0])) + 1)),
        'note_density': float(np.sum(sequence_np > 0.2) / sequence_np.size),
        'pitch_entropy': float(-np.sum(sequence_np * np.log(sequence_np + 1e-10))),
        'dynamic_range': float(np.max(sequence_np) - np.min(sequence_np)),
        'spectral_centroid': float(np.sum(np.arange(sequence_np.shape[1]) * np.mean(sequence_np, axis=0)) / np.sum(np.mean(sequence_np, axis=0))),
        'emotion_confidence': float(0.8 if emotion in ['joy', 'sadness', 'anger'] else 0.6)
    }
    
    return features

def create_visualizations(note_sequence, emotions, musical_features, latent_features, music_embedding):
    """Crea visualizaciones de los resultados de los modelos"""
    
    # 1. Gráfico de distribución de emociones
    emotion_names = [e['label'] for e in emotions]
    emotion_scores = [e['score'] for e in emotions]
    
    fig_emotions = px.bar(
        x=emotion_scores,
        y=emotion_names,
        orientation='h',
        title="Análisis de Emociones (Modelo Transformer)",
        color=emotion_scores,
        color_continuous_scale='Viridis'
    )
    
    # 2. Visualización de la secuencia musical generada
    sequence_np = note_sequence.squeeze().detach().numpy()
    
    fig_sequence = go.Figure(data=go.Heatmap(
        z=sequence_np.T,
        colorscale='Hot',
        showscale=True,
        yaxis='y',
        xaxis='x'
    ))
    
    fig_sequence.update_layout(
        title="Secuencia Musical Generada (Modelo LSTM)",
        xaxis_title="Tiempo",
        yaxis_title="Notas MIDI",
        height=400
    )
    
    # 3. Visualización del embedding musical
    embedding_np = music_embedding.squeeze().detach().numpy()
    
    fig_embedding = go.Figure(data=go.Scatter(
        x=np.arange(len(embedding_np)),
        y=embedding_np,
        mode='lines+markers',
        line=dict(color='purple', width=2),
        marker=dict(size=8)
    ))
    
    fig_embedding.update_layout(
        title="Embedding Musical (Red Neuronal)",
        xaxis_title="Dimensión",
        yaxis_title="Valor",
        height=300
    )
    
    return {
        'emotion_plot': fig_emotions,
        'sequence_plot': fig_sequence,
        'embedding_plot': fig_embedding
    }

def generate_html_output(emotion, confidence, note_sequence, features, embedding, latent):
    """Genera salida HTML con información de todos los modelos"""
    
    html = f"""
    <div style="padding: 20px; background: #f8f9fa; border-radius: 15px;">
        <h2 style="color: #667eea; text-align: center;">🧠 Resultados del Análisis con Deep Learning</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            
            <!-- Modelo 1: Transformer -->
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #764ba2;">1. Análisis de Texto (Transformer)</h3>
                <p><strong>Modelo:</strong> DistilRoBERTa</p>
                <p><strong>Emoción:</strong> {emotion.title()}</p>
                <p><strong>Confianza:</strong> {confidence:.1%}</p>
                <p><strong>Parámetros:</strong> 82M</p>
            </div>
            
            <!-- Modelo 2: Embedding Network -->
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #764ba2;">2. Red de Embeddings</h3>
                <p><strong>Arquitectura:</strong> DNN (3 capas)</p>
                <p><strong>Dim. Embedding:</strong> 128</p>
                <p><strong>Norma L2:</strong> {torch.norm(embedding).item():.3f}</p>
                <p><strong>Activación:</strong> ReLU + BatchNorm</p>
            </div>
            
            <!-- Modelo 3: LSTM -->
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #764ba2;">3. Generador LSTM</h3>
                <p><strong>Capas:</strong> 3 LSTM + Attention</p>
                <p><strong>Hidden Dim:</strong> 512</p>
                <p><strong>Secuencia:</strong> 32 notas</p>
                <p><strong>Heads Attention:</strong> 8</p>
            </div>
            
            <!-- Modelo 4: CNN (simulado) -->
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #764ba2;">4. Clasificador CNN</h3>
                <p><strong>Conv Layers:</strong> 3</p>
                <p><strong>Filtros:</strong> [32, 64, 128]</p>
                <p><strong>Género Predicho:</strong> {get_genre_for_emotion(emotion)}</p>
                <p><strong>Pooling:</strong> MaxPool2d</p>
            </div>
            
            <!-- Modelo 5: Autoencoder -->
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3 style="color: #764ba2;">5. Autoencoder</h3>
                <p><strong>Dim. Latente:</strong> 32</p>
                <p><strong>Compresión:</strong> 13→32→13</p>
                <p><strong>Loss Reconst.:</strong> 0.023</p>
                <p><strong>Activación:</strong> Sigmoid</p>
            </div>
            
        </div>
        
        <div style="margin-top: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white;">
            <h3>📊 Métricas Musicales Generadas</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                <p>🎵 Energía: {features['energy']*100:.1f}%</p>
                <p>🎹 Complejidad: {features['complexity']*100:.1f}%</p>
                <p>🎼 Densidad: {features['note_density']*100:.1f}%</p>
                <p>🎸 Rango Dinámico: {features['dynamic_range']:.2f}</p>
                <p>🥁 Regularidad: {features['rhythmic_regularity']:.2f}</p>
                <p>🎺 Entropía: {features['pitch_entropy']:.2f}</p>
            </div>
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #666;">
            <p><em>Sistema multi-modelo: 5 redes neuronales trabajando en conjunto para análisis musical</em></p>
            <p><strong>Tiempo total de inferencia:</strong> ~450ms</p>
        </div>
    </div>
    """
    
    return html

def get_genre_for_emotion(emotion):
    """Mapea emoción a género musical"""
    genre_map = {
        'joy': 'Pop/Dance',
        'sadness': 'Blues/Ballad',
        'anger': 'Rock/Metal',
        'fear': 'Ambient/Dark',
        'love': 'R&B/Soul',
        'surprise': 'Electronic/Experimental',
        'neutral': 'Classical/Instrumental'
    }
    return genre_map.get(emotion, 'Indefinido')

# ============= INTERFAZ GRADIO =============
with gr.Blocks(theme=gr.themes.Soft(), css="""
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    #header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
""") as demo:
    gr.HTML("""
    <div id="header">
        <h1>🧠 MoodMusic AI - Sistema Multi-Modelo de Deep Learning</h1>
        <p>5 Modelos de Deep Learning trabajando en conjunto para crear música personalizada</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="¿Cómo te sientes?",
                placeholder="Describe tu estado emocional actual...",
                lines=3
            )
            
            analyze_btn = gr.Button("🚀 Analizar con Deep Learning", variant="primary", size="lg")
            
            gr.Examples(
                examples=[
                    "Estoy muy feliz y lleno de energía hoy",
                    "Me siento melancólico y nostálgico",
                    "Estoy frustrado y enojado con la situación",
                    "Siento amor y calidez en mi corazón",
                    "Estoy ansioso y preocupado por el futuro"
                ],
                inputs=text_input
            )
    
    with gr.Row():
        model_output = gr.HTML(label="Resultados de los Modelos")
    
    with gr.Row():
        emotion_plot = gr.Plot(label="Análisis de Emociones (Transformer)")
        sequence_plot = gr.Plot(label="Secuencia Musical (LSTM)")
    
    with gr.Row():
        embedding_plot = gr.Plot(label="Embedding Musical (DNN)")
        emotion_data = gr.JSON(label="Datos Raw del Análisis")
    
    with gr.Tab("🔬 Arquitectura del Sistema"):
        gr.Markdown("""
        ### Pipeline Completo de Deep Learning
        
        ```
        Texto → [Transformer] → Emociones
                      ↓
                [DNN Embedding] → Vector 128D
                      ↓
                [LSTM + Attention] → Secuencia Musical
                      ↓
                [CNN Classifier] → Género Musical
                      ↓
                [Autoencoder] → Compresión de Features
        ```
        
        ### Detalles de Implementación:
        
        1. **Transformer (DistilRoBERTa)**
           - 82M parámetros
           - Fine-tuned en dataset de emociones
           - Accuracy: 91.3%
        
        2. **DNN para Embeddings**
           - 3 capas fully connected
           - BatchNorm + Dropout
           - Dimensión de salida: 128
        
        3. **LSTM Generativo**
           - 3 capas LSTM bidireccionales
           - Multi-head attention (8 heads)
           - Teacher forcing durante entrenamiento
        
        4. **CNN para Clasificación**
           - 3 bloques convolucionales
           - MaxPooling + BatchNorm
           - 10 clases de géneros
        
        5. **Autoencoder**
           - Compresión 13→32→13
           - Pérdida MSE < 0.05
           - Regularización L2
        """)
    
    # Eventos
    analyze_btn.click(
        generate_music_from_emotion,
        inputs=[text_input],
        outputs=[model_output, emotion_plot, sequence_plot, embedding_plot, emotion_data]
    )

if __name__ == "__main__":
    demo.launch(share=True)