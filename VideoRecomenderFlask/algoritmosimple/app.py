import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.recomendaciondevideos
videos_collection = db.videos

def jaccard_similarity(list1, list2):
    intersection = len(set(list1).intersection(list2))
    union = len(set(list1).union(list2))
    return intersection / union

def recommend_video(watched_videos, all_genres):
    # Crear matriz de características (solo géneros)
    feature_matrix = []
    for video in watched_videos:
        features = [1 if genre in video['categories'] else 0 for genre in all_genres]
        feature_matrix.append(features)

    # Obtener todos los videos que no han sido vistos
    unseen_videos = list(videos_collection.find({'_id': {'$nin': [video['_id'] for video in watched_videos]}}))

    # Calcular similitud Jaccard entre cada video no visto y la matriz de características de los videos vistos
    similarity_scores = []
    for unseen_video in unseen_videos:
        unseen_features = [1 if genre in unseen_video['categories'] else 0 for genre in all_genres]
        score = np.mean([jaccard_similarity(unseen_features, seen_features) for seen_features in feature_matrix])
        similarity_scores.append(score)

    # Recomendar el video con la mayor similitud que no haya sido visto
    recommended_video_index = np.argmax(similarity_scores)
    return unseen_videos[recommended_video_index]

def main():
    watched_videos = []
    all_genres = set()

    # Obtener los dos primeros videos aleatoriamente
    first_two_videos = list(videos_collection.aggregate([{ '$sample': { 'size': 2 } }]))

    for i, video in enumerate(first_two_videos):
        print(f"Video {i + 1}: {video['filename']} - Categorías: {', '.join(video['categories'])}")
        all_genres.update(video['categories'])
        seconds_watched = int(input(f"¿Cuántos segundos ha visto el video {i + 1}? (0-15): "))
        video['seconds_watched'] = seconds_watched
        watched_videos.append(video)

    while True:
        recommended_video = recommend_video(watched_videos, all_genres)
        print(f"Se recomienda ver el siguiente video: {recommended_video['filename']} - Categorías: {', '.join(recommended_video['categories'])}")
        all_genres.update(recommended_video['categories'])
        seconds_watched = int(input("¿Cuántos segundos ha visto el video recomendado? (0-15): "))
        recommended_video['seconds_watched'] = seconds_watched
        watched_videos.append(recommended_video)

if __name__ == "__main__":
    main()
