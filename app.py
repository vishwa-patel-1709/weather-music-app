import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP & NEON THEME ---
st.set_page_config(page_title="Neon Vibe Check", page_icon="⚡", layout="centered")

# Injecting heavy custom CSS for a dark mode canvas with glowing neon borders
st.markdown("""
    <style>
    /* Force the entire background to a sleek dark cyber canvas */
    .stApp {
        background-color: #0d0e15 !important;
    }
    
    /* Make the title glow with a vibrant neon gradient */
    .neon-title {
        font-size: 50px !important;
        font-weight: bold;
        font-family: 'Courier New', Courier, monospace;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #00ffcc, 0 0 30px #00ffcc;
        margin-bottom: 5px;
    }
    
    /* Cyber styling for the subheader text */
    .neon-sub {
        text-align: center;
        color: #ff007f;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 8px rgba(255, 0, 127, 0.6);
        margin-bottom: 25px;
    }
    
    /* Neon glow effect for the input search bar */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #00ffcc !important;
        background-color: #161925 !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.4) !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    
    /* Futuristic Glassmorphic cards with glowing hot pink borders */
    .neon-card {
        background: rgba(22, 25, 37, 0.85);
        border: 2px solid #ff007f;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
        transition: all 0.3s ease;
    }
    
    .neon-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.8), 0 0 10px #fff;
    }
    
    /* Dynamic Weather Badge styles */
    .badge-hot {
        color: #ff3333;
        text-shadow: 0 0 10px #ff3333;
        font-weight: bold;
    }
    .badge-pleasant {
        color: #33ff33;
        text-shadow: 0 0 10px #33ff33;
        font-weight: bold;
    }
    .badge-cold {
        color: #33ccff;
        text-shadow: 0 0 10px #33ccff;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="neon-title">⚡ NEON VIBE CHECK ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="neon-sub">REAL-TIME WEATHER X GLOBAL AUDIO LOGIC</p>', unsafe_allow_html=True)

# --- 2. DATA PROCESSING ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

country_to_genre = {
    "India": "indian",
    "France": "french",
    "Germany": "german",
    "Spain": "spanish",
    "Mexico": "latino",
    "Japan": "j-pop",
    "South Korea": "k-pop",
    "Brazil": "brazil",
    "Turkey": "turkish",
    "Sweden": "swedish",
    "United Kingdom": "british",
}

# --- 3. RUNTIME APP INTERACTION ---
city = st.text_input("", placeholder="⌨️ ENTER SYSTEM CITY TARGET (e.g., AHMEDABAD, CHICAGO, TOKYO)...")

if city:
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"❌ ERROR: TARGET LOCATION '{city.upper()}' NOT FOUND.")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', 'United States')
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        # Configure localized genres
        local_genre = country_to_genre.get(country, "pop")
        genre_df = df[df['track_genre'] == local_genre] if 'track_genre' in df.columns else df
        if genre_df.empty: genre_df = df
        
        # Map out text style variables dynamically depending on climate data
        if current_temp > 25:
            status_badge = f"<span class='badge-hot'>CRITICAL HEAT // {current_temp}°C</span>"
            recs = genre_df[(genre_df['energy'] > 0.6)]
        elif current_temp > 10:
            status_badge = f"<span class='badge-pleasant'>OPTIMAL VIBE // {current_temp}°C</span>"
            recs = genre_df[genre_df['valence'] > 0.5]
        else:
            status_badge = f"<span class='badge-cold'>CRYOGENIC STATE // {current_temp}°C</span>"
            st.snow()
            recs = genre_df[(genre_df['energy'] < 0.5)]

        # Display Live Metric Indicators inside a dark slate format
        st.markdown(f"""
        <div style='background-color:#161925; padding:15px; border-radius:10px; border:1px solid #00ffcc; margin-bottom:25px; text-align:center;'>
            <span style='color:#fff; font-family:monospace;'>[ LOCATION: {city.upper()} ] &nbsp;&nbsp;&nbsp;&nbsp; [ CLIMATE: {status_badge} ] &nbsp;&nbsp;&nbsp;&nbsp; [ REGION GENRE: {local_genre.upper()} ]</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Pull 3 recommendation samples and frame them in glowing pink containers
        if not recs.empty:
            top_3 = recs.sample(min(3, len(recs)))
            for index, row in top_3.iterrows():
                st.markdown(f"""
                <div class="neon-card">
                    <h2 style="margin:0; color: #00ffcc; font-family: monospace; text-shadow: 0 0 5px rgba(0,255,204,0.5);">🎵 {row['track_name']}</h2>
                    <p style="font-size: 18px; margin: 8px 0 0 0; color: #ffffff; font-family: sans-serif;">🎤 ARTIST: <b>{row['artists']}</b></p>
                    <p style="font-size: 12px; margin: 12px 0 0 0; color: #ff007f; font-family: monospace; letter-spacing:1px;">⚡ ALGORITHMIC PLAYLIST FEED MATCH</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ CRITICAL OVERRIDE: DATASET CAPACITIES EXHAUSTED FOR CURRENT CLIMATE RANGE.")