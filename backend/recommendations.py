import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
import sklearn
from fuzzywuzzy import fuzz

# Caché simple para almacenar recomendaciones según el título (en minúsculas)
_recommendations_cache = {}

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
    
    # Verificar la versión de scikit-learn y ajustar el parámetro de OneHotEncoder
    if sklearn.__version__ >= '0.24':
        encoder = OneHotEncoder(sparse_output=False)
    else:
        encoder = OneHotEncoder(sparse=False)
    
    # Se usa OneHotEncoder para los géneros y duración
    genero_encoded = encoder.fit_transform(df[['genres']])
    duracion_encoded = encoder.fit_transform(df[['Duración']])
    
    # Convertir rating a float32 para reducir memoria
    rating_array = df[['rating']].values.astype(np.float32)
    
    # Concatenamos las características: rating, géneros y duración
    matriz_caracteristicas = np.hstack((
        rating_array,
        genero_encoded.astype(np.float32),
        duracion_encoded.astype(np.float32)
    ))
    
    # Calculamos la similitud coseno
    matriz_similitud = cosine_similarity(matriz_caracteristicas)
    similarity_df = pd.DataFrame(matriz_similitud, index=df['title'], columns=df['title'])
    
    return df, similarity_df

def es_similar_nombre(nombre1, nombre2, umbral=90):
    return fuzz.ratio(nombre1.lower(), nombre2.lower()) > umbral

def recomendar_animes(anime, df, similarity_df, umbral_similitud=90):
    """
    Retorna una lista de recomendaciones para el anime solicitado.
    Se utiliza un caché para evitar cálculos repetidos.
    """
    cache_key = anime.lower()
    if cache_key in _recommendations_cache:
        return _recommendations_cache[cache_key]
    
    anime_lower = anime.lower()
    # Buscamos el título en el DataFrame comparando en minúsculas
    titles_lower = similarity_df.index.str.lower()
    if anime_lower not in titles_lower:
        result = [{"title": "El anime no está en la base de datos."}]
        _recommendations_cache[cache_key] = result
        return result
    
    # Recuperamos el título exacto según la coincidencia
    anime_exacto = similarity_df.index[titles_lower == anime_lower].tolist()[0]
    # Obtenemos las 6 animes más similares (excluyendo el mismo)
    similar_animes = similarity_df[anime_exacto].sort_values(ascending=False).iloc[1:7]
    
    recomendados = []
    for nombre in similar_animes.index:
        if not any(es_similar_nombre(nombre, recomendado, umbral_similitud) for recomendado in recomendados):
            recomendados.append(nombre)
    
    if not recomendados:
        result = [{"title": "No hay recomendaciones disponibles debido a la similitud de nombres."}]
        _recommendations_cache[cache_key] = result
        return result
    
    recomendaciones = []
    for nombre in recomendados[:6]:
        # Asegurarse de obtener la información del anime
        anime_info = df[df['title'] == nombre].iloc[0]
        recomendaciones.append({
            "title": nombre,
            "main_picture_medium": anime_info["main_picture_medium"],
            "rating": float(anime_info["rating"]),
            "num_episodes": int(anime_info["num_episodes"]),
            "synopsis": anime_info["synopsis"]
        })
    
    _recommendations_cache[cache_key] = recomendaciones
    return recomendaciones
