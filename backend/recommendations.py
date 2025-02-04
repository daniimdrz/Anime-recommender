# backend/recommendations.py

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
from fuzzywuzzy import fuzz

def categorizar_duracion(num_episodios):
    if num_episodios <= 13:
        return 'Corta'
    elif num_episodios <= 26:
        return 'Media'
    else:
        return 'Larga'

def prepare_data(df):
    """
    Prepara el DataFrame añadiendo la columna 'Duración'
    y creando la matriz de características y de similitud.
    """
    df['Duración'] = df['num_episodes'].apply(categorizar_duracion)
    
    # Se usa OneHotEncoder para los géneros y duración
    encoder = OneHotEncoder(sparse_output=False)
    genero_encoded = encoder.fit_transform(df[['genres']])
    duracion_encoded = encoder.fit_transform(df[['Duración']])
    
    # Concatenamos las características (rating, géneros y duración)
    matriz_caracteristicas = np.hstack((
        df[['rating']].values,
        genero_encoded,
        duracion_encoded
    ))
    
    # Calculamos la similitud coseno
    matriz_similitud = cosine_similarity(matriz_caracteristicas)
    similarity_df = pd.DataFrame(matriz_similitud, index=df['title'], columns=df['title'])
    
    return df, similarity_df

def es_similar_nombre(nombre1, nombre2, umbral=90):
    return fuzz.ratio(nombre1.lower(), nombre2.lower()) > umbral

def recomendar_animes(anime, df, similarity_df, umbral_similitud=90):
    anime_lower = anime.lower()
    
    # Buscamos el título en el DataFrame comparando en minúsculas
    titles_lower = similarity_df.index.str.lower()
    if anime_lower not in titles_lower:
        return [{"title": "El anime no está en la base de datos."}]
    
    # Recuperar el título exacto según la coincidencia
    anime_exacto = similarity_df.index[titles_lower == anime_lower].tolist()[0]
    # Obtenemos las 5 animes más similares (excluyendo el mismo)
    similar_animes = similarity_df[anime_exacto].sort_values(ascending=False).iloc[1:7]
    
    recomendados = []
    for nombre in similar_animes.index:
        if not any(es_similar_nombre(nombre, recomendado, umbral_similitud) for recomendado in recomendados):
            recomendados.append(nombre)
    
    if not recomendados:
        return [{"title": "No hay recomendaciones disponibles debido a la similitud de nombres."}]
    
    recomendaciones = []
    for nombre in recomendados[:6]:
        anime_info = df[df['title'] == nombre].iloc[0]
        recomendaciones.append({
            "title": nombre,
            "main_picture_medium": anime_info["main_picture_medium"],
            "rating": float(anime_info["rating"]),
            "num_episodes": int(anime_info["num_episodes"]),
            "synopsis": anime_info["synopsis"]
        })
    
    return recomendaciones