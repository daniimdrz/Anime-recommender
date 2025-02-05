import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, render_template
from config import DEBUG, DATABASE
from database import load_data
from recommendations import prepare_data, recomendar_animes

app = Flask(__name__,
            template_folder=os.path.join('..', 'frontend'),
            static_folder=os.path.join('..', 'frontend', 'static'))

# Cargar datos y preparar la matriz de similitud (se realiza una sola vez al iniciar)
print("Cargando datos de la base de datos...")
df = load_data(DATABASE)
print("Preparando la matriz de similitud...")
df, similarity_df = prepare_data(df)
print("Datos cargados exitosamente.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    query_lower = query.lower()
    # Filtrar títulos que contengan el query (sin distinción de mayúsculas)
    matches = df[df['title'].str.lower().str.contains(query_lower)]
    suggestions = matches[['title', 'main_picture_medium']].drop_duplicates().head(4)
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
    port = int(os.getenv("PORT", 5000))
    app.run(debug=DEBUG, host="0.0.0.0", port=port)
