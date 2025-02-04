# backend/config.py

import os

# Directorio actual (la carpeta backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta completa a la base de datos (se asume que está en la carpeta backend)
DATABASE = os.path.join(BASE_DIR, 'anime_app.db')

DEBUG = True
