# backend/app.py

from flask import Flask, jsonify, request, render_template
import os

# Importamos la configuración y la lógica modularizada
from backend.config import DEBUG, DATABASE
from database import load_data
from recommendations import prepare_data, recomendar_animes

app = Flask(__name__,
            template_folder=os.path.join('..', 'frontend'),
            static_folder=os.path.join('..', 'frontend', 'static'))

# Cargamos los datos y preparamos la similitud
df = load_data(DATABASE)
df, similarity_df = prepare_data(df)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    query_lower = query.lower()
    # Filtramos por títulos que contengan el query (sin distinguir mayúsculas)
    matches = df[df['title'].str.lower().str.contains(query_lower)]
    # Obtenemos un DataFrame con títulos únicos y sus imágenes; limitamos a 5 sugerencias.
    suggestions = matches[['title', 'main_picture_medium']].drop_duplicates().head(4)
    # Convertimos el DataFrame a una lista de diccionarios
    suggestions_list = suggestions.to_dict(orient='records')
    return jsonify(suggestions_list)




@app.route('/recomendaciones', methods=['GET'])
def obtener_recomendaciones():
    anime = request.args.get('anime', '')
    if anime:
        recomendaciones = recomendar_animes(anime, df, similarity_df)
        return jsonify(recomendaciones)
    else:
        return jsonify({"message": "Por favor, proporcione un nombre de anime para obtener recomendaciones."})
    


if __name__ == '__main__':
    app.run(debug=DEBUG)