import pandas as pd

def load_movies():
    movies_df = pd.read_csv("dataset/movies.csv")
    ratings_df = pd.read_csv("dataset/ratings.csv")

    # Calculate average ratings
    average_ratings = ratings_df.groupby("movieId")["rating"].mean()
    movies_df["rating"] = movies_df["movieId"].map(average_ratings)

    # Extract unique genres
    all_genres = set()
    for genre_list in movies_df["genres"].dropna():
        all_genres.update(genre_list.split("|"))
    genres = sorted(all_genres)

    return movies_df, genres
