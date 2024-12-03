import pandas as pd

def filter_movies(params):
    """Filters movies based on genre and rating and adds IMDb and TMDb links."""
    # Load datasets
    movies_df = pd.read_csv("dataset/movies.csv")
    ratings_df = pd.read_csv("dataset/ratings.csv")
    links_df = pd.read_csv("dataset/links.csv")

    # Calculate average ratings
    avg_ratings = ratings_df.groupby("movieId")["rating"].mean().reset_index()
    movies_df = movies_df.merge(avg_ratings, on="movieId", how="left")

    # Filter by genre if specified
    if params.get("genre"):
        genre_filter = params["genre"]
        movies_df = movies_df[movies_df["genres"].str.contains(genre_filter, case=False, na=False)]

    # Filter by rating if specified
    min_rating = params.get("rating", 0)
    movies_df = movies_df[movies_df["rating"].fillna(0) >= min_rating]
    # Add IMDb and TMDb links
    movies_df = movies_df.merge(links_df, on="movieId", how="left")
    movies_df["imdb_link"] = movies_df["imdbId"].apply(
        lambda x: f"https://www.imdb.com/title/tt{str(int(x)).zfill(7)}/" if pd.notnull(x) else None
    )
    movies_df["tmdb_link"] = movies_df["tmdbId"].apply(
        lambda x: f"https://www.themoviedb.org/movie/{int(x)}" if pd.notnull(x) else None
    )

    # Return filtered results with only the required columns
    return movies_df[["title", "genres", "rating", "imdb_link", "tmdb_link", "tmdbId"]].dropna(subset=["rating"]).to_dict(orient="records")
