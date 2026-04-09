import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
import os
import pickle


def load_featured_movies(processed_dir: str) -> pd.DataFrame:
    """
    Load the featured movie dataset produced by feature_engineering.py bro leab task.
    Expects a CSV with at least: movieId, title, combined_features
    """
    path = os.path.join(processed_dir, "movies_featured.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Featured dataset not found at: {path}\n"
            "Please run feature_engineering.py (Leab's task) first."
        )
    
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} movies from featured dataset.")
    return df

def build_tfidf_vectorizer(
    max_features: int = 5000,
    ngram_range: tuple = (1, 2),
    min_df: int = 2,
) -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        sublinear_tf=True,  
        strip_accents="unicode",
        analyzer="word",
    )


def vectorize_movies(movies_df: pd.DataFrame, vectorizer: TfidfVectorizer):
    texts = movies_df["combined_features"].fillna("").tolist()
    print(f"\nVectorizing {len(texts)} movies …")

    movie_matrix = vectorizer.fit_transform(texts)

    print(f"Matrix shape  : {movie_matrix.shape}")
    print(f"  • Rows      : {movie_matrix.shape[0]}  (one per movie)")
    print(f"  • Columns   : {movie_matrix.shape[1]}  (one per unique word/phrase)")
    print(f"  • Sparsity  : {100 * (1 - movie_matrix.nnz / (movie_matrix.shape[0] * movie_matrix.shape[1])):.2f}%")
    return movie_matrix, vectorizer


def save_artifacts(movie_matrix, vectorizer, movies_df: pd.DataFrame, processed_dir: str):
    os.makedirs(processed_dir, exist_ok=True)

    matrix_path     = os.path.join(processed_dir, "movie_vectors.npz")
    vectorizer_path = os.path.join(processed_dir, "vectorizer.pkl")
    index_path      = os.path.join(processed_dir, "movie_index.csv")

    save_npz(matrix_path, movie_matrix)
    print(f"\nSaved movie matrix   → {matrix_path}")

    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Saved vectorizer     → {vectorizer_path}")

    movie_index = movies_df[["movieId", "title"]].reset_index(drop=True)
    movie_index.index.name = "vector_row"
    movie_index.to_csv(index_path)
    print(f"Saved movie index    → {index_path}")

    return matrix_path, vectorizer_path, index_path


def print_sample(movies_df: pd.DataFrame, vectorizer: TfidfVectorizer, movie_matrix, title_query: str = "Toy Story"):
    mask = movies_df["title"].str.contains(title_query, case=False, na=False)
    if not mask.any():
        print(f"\n(No movie matching '{title_query}' found for sample output.)")
        return

    idx        = movies_df[mask].index[0]
    feature_names = vectorizer.get_feature_names_out()
    row        = movie_matrix[idx].toarray().flatten()
    top_idx    = row.argsort()[::-1][:10]

    print(f"\n── Sample: Top-10 TF-IDF keywords for '{movies_df.loc[idx, 'title']}' ──")
    print(f"  Raw text : {movies_df.loc[idx, 'combined_features'][:120]} …")
    print(f"  Keywords :")
    for rank, i in enumerate(top_idx, 1):
        if row[i] > 0:
            print(f"    {rank:2d}. '{feature_names[i]}'  →  {row[i]:.4f}")


def main():
    print("=" * 60)
    print("  MOVIE VECTORIZATION ")
    print("=" * 60)

    #Paths
    base_dir      = os.path.dirname(os.path.abspath(__file__))
    project_dir   = os.path.dirname(base_dir)
    processed_dir = os.path.join(project_dir, "data", "processed")

    # Step 1 : Load featured data (output from Leab's task)
    movies_df = load_featured_movies(processed_dir)

    #Step 2 : Build vectorizer 
    vectorizer = build_tfidf_vectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
    )

    # Step 3 : Vectorize every movie
    movie_matrix, vectorizer = vectorize_movies(movies_df, vectorizer)

    # Step 4 : Show a readable sample
    print_sample(movies_df, vectorizer, movie_matrix, title_query="Toy Story")

    # Step 5 : Save artifacts for bro Sak & theara
    save_artifacts(movie_matrix, vectorizer, movies_df, processed_dir)

    print("\n✓ Movie Vectorization complete!")
    print("  Next step bro Sak's task: build the User Vector using vectorizer.pkl")


if __name__ == "__main__":
    main()