import streamlit as st
import pickle
import requests
import os
import gdown

# Download similarity.pkl from Google Drive if it's not already present locally
SIMILARITY_FILE_ID = '1-9LyvEEoyfG6sVveuA6Nb6Bnj2mK56HS'
SIMILARITY_PATH = 'similarity.pkl'

if not os.path.exists(SIMILARITY_PATH):
    gdown.download(id=SIMILARITY_FILE_ID, output=SIMILARITY_PATH, quiet=False)

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open(SIMILARITY_PATH, 'rb'))


def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" +  data['poster_path']


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster from api
        recommended_movies_posters.append(fetch_poster(movie_id))

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
    "",
    movies['title'].values,
    label_visibility="collapsed",
)
recommend_clicked = st.button("Recommend")
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------
if recommend_clicked:
    names, posters = recommend(selected_movie_name)

    st.markdown('<div class="results-heading">✦ Also Playing ✦</div>', unsafe_allow_html=True)

    cards_html = '<div class="film-grid">'
    for name, poster in zip(names, posters):
        cards_html += f"""
        <div class="film-card">
            <div class="sprockets"></div>
            <img src="{poster}" alt="{name}" />
            <div class="sprockets"></div>
            <div class="title-plate">{name}</div>
        </div>
        """
    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)