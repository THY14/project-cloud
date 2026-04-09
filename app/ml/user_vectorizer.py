import json
import os
import numpy as np
import pandas as pd
from scipy.sparse import load_npz
import pickle

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def load_artifacts(processed_dir: str):
    """Load movie matrix, movie index, and vectorizer."""
    matrix_path     = os.path.join(processed_dir, "movie_vectors.npz")
    index_path      = os.path.join(processed_dir, "movie_index.csv")
    vectorizer_path = os.path.join(processed_dir, "vectorizer.pkl")

    for p in [matrix_path, index_path, vectorizer_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing artifact: {p}")

    movie_matrix = load_npz(matrix_path)
    movie_index  = pd.read_csv(index_path)

    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)

    print(f"Loaded movie matrix  : {movie_matrix.shape}")
    print(f"Loaded movie index   : {len(movie_index)} titles")
    return movie_matrix, movie_index, vectorizer

def build_user_vector(liked_movie_ids, movie_matrix, movie_index):
    """Compute a single user's vector as the mean of liked movie vectors."""
    id_to_row = dict(zip(movie_index["movieId"], movie_index["vector_row"]))
    matched_rows = [id_to_row[mid] for mid in liked_movie_ids if mid in id_to_row]

    if not matched_rows:
        return None  # No liked movies found

    liked_vectors = movie_matrix[matched_rows].toarray()
    user_vector = liked_vectors.mean(axis=0)
    return user_vector

def build_user_matrix(ratings_path, movie_matrix, movie_index, rating_threshold=4.0):
    """Build matrix of all users: rows = users, columns = movie features."""
    ratings = pd.read_csv(ratings_path)
    user_ids = sorted(ratings["userId"].unique())
    num_features = movie_matrix.shape[1]
    user_id_to_row = {uid: i for i, uid in enumerate(user_ids)}
    user_matrix = np.zeros((len(user_ids), num_features), dtype=np.float32)

    for uid in user_ids:
        liked_ids = ratings[(ratings["userId"] == uid) & (ratings["rating"] >= rating_threshold)]["movieId"].tolist()
        user_vec = build_user_vector(liked_ids, movie_matrix, movie_index)
        if user_vec is not None:
            user_matrix[user_id_to_row[uid]] = user_vec

    print(f"Built user matrix: {user_matrix.shape} (users × features)")
    return user_matrix, user_id_to_row

def save_user_matrix(user_matrix, user_id_to_row, processed_dir):
    os.makedirs(processed_dir, exist_ok=True)
    matrix_path = os.path.join(processed_dir, "user_matrix.npy")
    mapping_path = os.path.join(processed_dir, "user_id_to_row.json")

    np.save(matrix_path, user_matrix)

    # Convert keys to int for JSON
    user_id_to_row_clean = {int(k): v for k, v in user_id_to_row.items()}

    with open(mapping_path, "w") as f:
        json.dump(user_id_to_row_clean, f)

    print(f"Saved user matrix → {matrix_path}")
    print(f"Saved user ID mapping → {mapping_path}")
    return matrix_path, mapping_path

def main(user_id=None, rating_threshold=4.0):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    processed_dir = os.path.join(project_root, "data", "processed")
    ratings_path  = os.path.join(project_root, "data", "cleaned", "ratings_clean.csv")

    movie_matrix, movie_index, vectorizer = load_artifacts(processed_dir)

    if user_id is not None:
        # Build a single user's vector
        ratings = pd.read_csv(ratings_path)
        liked_ids = ratings[(ratings["userId"] == user_id) & (ratings["rating"] >= rating_threshold)]["movieId"].tolist()
        user_vector = build_user_vector(liked_ids, movie_matrix, movie_index)
        print(f"Built vector for user {user_id}: {user_vector.shape if user_vector is not None else None}")
        return user_vector
    else:
        # Build matrix for all users
        user_matrix, user_id_to_row = build_user_matrix(ratings_path, movie_matrix, movie_index, rating_threshold)
        save_user_matrix(user_matrix, user_id_to_row, processed_dir)
        return user_matrix

# ─────────────────────────────────────────────
# Run script
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()