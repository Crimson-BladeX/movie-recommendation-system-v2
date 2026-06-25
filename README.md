# 🎬 Movie Time Fellas

A content-based Movie Recommendation System built with Machine Learning and deployed using Streamlit.

## 📸 Demo

**Live App:** https://your-streamlit-url.streamlit.app

**GitHub Repository:** https://github.com/Crimson-BladeX/movie-recommendation-system-v2

---

## ✨ Features

- 🔍 Search movies by title
- 🎭 Discover movies by genre
- 🤖 Content-based recommendations using TF-IDF and Cosine Similarity
- 🎬 Movie posters fetched automatically from TMDB
- ⭐ Movie ratings and release year
- 🎨 Custom cinematic Streamlit UI

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- NLTK
- BeautifulSoup
- Requests

---

## 🧠 Machine Learning Pipeline

1. Load TMDB Movies and Credits datasets
2. Merge datasets
3. Clean and preprocess movie metadata
4. Apply stemming using NLTK
5. Create movie tags
6. Convert tags using TF-IDF Vectorizer
7. Compute Cosine Similarity
8. Recommend the most similar movies

---

## 📂 Dataset

TMDB 5000 Movie Dataset

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Crimson-BladeX/movie-recommendation-system-v2.git
```

Move into the folder

```bash
cd movie-recommendation-system-v2
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
movie-recommendation-system-v2/
│
├── app.py
├── requirements.txt
├── README.md
├── tmdb 5000/
│   ├── tmdb_movies.csv
│   └── tmdb_credits.csv
```

---

## 👨‍💻 Author

**Dharani G**

LinkedIn:
https://linkedin.com/in/dharanig21

GitHub:
https://github.com/Crimson-BladeX
