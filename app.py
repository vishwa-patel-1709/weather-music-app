import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Vibe Studio", page_icon="🎧", layout="centered")

# --- 2. MINIMALIST STUDIO CSS ---
st.markdown("""
    <style>
    /* Deep matte background with a subtle data-grid pattern */
    .stApp {
        background-color: #121212;
        background-image: 
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean, editorial header */
    .studio-title {
        font-size: 42px;
        font-weight: 300;
        letter-spacing: -1px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Minimalist search bar */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #333 !important;
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        padding: 18px !important;
        font-size: 18px !important;
        font-weight: 300;
        transition: all 0.2s ease-in-out;
    }
    
    .stTextInput > div > div > input:focus {
        border: 1px solid #1DB954 !important;
        box-shadow: none !important;
    }
    
    /* Sleek 'Now Playing' style cards */
    .studio-card {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
    }
    
    .track-name {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        margin: 0 0 8px 0;
    }
    
    .artist-name {
        font-size: 16px;
        font-weight: 400;
        color: #b3b3b3;
        margin: 0;
    }
    
    .vibe-tag {
        display: inline-block;
        background-color: #282828;
        color: #b3b3b3;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 500;
        margin-top: 16px;
        width: fit-content;
    }
    
    /* Clean metric boxes */
    .metric-container {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="studio-title">Atmosphere Analytics</h1>', unsafe_allow_html=True)
st.write("<center style='color: #b3b3b3; font-weight: 300; margin-bottom: 30px;'>Input a global coordinate. Extract real-time climate and acoustic correlations.</center>", unsafe_allow_html=True)

# --- 3. DATA PROCESSING ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british",
}

# --- 4. APP INTERACTION ---
city = st.text_input("", placeholder="Search city (e.g., Ahmedabad, London)...")

if city:
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error("Location not found in global index.")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', 'United States')
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        local_genre = country_to_genre.get(country, "pop")
        genre_df = df[df['track_genre'] == local_genre] if 'track_genre' in df.columns else df
        if genre_df.empty: genre_df = df
        
        # Determine the vibe for the UI tag
        if current_temp > 25:
            recs = genre_df[(genre_df['energy'] > 0.6)]
            vibe_label = f"{current_temp}°C • High Energy"
        elif current_temp > 10:
            recs = genre_df[genre_df['valence'] > 0.5]
            vibe_label = f"{current_temp}°C • Elevated Valence"
        else:
            recs = genre_df[(genre_df['energy'] < 0.5)]
            vibe_label = f"{current_temp}°C • Acoustic / Chill"

        # Minimalist Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-container'><span style='color:#b3b3b3; font-size:14px;'>Target</span><br><span style='font-size:24px; color:#fff;'>{city.title()}, {country}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-container'><span style='color:#b3b3b3; font-size:14px;'>Climate Parameter</span><br><span style='font-size:24px; color:#fff;'>{vibe_label}</span></div>", unsafe_allow_html=True)
            
        st.write("") # Spacer
        
        # Display recommendations
        if not recs.empty:
            top_3 = recs.sample(min(3, len(recs)))
            for index, row in top_3.iterrows():
                st.markdown(f"""
                <div class="studio-card">
                    <p class="track-name">{row['track_name']}</p>
                    <p class="artist-name">{row['artists']}</p>
                    <div class="vibe-tag">Genre: {local_genre.title()}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Insufficient acoustic data for this coordinate.")