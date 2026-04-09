import pandas as pd
import os

def main():
    print("Starting Feature Engineering...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base_dir)
    data_dir = os.path.join(project_dir, "data", "cleaned")

    movies_path = os.path.join(data_dir, "movies_clean.csv")
    tags_path = os.path.join(data_dir, "tags_clean.csv")

    movies = pd.read_csv(movies_path)
    tags = pd.read_csv(tags_path)

    tags_grouped = tags.groupby("movieId")["tag"].apply(lambda x: " ".join(x.dropna().astype(str)))
    movies["tag"] = movies["movieId"].map(tags_grouped).fillna("")

    # CREATE A COMBINED FEATURE STRING
    movies["combined_features"] = (
        (movies["genres"].str.replace("|", " ", regex=False) + " ") * 2 +
        (movies["tag"] + " ") * 1
    ).str.lower()

    result = movies[["movieId", "title", "combined_features"]]

    output_dir = os.path.join(project_dir, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "movies_featured.csv")

    result.to_csv(output_path, index=False)

    print("Done! File saved to:", output_path)


if __name__ == "__main__":
    main()