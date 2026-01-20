import streamlit as st
import pickle
import requests
import pandas as pd
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ------------------ LOAD DATA ------------------
MOVIES_PATH = "movies.pkl"
SIMILARITY_PATH = "similarity.pkl"

if not os.path.exists(MOVIES_PATH) or not os.path.exists(SIMILARITY_PATH):
    st.error(
        "❌ Required data files not found.\n\n"
        "Make sure movies.pkl and similarity.pkl are in the SAME folder as app.py"
    )
    st.stop()

try:
    movies = pickle.load(open(MOVIES_PATH, "rb"))
    similarity = pickle.load(open(SIMILARITY_PATH, "rb"))

    if not isinstance(movies, pd.DataFrame):
        st.error("❌ movies.pkl is not a pandas DataFrame.")
        st.stop()

    if "title" not in movies.columns:
        st.error("❌ movies.pkl must contain a 'title' column.")
        st.stop()

except Exception as e:
    st.error(f"❌ Error loading data files: {e}")
    st.stop()

# ------------------ OMDb API KEY ------------------
# Store key in .streamlit/secrets.toml
try:
    OMDB_API_KEY = st.secrets["omdb_api_key"]
except KeyError:
    st.error(
        "❌ OMDb API key not found.\n\n"
        "Add this to .streamlit/secrets.toml:\n"
        "omdb_api_key = \"YOUR_API_KEY\""
    )
    st.stop()

# ------------------ POSTER FUNCTION ------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        poster = data.get("Poster")
        if poster and poster != "N/A":
            return poster
    except Exception:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"

# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie_name):
    try:
        index = movies[movies["title"] == movie_name].index[0]
    except IndexError:
        return [], []

    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# ------------------ UI ------------------
st.title("🎬 Movie Recommendation System")

movie_titles = sorted(movies["title"].unique())
selected_movie = st.selectbox("Select a movie", movie_titles)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)


    if names:
        st.subheader(f"Movies similar to **{selected_movie}**")

        cols = st.columns(len(names))
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.image(poster, caption=name, width=230)
    else:
        st.info("No recommendations found.")

