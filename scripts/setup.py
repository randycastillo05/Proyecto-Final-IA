#!/usr/bin/env python3
"""Setup script para configurar el proyecto"""

import os
import sys
import subprocess

def setup_project():
    """Configura el proyecto completo"""
    
    print("🚀 Configurando MoodMusic AI...")
    
    # Crear directorios necesarios
    directories = [
        'data/pretrained',
        'data/samples',
        'logs',
        'outputs'
    ]
    
    for dir in directories:
        os.makedirs(dir, exist_ok=True)
        print(f"✓ Creado directorio: {dir}")
    
    # Instalar dependencias
    print("\n📦 Instalando dependencias...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Descargar modelos
    print("\n🤖 Descargando modelos preentrenados...")
    subprocess.run([sys.executable, "scripts/download_models.py"])
    
    print("\n✅ ¡Configuración completa! Ejecuta 'python app.py' para iniciar.")

if __name__ == "__main__":
    setup_project()