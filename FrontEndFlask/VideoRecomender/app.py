from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
import random
import redis
import datetime

app = Flask(__name__)

# Conexión a la base de datos MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.recomendaciondevideos

# Conexión a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    videos = list(db.videos.find())
    return render_template('index.html', videos=videos)

@app.route('/add_video')
def add_video():
    categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5',
                  'Category 6', 'Category 7', 'Category 8', 'Category 9', 'Category 10',
                  'Category 11', 'Category 12', 'Category 13', 'Category 14', 'Category 15',
                  'Category 16', 'Category 17', 'Category 18', 'Category 19', 'Category 20']
    return render_template('add_video.html', categories=categories)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    video = request.files['video']
    categories = request.form.getlist('category[]')

    if video.filename == '':
        return jsonify({'error': 'No selected video file'}), 400

    filename = secure_filename(video.filename)
    video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Información del video
    video_data = {
        'filename': filename,
        'categories': categories,
    }

    # Insertar información del video en MongoDB
    db.videos.insert_one(video_data)

    # Obtener información del video
    video_info = {
        'id': str(db.videos.find_one({'filename': filename})['_id']),  # ID del video
        'user_id': request.form['user-id'],  # ID del usuario seleccionado
        'seconds_watched': 0,  # Inicialmente 0 segundos vistos
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Fecha actual
    }

    # Almacenar información del video en Redis
    r.hmset('video:' + video_info['id'], video_info)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
