import os
import pandas as pd
import numpy as np
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import streamlit.components.v1 as components
import requests
import re
from bs4 import BeautifulSoup
import concurrent.futures

# Set page config
st.set_page_config(
    page_title="Movie time fellas",
    page_icon="🎬",
    layout="wide"
)

# Canvas-based linear mouse-trail injection component with Hot-Reload Cleanup
components.html("""
<script>
const doc = window.parent.document;

// Clean up old canvas if present (essential for hot-reloads)
const oldCanvas = doc.getElementById('mouse-trail-canvas');
if (oldCanvas) {
    oldCanvas.remove();
}

// Clean up old listener if present to prevent leaks
if (window.parent.__mousemoveListener) {
    doc.removeEventListener('mousemove', window.parent.__mousemoveListener);
}

// Create new canvas
const canvas = doc.createElement('canvas');
canvas.id = 'mouse-trail-canvas';
canvas.style.position = 'absolute';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.pointerEvents = 'none';
canvas.style.zIndex = '999999';
doc.body.appendChild(canvas);

const ctx = canvas.getContext('2d');
let points = [];

// Sizing handling
function resizeCanvas() {
    canvas.width = doc.documentElement.scrollWidth;
    canvas.height = doc.documentElement.scrollHeight;
}
resizeCanvas();
doc.addEventListener('resize', resizeCanvas);
window.addEventListener('resize', resizeCanvas);

// Sizing update loop for dynamic content loads
setInterval(resizeCanvas, 1000);

// Track mouse movement coordinates with timestamp
const mousemoveListener = (e) => {
    points.push({
        x: e.pageX,
        y: e.pageY,
        time: Date.now()
    });
};
doc.addEventListener('mousemove', mousemoveListener);

// Save listener reference for next hot-reload cleanup
window.parent.__mousemoveListener = mousemoveListener;

// Render loop
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const now = Date.now();
    // Remove points older than 250ms for a tighter, cleaner trail
    points = points.filter(p => now - p.time < 250);
    
    if (points.length > 1) {
        for (let i = 1; i < points.length; i++) {
            const p1 = points[i - 1];
            const p2 = points[i];
            
            const age = now - p1.time;
            const ratio = 1 - (age / 250); // 1 at cursor tip, 0 at tail
            
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            
            // Translucent yellow stroke with a soft glow (lowered brightness)
            ctx.strokeStyle = `rgba(252, 196, 25, ${ratio * 0.22})`;
            ctx.lineWidth = ratio * 3.5;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            // Soft yellow shadow glow
            ctx.shadowBlur = 3;
            ctx.shadowColor = 'rgba(252, 196, 25, 0.3)';
            
            ctx.stroke();
        }
    }
    
    requestAnimationFrame(animate);
}
animate();
</script>
""", height=0, width=0)

# Custom SVG logo of a vintage movie camera styled like a Tommy gun
camera_logo_svg = """
<div class="logo-container">
    <svg viewBox="0 0 100 80" width="95" height="95" fill="#fcc419" style="filter: drop-shadow(0 0 12px rgba(252, 196, 25, 0.7));">
        <!-- Left Reel -->
        <circle cx="36" cy="26" r="14" fill="none" stroke="#fcc419" stroke-width="2.5" />
        <circle cx="36" cy="26" r="4" fill="#fcc419" />
        <line x1="36" y1="12" x2="36" y2="40" stroke="#fcc419" stroke-width="1.5" />
        <line x1="22" y1="26" x2="50" y2="26" stroke="#fcc419" stroke-width="1.5" />
        <!-- Right Reel -->
        <circle cx="64" cy="26" r="14" fill="none" stroke="#fcc419" stroke-width="2.5" />
        <circle cx="64" cy="26" r="4" fill="#fcc419" />
        <line x1="64" y1="12" x2="64" y2="40" stroke="#fcc419" stroke-width="1.5" />
        <line x1="50" y1="26" x2="78" y2="26" stroke="#fcc419" stroke-width="1.5" />
        <!-- Camera Body / Gun Frame -->
        <path d="M 28 44 H 72 V 64 H 48 L 40 76 H 28 Z" fill="#fcc419" stroke="#0c0909" stroke-width="1.2" />
        <!-- Lens / Gun Barrel -->
        <path d="M 72 48 L 92 44 L 92 60 L 72 56 Z" fill="#fcc419" />
        <line x1="86" y1="45" x2="86" y2="59" stroke="#0c0909" stroke-width="1.5" />
        <!-- Pistol Grip -->
        <path d="M 38 64 L 30 84 H 42 L 48 64 Z" fill="#fcc419" />
        <!-- Trigger Guard & Trigger -->
        <path d="M 52 64 C 52 71, 60 71, 60 64" stroke="#fcc419" stroke-width="2.5" fill="none" />
        <path d="M 55 64 Q 57 68, 55 68" stroke="#fcc419" stroke-width="2" fill="none" />
        <!-- Small details -->
        <path d="M 30 64 V 74 M 34 64 V 74" stroke="#0c0909" stroke-width="1" />
    </svg>
</div>
"""

# Custom CSS for fonts, sidebar fixes, padding removal, sharp edges glow, and button styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Limelight&family=Playfair+Display:ital,wght@1,400;1,600&family=Outfit:wght@300;400;600;700&display=swap');

/* Global viewport edge-lighting and background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0808 !important;
    background-image: radial-gradient(circle at top, #32080a 0%, #0b0808 70%) !important;
    font-family: 'Outfit', sans-serif !important;
    color: #f8f9fa !important;
    
    /* Slightly reduced blur so edge lighting spreads less and stays sharper */
    box-shadow: inset 0 0 35px rgba(252, 196, 25, 0.4) !important;
}


/* Remove big blank white space at top of the page */
[data-testid="stHeader"] {
    background-color: transparent !important;
}
[data-testid="stHeader"] > div {
    display: none !important; /* Hide deploy/settings buttons */
}
[data-testid="stAppViewContainer"] {
    padding-top: 0px !important;
}
[data-testid="stMainViewContainer"] {
    padding-top: 0px !important;
}
.block-container {
    padding-top: 1rem !important; /* Pull content to top */
    padding-bottom: 2rem !important;
}


/* Headings styling */
h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px;
}

/* Curved screening banner */
.cinema-screen {
    background: linear-gradient(180deg, #161111 0%, #0c0909 100%);
    border-top: 4px solid #fcc419;
    border-bottom: 2px solid #e50914;
    border-radius: 4px 4px 60px 60px / 4px 4px 15px 15px;
    box-shadow: 0 -15px 40px -10px rgba(229, 9, 20, 0.3), 
                0 15px 30px rgba(0, 0, 0, 0.8);
    padding: 20px 20px;
    text-align: center;
    margin-bottom: 35px;
    position: relative;
}

/* Premium vintage cinema Limelight font for title */
.cinema-screen h1 {
    font-family: 'Limelight', cursive !important;
    font-size: 4.8rem !important; /* Made significantly bigger than tagline */
    color: #ffffff;
    text-shadow: 0 0 15px rgba(252, 196, 25, 0.6), 0 0 25px rgba(229, 9, 20, 0.4);
    margin: 0;
    letter-spacing: 3px;
    line-height: 1.1;
}

/* Thin italic Playfair Display font for tagline */
.cinema-screen p {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-size: 1.35rem; /* Tighter visual contrast */
    color: #fcc419;
    margin: 15px 0 0 0;
    letter-spacing: 1px;
    font-weight: 400 !important;
    text-transform: none !important;
}

.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}

/* Modern-Vintage Celluloid Strip Card */
.film-card {
    background: rgba(22, 17, 17, 0.55) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(252, 196, 25, 0.15) !important;
    border-radius: 12px !important;
    position: relative !important;
    overflow: hidden !important;
    padding: 12px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    min-height: 480px !important;
}

/* Celluloid Film Sprocket Holes Styling (repeating gold/black pattern) */
.film-sprockets {
    height: 12px;
    width: 100%;
    background: repeating-linear-gradient(
        90deg,
        #0b0808,
        #0b0808 10px,
        #fcc419 10px,
        #fcc419 18px
    );
    border-radius: 2px;
    opacity: 0.85;
    margin-bottom: 12px;
}

.film-card:hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 20px 40px rgba(252, 196, 25, 0.35) !important;
    border-color: #fcc419 !important;
}

/* Change sprocket colors to white/yellow highlights on hover */
.film-card:hover .film-sprockets {
    background: repeating-linear-gradient(
        90deg,
        #fcc419,
        #fcc419 10px,
        #ffffff 10px,
        #ffffff 18px
    );
    opacity: 1;
}

.ticket-poster-container {
    width: 100%;
    height: 250px;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.6);
    margin-bottom: 12px;
}

.ticket-poster {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s ease;
}

.film-card:hover .ticket-poster {
    transform: scale(1.08);
}

.ticket-details {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    justify-content: space-between;
    text-align: center;
    padding: 0 5px;
}

.ticket-title {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    color: #ffffff;
    margin: 5px 0 10px 0;
    line-height: 1.2;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 3.4rem;
    letter-spacing: 1px;
}

.ticket-meta {
    font-size: 0.95rem;
    color: #c5c5c5;
    margin-bottom: 15px;
    font-weight: 300;
}

.ticket-rating {
    color: #fcc419;
    font-weight: 600;
}

/* Card Button: Outlined yellow button that fills on hover */
.ticket-btn {
    display: block;
    background: transparent;
    color: #fcc419 !important;
    text-decoration: none !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.15rem;
    letter-spacing: 1.5px;
    padding: 8px 12px;
    border-radius: 6px;
    text-align: center;
    transition: all 0.3s ease;
    border: 2px solid rgba(252, 196, 25, 0.4);
    margin-top: auto;
    cursor: pointer !important;
}

.ticket-btn:hover {
    background: #fcc419 !important;
    color: #0b0808 !important;
    border-color: #fcc419 !important;
    box-shadow: 0 4px 15px rgba(252, 196, 25, 0.4);
}

/* Tabs customization */
.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #161111;
    border-radius: 8px 8px 0 0;
    color: #b3b3b3;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem;
    letter-spacing: 1.5px;
    padding: 10px 25px;
    border: 1px solid rgba(252, 196, 25, 0.15);
    border-bottom: none;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #fcc419 !important;
    color: #0b0808 !important;
    border-color: #fcc419 !important;
}

.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background-color: #2b2020;
    color: #ffffff;
}

/* Force hand cursor on search select box dropdown components */
div[data-baseweb="select"], 
div[data-baseweb="select"] *, 
input[role="combobox"], 
.stSelectbox div {
    cursor: pointer !important;
}

div[role="listbox"],
div[role="listbox"] * {
    cursor: pointer !important;
}

/* Main Action Buttons: Yellow by default, black and gold/yellow on hover */
div.stButton > button {
    background-color: #fcc419 !important;
    color: #0b0808 !important;
    border: 2px solid #fcc419 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.35rem !important;
    letter-spacing: 1.5px !important;
    padding: 8px 24px !important;
    border-radius: 6px !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    cursor: pointer !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(252, 196, 25, 0.25) !important;
}

div.stButton > button p {
    color: inherit !important;
}

div.stButton > button:hover {
    background-color: #0b0808 !important;
    color: #fcc419 !important;
    border: 2px solid #fcc419 !important;
    box-shadow: 0 0 25px rgba(252, 196, 25, 0.5) !important;
    transform: translateY(-2px) !important;
}

div.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Bottom page footer styling */
.footer-container {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px dashed rgba(252, 196, 25, 0.2);
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem;
    color: #888888;
    padding-bottom: 25px;
}

.footer-link {
    color: #fcc419 !important;
    text-decoration: none !important;
    font-weight: 600;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer !important;
}

.footer-link:hover {
    color: #ffffff !important;
    text-shadow: 0 0 8px rgba(252, 196, 25, 0.6);
}
</style>
""", unsafe_allow_html=True)


# Load data and compute similarity matrix (cached at startup)
@st.cache_resource
def load_and_preprocess_data():
    try:
        # Load dataset
        base_dir = os.path.dirname(os.path.abspath(__file__))
        movies_path = os.path.join(base_dir, "tmdb 5000", "tmdb_movies.csv")
        credits_path = os.path.join(base_dir, "tmdb 5000", "tmdb_credits.csv")
        
        df = pd.read_csv(movies_path)
        df_credits = pd.read_csv(credits_path)
        
        # Drop title from movies (it's duplicated in credits)
        df.drop('title', axis=1, inplace=True)
        df.rename(columns={'original_title': 'title'}, inplace=True)
        
        # Merge credits with movies
        df_credits.rename(columns={'movie_id': 'id'}, inplace=True)
        df = df.merge(df_credits[['id', 'cast', 'crew']], on='id', how='left')
        
        # Save original genres list for filtering by genre in the UI
        def get_genres_list(text):
            try:
                return [item['name'] for item in ast.literal_eval(text)]
            except Exception:
                return []
                
        df['genres_list'] = df['genres'].apply(get_genres_list)
        
        # Clean release date to release year
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year.fillna(0).astype(int)
        
        # Overview and tagline combination
        df['tagline'] = df['tagline'].fillna(' ')
        df['overview'] = df['overview'].fillna(' ') + ' ' + df['tagline']
        df['overview'] = df['overview'].apply(lambda x: ' '.join(str(x).split()[:50]))
        
        # Drop unused columns
        cols_to_drop = ['budget', 'homepage', 'original_language', 'popularity', 
                        'production_companies', 'production_countries', 'revenue', 'spoken_languages']
        df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)
        
        # Fill runtime
        df['runtime'] = df['runtime'].fillna(df['runtime'].mean()).astype(int)
        
        # Keep only released movies
        df = df[df['status'] == 'Released'].copy()
        df.drop(columns=['status'], inplace=True, errors='ignore')
        
        # Clean cast (up to 3 names, remove spaces)
        def extract_cast(text):
            try:
                cast_list = []
                for i, item in enumerate(ast.literal_eval(text)):
                    if i < 3:
                        cast_list.append(item['name'].replace(" ", ""))
                return " ".join(cast_list)
            except Exception:
                return ""
                
        # Clean crew (Director only)
        def extract_director(text):
            try:
                for item in ast.literal_eval(text):
                    if item['job'] == 'Director':
                        return item['name'].replace(" ", "")
                return ""
            except Exception:
                return ""
                
        df['cast_clean'] = df['cast'].apply(extract_cast)
        df['crew_clean'] = df['crew'].apply(extract_director)
        
        # Clean genres and keywords for vectorization
        def clean_json_names(text):
            try:
                names = [item['name'].replace(" ", "") for item in ast.literal_eval(text)]
                return " ".join(names).lower()
            except Exception:
                return ""
                
        df['genres_clean'] = df['genres'].apply(clean_json_names)
        df['keywords_clean'] = df['keywords'].apply(clean_json_names)
        
        # Filter by vote count
        df = df[df['vote_count'] >= 60].copy()
        df.reset_index(drop=True, inplace=True)
        
        # Stem overview
        ps = PorterStemmer()
        def stem(text):
            return " ".join([ps.stem(word) for word in text.split()])
            
        df['overview_stemmed'] = df['overview'].apply(stem)
        
        # Combine tags
        df['tags'] = (
            df['genres_clean'] + " " + df['genres_clean'] + " " +
            df['keywords_clean'] + " " + df['keywords_clean'] + " " + df['keywords_clean'] + " " +
            df['cast_clean'] + " " + df['cast_clean'] + " " +
            df['crew_clean'] + " " + df['crew_clean'] + " " +
            df['title'].str.lower() + " " + df['title'].str.lower() + " " + df['title'].str.lower() + " " +
            df['overview_stemmed']
        )
        df['tags'] = df['tags'].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True).str.lower()
        
        # TF-IDF Vectorizer
        tfidf = TfidfVectorizer(max_features=10000, stop_words='english', ngram_range=(1,2))
        vectors = tfidf.fit_transform(df['tags']).toarray()
        
        # Cosine Similarity
        sim = cosine_similarity(vectors)
        
        # Keep raw title for search casing, but lower titles for matching
        df['original_title'] = df['title']
        df['title'] = df['title'].str.lower()
        
        return df, sim
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Load the data
with st.spinner("🎞️ Projecting celluloid... Please Wait."):
    df, sim = load_and_preprocess_data()

# Dynamic Extraction of Unique Genres
@st.cache_data
def get_all_genres(_df):
    genres = set()
    for lst in _df['genres_list']:
        for g in lst:
            genres.add(g)
    return sorted(list(genres))

if df is not None:
    all_genres = get_all_genres(df)
else:
    all_genres = []

# Fetch Movie Poster URL (cached to prevent repeated network requests)
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    # Scraping (zero-config)
    try:
        url = f"https://www.themoviedb.org/movie/{movie_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_og_image = soup.find('meta', property='og:image')
            if meta_og_image and meta_og_image.get('content'):
                return meta_og_image['content']
            match = re.search(r'<meta property="og:image" content="([^"]+)"', response.text)
            if match:
                return match.group(1)
    except Exception:
        pass

    # High quality Unsplash movie theater fallback poster
    return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=500&auto=format&fit=crop"

# Concurrent poster loading for the 5 recommendations
def fetch_multiple_posters(movie_ids):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        posters = list(executor.map(fetch_poster, movie_ids))
    return posters

# Content-based recommendation algorithm
def recommend_movies(movie_title, _df, _sim):
    movie_title_lower = movie_title.lower()
    if movie_title_lower not in _df['title'].values:
        return []
        
    movie_index = _df[_df['title'] == movie_title_lower].index[0]
    distances = _sim[movie_index]
    
    # Sort distances (exclude the searched movie itself at index 0)
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]
    
    results = []
    for i in movies_list:
        idx = i[0]
        results.append({
            'id': _df.iloc[idx].id,
            'title': _df.iloc[idx].original_title,
            'release_year': _df.iloc[idx].release_year,
            'tmdb_link': f"https://www.themoviedb.org/movie/{_df.iloc[idx].id}",
            'rating': _df.iloc[idx].vote_average
        })
    return results

# Genre-based recommendation algorithm
def recommend_by_genre(genre_name, _df):
    # Filter by genre and sort by rating and vote count to recommend top movies
    genre_movies = _df[_df['genres_list'].apply(lambda x: genre_name in x)]
    genre_movies = genre_movies.sort_values(by=['vote_average', 'vote_count'], ascending=[False, False])
    
    results = []
    for idx, row in genre_movies.head(5).iterrows():
        results.append({
            'id': row.id,
            'title': row.original_title,
            'release_year': row.release_year,
            'tmdb_link': f"https://www.themoviedb.org/movie/{row.id}",
            'rating': row.vote_average
        })
    return results


# APP LAYOUT
# Cinema Screen Glow Header (Aligned to far-left margin, title and tagline full stops removed, typography updated)
st.markdown(f"""<div class="cinema-screen">
{camera_logo_svg}
<h1>Movie time fellas</h1>
<p>Movies are dreams that you never forget</p>
</div>""", unsafe_allow_html=True)


# Main Application Tabs (Search tab in lowercase as requested)
tab_search, tab_genre = st.tabs(["search film by title", "Explore by Genre"])

# TAB 1: Search film by title
with tab_search:
    st.markdown("### 🎬 What film did you enjoy?")
    st.write("Type or select a movie you like from the cinema registry to find similar recommendations.")
    
    if df is not None:
        movie_titles_list = df['original_title'].tolist()
        selected_movie = st.selectbox(
            "Select or Type a Movie Title",
            options=movie_titles_list,
            index=None,
            placeholder="Choose a movie..."
        )
        
        if st.button("Recommend Similar Movies", key="btn_search"):
            if not selected_movie:
                st.warning("Please select or type a movie title first.")
            else:
                st.markdown("---")
                with st.spinner("📽️ Projecting recommended films onto the screen..."):
                    recs = recommend_movies(selected_movie, df, sim)
                    
                    if recs:
                        movie_ids = [m['id'] for m in recs]
                        posters = fetch_multiple_posters(movie_ids)
                        
                        st.markdown("### 🎞️ Now Showing:")
                        cols = st.columns(5)
                        for i, col in enumerate(cols):
                            if i < len(recs):
                                movie = recs[i]
                                poster_url = posters[i]
                                
                                # Card designed like a celluloid strip cell (modern-vintage style)
                                card_html = f"""
                                <div class="film-card">
                                    <div class="film-sprockets"></div>
                                    <div class="ticket-poster-container">
                                        <img src="{poster_url}" class="ticket-poster" alt="{movie['title']}">
                                    </div>
                                    <div class="ticket-details">
                                        <h3 class="ticket-title">{movie['title']}</h3>
                                        <p class="ticket-meta">📅 {movie['release_year']} | <span class="ticket-rating">⭐ {movie['rating']:.1f}/10</span></p>
                                        <a href="{movie['tmdb_link']}" target="_blank" class="ticket-btn">View Movie</a>
                                    </div>
                                    <div class="film-sprockets" style="margin-top: 12px; margin-bottom: 0;"></div>
                                </div>
                                """
                                col.markdown(card_html, unsafe_allow_html=True)
                    else:
                        st.error("Movie not found in registry.")
    else:
        st.error("Registry failed to load. Please verify the CSV files.")

# TAB 2: Genre-based finding
with tab_genre:
    st.markdown("### 🎭 Choose a Movie Genre")
    st.write("Select a film genre below to receive 5 of the top-rated recommendations in that category.")
    
    if df is not None and len(all_genres) > 0:
        selected_genre = st.selectbox(
            "Select Genre",
            options=all_genres,
            index=all_genres.index("Action") if "Action" in all_genres else 0
        )
        
        if st.button("Discover Top Hits", key="btn_genre"):
            st.markdown("---")
            with st.spinner("📽️ Loading top hits for this genre..."):
                recs = recommend_by_genre(selected_genre, df)
                
                if recs:
                    movie_ids = [m['id'] for m in recs]
                    posters = fetch_multiple_posters(movie_ids)
                    
                    st.markdown(f"### 🎞️ Top 5 Recommendations in {selected_genre}:")
                    cols = st.columns(5)
                    for i, col in enumerate(cols):
                        if i < len(recs):
                            movie = recs[i]
                            poster_url = posters[i]
                            
                            card_html = f"""
                            <div class="film-card">
                                <div class="film-sprockets"></div>
                                <div class="ticket-poster-container">
                                    <img src="{poster_url}" class="ticket-poster" alt="{movie['title']}">
                                </div>
                                <div class="ticket-details">
                                    <h3 class="ticket-title">{movie['title']}</h3>
                                    <p class="ticket-meta">📅 {movie['release_year']} | <span class="ticket-rating">⭐ {movie['rating']:.1f}/10</span></p>
                                    <a href="{movie['tmdb_link']}" target="_blank" class="ticket-btn">View Movie</a>
                                </div>
                                <div class="film-sprockets" style="margin-top: 12px; margin-bottom: 0;"></div>
                            </div>
                            """
                            col.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("No movies found for this genre.")
    else:
        st.error("Registry genres failed to load.")

# Static bottom page footer linking to Crimson-BladeX's GitHub Profile and LinkedIn
st.markdown("""
<div class="footer-container">
    <span>Developed by </span>
    <a href="https://github.com/Crimson-BladeX" target="_blank" class="footer-link">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 2px;"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        GitHub
    </a>
    <span style="margin: 0 10px;">|</span>
    <a href="https://www.linkedin.com/in/dharanig21" target="_blank" class="footer-link">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 2px;"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
        LinkedIn
    </a>
</div>
""", unsafe_allow_html=True)
