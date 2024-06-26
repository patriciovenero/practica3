import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración del registro de errores
logging.basicConfig(level=logging.DEBUG)

# Conexión a la base de datos MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.recomendaciondevideos

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    videos = list(db.videos.aggregate([{'$sample': {'size': 2}}]))
    return render_template('index.html', videos=videos)

@app.route('/add_video')
def add_video():
    categories = ['Acción', 'Comedia', 'Drama', 'Ciencia ficción', 'Romance',
                  'Aventura', 'Animación', 'Suspense', 'Fantasía', 'Documental',
                  'Terror', 'Musical', 'Crimen', 'Western', 'Histórico',
                  'Biografía', 'Misterio', 'Guerra', 'Deportes']
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

    video_data = {
        'filename': filename,
        'categories': categories,
        'upload_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    db.videos.insert_one(video_data)

    return redirect(url_for('index'))

@app.route('/video_seen', methods=['POST'])
def video_seen():
    try:
        video_id = request.json.get('video_id')
        seconds_watched = request.json.get('seconds_watched')

        app.logger.debug(f"Received request: video_id={video_id}, seconds_watched={seconds_watched}")

        video = db.videos.find_one({'_id': ObjectId(video_id)})

        if not video:
            app.logger.error(f"Video not found: video_id={video_id}")
            return jsonify({'error': 'Video not found'}), 404

        video_info = {
            'video_id': video_id,
            'filename': video['filename'],
            'categories': video['categories'],
            'seconds_watched': seconds_watched,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        app.logger.debug(f"Inserting video info into MongoDB: {video_info}")

        db.infovideo.insert_one(video_info)

        app.logger.debug(f"Video info stored in MongoDB: {video_info}")

        return jsonify({'status': 'success', 'video_info': video_info})
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        print(f"Error processing request: {e}")
        return 'Internal Server Error', 500

if __name__ == '__main__':
    app.run(debug=True)
