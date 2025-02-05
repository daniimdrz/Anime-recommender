import sqlite3
import pandas as pd

def get_connection(db_name='anime_app.db'):
    """Crea y retorna una conexión a la base de datos."""
    return sqlite3.connect(db_name)

def load_data(db_name='anime_app.db'):
    """Carga y retorna el DataFrame con los datos de animes."""
    with sqlite3.connect(db_name) as conn:
        query = "SELECT title, num_episodes, rating, genres, synopsis, main_picture_medium FROM animes"
        df = pd.read_sql(query, conn)
    # Seleccionamos solo las columnas necesarias
    df = df[['title', 'num_episodes', 'rating', 'genres', 'synopsis', 'main_picture_medium']]
    return df
