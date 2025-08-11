# Analisis_Emocional
# Autor: [Randy Castillo ]
# Matrícula: [21-EISN-2-007]

from openai import OpenAI
import json
import requests
import os

class RecomendadorMusical:
    """Clase para manejar recomendaciones musicales basadas en IA"""
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.modelo = "gpt-4o-mini"
    
    def analizar_emocion_y_recomendar(self, texto_usuario):
        if not texto_usuario.strip():
            return "Por favor, comparte cómo te sientes...", None, None, None, None

        prompt = self._crear_prompt(texto_usuario)
        
        try:
            datos_cancion = self._obtener_recomendacion_ia(prompt)
            
            if not datos_cancion:
                return "Error: No se pudo generar una recomendación válida", None, None, None, None
            
            descripcion = self._crear_descripcion(datos_cancion)
            
            # Buscar información en Deezer
            enlace, imagen, preview = self._buscar_deezer(
                datos_cancion["titulo"], 
                datos_cancion.get("artista"), 
                datos_cancion.get("genero")
            )

            # Crear enlace de YouTube
            link_youtube = self._crear_link_youtube(
                datos_cancion["titulo"], 
                datos_cancion.get("artista")
            )
            
            if not enlace:
                descripcion += "\n\n⚠️ *No se encontró en Deezer, pero puedes buscarla en Spotify, YouTube Music u otras plataformas*"

            return descripcion, enlace, imagen, preview, link_youtube

        except Exception as e:
            return f"Error generando recomendación: {str(e)}", None, None, None, None
    
    def _crear_prompt(self, texto_usuario):
        return f"""
        El usuario dice: "{texto_usuario}".
        
        Analiza la emoción del usuario y recomienda UNA canción que encaje perfectamente con su estado de ánimo.
        
        Devuelve SOLO un JSON válido con este formato exacto:
        {{
            "titulo": "nombre exacto de la canción",
            "artista": "nombre exacto del artista principal",
            "emocion_detectada": "emoción principal detectada",
            "razon": "breve explicación de por qué esta canción encaja",
            "genero": "género musical de la canción"
        }}
        
        Guía de emociones y géneros:
        - Tristeza/Melancolía: baladas, indie folk, música introspectiva
        - Felicidad/Alegría: pop alegre, reggae, música upbeat
        - Energía/Motivación: rock, electronic, hip hop energético  
        - Relajación/Calma: jazz suave, ambient, chill-out
        - Nostalgia: clásicos, oldies, música de épocas pasadas
        - Amor/Romance: baladas románticas, R&B, pop romántico
        - Ansiedad/Estrés: música calmante, new age, instrumental
        - Ira/Frustración: rock pesado, metal, punk
        - Soledad: indie, folk, singer-songwriter
        
        Elige canciones conocidas y populares para mejor disponibilidad en Deezer.
        Prioriza canciones en español e inglés.
        """
    
    def _obtener_recomendacion_ia(self, prompt):
        try:
            respuesta = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto musicólogo que recomienda canciones basándose en análisis emocional. Responde SOLO con JSON válido."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )

            contenido = respuesta.choices[0].message.content.strip()
            
            if contenido.startswith("```json"):
                contenido = contenido.replace("```json", "").replace("```", "").strip()
            
            datos = json.loads(contenido)
            
            campos_requeridos = ["titulo", "artista", "emocion_detectada", "razon"]
            if all(campo in datos and datos[campo].strip() for campo in campos_requeridos):
                return datos
            else:
                print("Error: Campos faltantes en la respuesta de IA")
                return None
                
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return None
        except Exception as e:
            print(f"Error con OpenAI API: {e}")
            return None
    
    def _crear_descripcion(self, datos_cancion):
        titulo = datos_cancion.get("titulo", "")
        artista = datos_cancion.get("artista", "")
        emocion = datos_cancion.get("emocion_detectada", "")
        razon = datos_cancion.get("razon", "")
        genero = datos_cancion.get("genero", "")
        
        descripcion = f"""
        ## 🎵 **{titulo}**
        **Artista:** {artista}
        """
        
        if genero:
            descripcion += f"\n**Género:** {genero}"
        
        descripcion += f"""
        
        **Emoción detectada:** {emocion}
        
        **¿Por qué esta canción?**  
        {razon}
        """
        
        return descripcion
    
    def _buscar_deezer(self, titulo, artista=None, genero=None):
        query = f'track:"{titulo}"'
        if artista:
            query += f' artist:"{artista}"'
        if genero:
            query += f' genre:"{genero}"'

        url = f"https://api.deezer.com/search?q={requests.utils.quote(query)}"
        
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None, None, None

            data = resp.json()
            if not data.get("data"):
                return None, None, None

            track = data["data"][0]
            enlace = track.get("link")
            imagen = track.get("album", {}).get("cover_xl")
            preview = track.get("preview")

            return enlace, imagen, preview
            
        except Exception as e:
            print(f"Error buscando en Deezer: {e}")
            return None, None, None
    
    def _crear_link_youtube(self, titulo, artista):
        query = f"{titulo} {artista}" if artista else titulo
        return f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"

def crear_recomendador(api_key):
    return RecomendadorMusical(api_key)

if __name__ == "__main__":
    API_KEY = input("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"
)
    recomendador = crear_recomendador(API_KEY)
    
    texto_test = "Me siento muy feliz hoy"
    resultado = recomendador.analizar_emocion_y_recomendar(texto_test)
    print("Resultado de prueba:", resultado[0])
