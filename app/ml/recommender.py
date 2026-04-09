import json

import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle


# ─────────────────────────────────────────────────────────────
# 1. LOAD ARTIFACTS
# ─────────────────────────────────────────────────────────────

def load_artifacts(processed_dir: str):
    """
    Load every artifact produced by the previous three steps.
    Raises a clear FileNotFoundError if anything is missing.
    """
    paths = {
        "movie_matrix":  os.path.join(processed_dir, "movie_vectors.npz"),
        "movie_index":   os.path.join(processed_dir, "movie_index.csv"),
        "vectorizer":    os.path.join(processed_dir, "vectorizer.pkl"),
    }

    print(f"\nLooking for artifacts in: {processed_dir}")
    for label, p in paths.items():
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"Missing artifact [{label}]: {p}\n"
                "Make sure all previous steps have been run first:\n"
                "  1. feature_engineering.py\n"
                "  2. movie_vectorizer.py\n"
                "  3. user_vectorizer.py\n"
            )
        print(f"  ✓  {label:<14} → {os.path.basename(p)}")

    movie_matrix = load_npz(paths["movie_matrix"])
    movie_index  = pd.read_csv(paths["movie_index"])

    with open(paths["vectorizer"], "rb") as f:
        vectorizer = pickle.load(f)

    print(f"\nMovie matrix shape : {movie_matrix.shape}")
    print(f"Movie index rows   : {len(movie_index)}")

    return movie_matrix, movie_index, vectorizer


# ─────────────────────────────────────────────────────────────
# 2. COSINE SIMILARITY COMPARISON
# ─────────────────────────────────────────────────────────────

def compute_similarity(user_vector: np.ndarray, movie_matrix) -> np.ndarray:
    """
    Compare the user vector against every movie vector using cosine similarity.

    Cosine similarity measures the angle between two vectors:
        . Score = 1.0  →  identical taste (perfect match)
        . Score = 0.0  →  completely different
    """
    print("\nComputing cosine similarity between user vector and all movies ...")

    # Reshape: (n_features,) → (1, n_features)
    user_vec_2d = user_vector.reshape(1, -1)

    # cosine_similarity handles both dense and sparse movie_matrix
    scores = cosine_similarity(user_vec_2d, movie_matrix)

    scores = scores.flatten()

    print(f"Similarity scores computed for {len(scores)} movies.")
    print(f"  Max score : {scores.max():.4f}")
    print(f"  Min score : {scores.min():.4f}")
    print(f"  Mean score: {scores.mean():.4f}")

    return scores


# ─────────────────────────────────────────────────────────────
# 3. RANK & FILTER
# ─────────────────────────────────────────────────────────────

def get_top_recommendations(
    scores: np.ndarray,
    movie_index: pd.DataFrame,
    ratings_path: str,
    user_id: int,
    top_n: int = 10,
    exclude_seen: bool = True,
) -> pd.DataFrame:
    """
    Rank all movies by similarity score and return the top-N results,
    optionally filtering out movies the user has already seen/rated.

    """

    results = movie_index.copy()
    results["similarity_score"] = scores

    # Exclude movies the user already watched
    if exclude_seen and os.path.exists(ratings_path):
        ratings = pd.read_csv(ratings_path)
        seen_ids = set(ratings[ratings["userId"] == user_id]["movieId"].tolist())
        before   = len(results)
        results  = results[~results["movieId"].isin(seen_ids)]
        print(f"\nExcluded {before - len(results)} already-seen movies for user {user_id}.")
    else:
        print("\n[Note] ratings.csv not found or exclude_seen=False — not filtering seen movies.")

    # Sort by score descending, take top N
    results = (
        results
        .sort_values("similarity_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    results.index += 1
    results.index.name = "rank"

    return results[["movieId", "title", "similarity_score"]]


# ─────────────────────────────────────────────────────────────
# 4. SAVE RESULTS
# ─────────────────────────────────────────────────────────────

def save_recommendations(recommendations: pd.DataFrame, processed_dir: str, user_id: int) -> str:
    os.makedirs(processed_dir, exist_ok=True)
    out_path = os.path.join(processed_dir, f"recommendations_{user_id}.csv")
    recommendations.to_csv(out_path)
    print(f"\nSaved recommendations → {out_path}")
    return out_path


# ─────────────────────────────────────────────────────────────
# 5. DISPLAY
# ─────────────────────────────────────────────────────────────

def print_recommendations(recommendations: pd.DataFrame, user_id: int):
    print(f"\n{'═' * 58}")
    print(f" Top-{len(recommendations)} Recommendations for User {user_id}")
    print(f"{'═' * 58}")
    print(f"{'Rank':<5} {'Score':>6}   {'Title'}")
    print(f"{'─' * 58}")
    for rank, row in recommendations.iterrows():
        print(f"{rank:<5} {row['similarity_score']:>6.4f}   {row['title']}")
    print(f"{'═' * 58}")


# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────

def main(user_id: int = 4, top_n: int = 10, exclude_seen: bool = True):
    print("=" * 60)
    print(" COMPARISON FOR RECOMMENDATION ")
    print("=" * 60)

    base_dir     = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    processed_dir = os.path.join(project_root, "data", "processed")
    ratings_path  = os.path.join(project_root, "data", "cleaned", "ratings_cleaned.csv")
    user_matrix = np.load(f"{processed_dir}/user_matrix.npy")
    with open(f"{processed_dir}/user_id_to_row.json") as f:
        user_id_to_row = json.load(f)

    print(f"\nProject root  : {project_root}")
    print(f"Processed dir : {processed_dir}")
    print(f"User ID       : {user_id}")
    print(f"Top N         : {top_n}")
    print(f"Exclude seen  : {exclude_seen}")

    # Step 1 – Load everything produced by the previous three steps
    movie_matrix, movie_index, vectorizer = load_artifacts(
        processed_dir
    )

    # Get user vector
    user_vector = user_matrix[user_id_to_row[str(user_id)]]

    # Step 2 – Compute cosine similarity: user_vector vs all movie vectors
    scores = compute_similarity(user_vector, movie_matrix)

    # Step 3 – Rank and filter
    recommendations = get_top_recommendations(
        scores        = scores,
        movie_index   = movie_index,
        ratings_path  = ratings_path,
        user_id       = user_id,
        top_n         = top_n,
        exclude_seen  = exclude_seen,
    )


    print("\n Recommendation step complete!")

    return recommendations


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate movie recommendations for a user.")
    parser.add_argument("--user_id",      type=int,   default=3,     help="userId from ratings.csv")
    parser.add_argument("--top_n",        type=int,   default=10,    help="Number of recommendations")
    parser.add_argument("--include_seen", action="store_true",       help="Include already-seen movies")

    args = parser.parse_args()

    main(
        user_id      = args.user_id,
        top_n        = args.top_n,
        exclude_seen = not args.include_seen,
    )