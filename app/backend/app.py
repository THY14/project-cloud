from fastapi import FastAPI, HTTPException
from ml.recommender import main as run_recommender
from ml.user_vectorizer     import main as run_user_vector
import pandas as pd
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
import pickle
import numpy as np

app = FastAPI()
app.title = "Movie Recommendation System"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load links.csv to map movieId → tmdbId
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
links_path = os.path.join(BASE_DIR, "..", "data", "raw", "links.csv")
links_df = pd.read_csv(links_path)
movie_to_tmdb = dict(zip(links_df["movieId"], links_df["tmdbId"]))

TMDB_API_KEY = "96f75ceb3581bb9350c1d242265c92db"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.get("/user/{user_id}/recommend")
def get_movie_recommendations(user_id: int, top_n: int = 10):
    try:
        recommendations_df = run_recommender(
            user_id=user_id,
            top_n=top_n,
            exclude_seen=True,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    result = []
    for rank, row in recommendations_df.iterrows():
        movie_id = int(row["movieId"])
        tmdb_id = movie_to_tmdb.get(movie_id)
        poster_url = None

        if tmdb_id:
            try:
                res = requests.get(f"{TMDB_BASE_URL}/{tmdb_id}", params={
                    "api_key": TMDB_API_KEY,
                    "language": "en-US"
                })
                if res.status_code == 200:
                    data = res.json()
                    poster_path = data.get("poster_path")
                    if poster_path:
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            except Exception as e:
                print(f"Error fetching TMDB data for movie {tmdb_id}: {e}")

        result.append({
            "rank": int(rank),
            "movie_id": movie_id,
            "title": row["title"],
            "tmdb_id": tmdb_id,
            "poster_url": poster_url,
            "score": float(row["similarity_score"])
        })

    return {"user_id": user_id, "recommendations": result}


@app.get("/user/{user_id}/top-keywords")
def get_top_keywords(user_id: int, top_n: int = 10):
    
    user_vector = run_user_vector(user_id=user_id)
    if user_vector is None:
        return {"error": f"No liked movies for user {user_id}"}

    processed_dir = os.path.join(os.path.dirname(BASE_DIR), "data", "processed")
    vectorizer_path = os.path.join(processed_dir, "vectorizer.pkl")
    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)

    weights = user_vector.flatten()
    top_indices = weights.argsort()[::-1][:top_n]

    feature_names = np.array(vectorizer.get_feature_names_out())
    top_keywords = [{"keyword": feature_names[i], "weight": float(weights[i])} for i in top_indices]

    return {"user_id": user_id, "top_keywords": top_keywords}