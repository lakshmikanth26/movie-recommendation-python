from flask import Blueprint, render_template, request, url_for
import pandas as pd
from .models.recommend import filter_movies
from .utils import load_movies
import requests

TMDB_API_KEY = '30d2fc00fd96fdce7c9c3dd575e37029'  # Replace with your TMDb API key
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # Base URL for TMDb image size

# Initialize blueprint
main_bp = Blueprint("main", __name__)

# Load movies and genres data
movies, genres = load_movies()

# Handle search route
@main_bp.route("/search", methods=["POST"])
def search():
    # Handle empty or invalid rating input
    try:
        rating = float(request.form.get("rating", 0))  # Default to 0 if no rating is provided
    except ValueError:
        rating = 0  # Fallback if input is invalid

    search_params = {
        "genre": request.form.get("genre"),
        "rating": rating,
    }
    filtered_movies = filter_movies(search_params)
    print(filtered_movies)
    # Add poster_url for each movie in filtered results
    for movie in filtered_movies:
        tmdb_id = movie.get("tmdbId")
        if tmdb_id:
            movie["poster_url"] = get_tmdb_poster_url(tmdb_id)  # Fetch poster from TMDb API
        else:
            movie["poster_url"] = url_for('static', filename='images/default.png')  # Default image

    return render_template("result.html", movies=filtered_movies)

def get_tmdb_poster_url(tmdb_id):
    """Fetch poster image URL from TMDb using tmdbId."""
    if not tmdb_id:
        return None

    # TMDb API URL for fetching movie details
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
    
    try:
        response = requests.get(url)
        data = response.json()
        # Extract poster path and generate full URL
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    except requests.exceptions.RequestException:
        return None
    return None

# Function to fetch popular movies for each genre
def get_popular_movies():
    popular_movies = {}
    
    # Load movies, links, and ratings data
    movies_df = pd.read_csv("dataset/movies.csv")
    links_df = pd.read_csv("dataset/links.csv")
    ratings_df = pd.read_csv("dataset/ratings.csv")
    
    # Merge movies data with links data to get imdbId and tmdbId
    merged_df = pd.merge(movies_df, links_df, on="movieId", how="left")
    
    # Merge ratings data to include movie ratings
    ratings_avg = ratings_df.groupby("movieId")["rating"].mean().reset_index()
    merged_df = pd.merge(merged_df, ratings_avg, on="movieId", how="left")
    
    for genre in genres:
        # Filter movies by genre
        genre_movies = merged_df[merged_df["genres"].str.contains(genre, na=False)]
        
        # Get the top movie based on rating for this genre
        top_movies = (
            genre_movies.sort_values(by="rating", ascending=False)
            .head(1)[["title", "genres", "rating", "movieId", "imdbId", "tmdbId"]]
            .to_dict(orient="records")
        )
        
        if top_movies:
            # Generate imdb_link and tmdb_link
            imdb_id = top_movies[0].get("imdbId")
            tmdb_id = top_movies[0].get("tmdbId")
            
            if imdb_id:
                top_movies[0]["imdb_link"] = f"https://www.imdb.com/title/tt{str(imdb_id).zfill(7)}/"
            if tmdb_id:
                top_movies[0]["tmdb_link"] = f"https://www.themoviedb.org/movie/{tmdb_id}"
                top_movies[0]["poster_url"] = get_tmdb_poster_url(tmdb_id)
            popular_movies[genre] = top_movies[0]
    
    return popular_movies

# Precompute popular movies for the index page when the server starts
popular_movies = get_popular_movies()

@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", movies=movies, genres=genres, popular_movies=popular_movies)
