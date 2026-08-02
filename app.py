import streamlit as st
import pickle
import requests
import os
import gdown
from concurrent.futures import ThreadPoolExecutor

# Download similarity.pkl from Google Drive if it's not already present locally
SIMILARITY_FILE_ID = '1-9LyvEEoyfG6sVveuA6Nb6Bnj2mK56HS'
SIMILARITY_PATH = 'similarity.pkl'

if not os.path.exists(SIMILARITY_PATH):
    gdown.download(id=SIMILARITY_FILE_ID, output=SIMILARITY_PATH, quiet=False)

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open(SIMILARITY_PATH, 'rb'))


PLACEHOLDER_POSTER = "https://placehold.co/500x750/2B0A1F/D4AF37?text=No+Poster"
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")


def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US'.format(movie_id, TMDB_API_KEY),
            timeout=10,
        )
        data = response.json()
        poster_path = data.get('poster_path')
        if not poster_path:
            return PLACEHOLDER_POSTER
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception as e:
        print(f"fetch_poster failed for movie_id={movie_id}: {e}")
        return PLACEHOLDER_POSTER


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
    movie_ids = [movies.iloc[i[0]].movie_id for i in movies_list]

    # fetch all posters in parallel instead of one-by-one
    with ThreadPoolExecutor(max_workers=5) as executor:
        recommended_movies_posters = list(executor.map(fetch_poster, movie_ids))

    return recommended_movies, recommended_movies_posters


# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Now Showing — Movie Recommender",
    page_icon="🎟️",
    layout="wide",
)

# ------------------------------------------------------------------
# Cinema marquee theme — load CSS from external style.css
# ------------------------------------------------------------------
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ------------------------------------------------------------------
# Hero / marquee
# ------------------------------------------------------------------
st.markdown("""
<div class="marquee-wrap">
    <div class="marquee-lights"></div>
    <div class="marquee-title">NOW SHOWING</div>
    <div class="marquee-subtitle">Pick a film. We'll find what's playing next.</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Selector panel (ticket style)
# ------------------------------------------------------------------
st.markdown('<div class="ticket-panel">', unsafe_allow_html=True)
st.markdown('<div class="ticket-label">SELECT YOUR FEATURE</div>', unsafe_allow_html=True)
selected_movie_name = st.selectbox(
    "Select a movie",
    movies['title'].values,
    label_visibility="collapsed",
)
recommend_clicked = st.button("Recommend")
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------
if recommend_clicked:
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    st.markdown('<div class="results-heading">✦ Also Playing ✦</div>', unsafe_allow_html=True)

    cards_html = '<div class="film-grid">'
    for name, poster in zip(names, posters):
        cards_html += (
            '<div class="film-card">'
            '<div class="sprockets"></div>'
            f'<img src="{poster}" alt="{name}" />'
            '<div class="sprockets"></div>'
            f'<div class="title-plate">{name}</div>'
            '</div>'
        )
    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)