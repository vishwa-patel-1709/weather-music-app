import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Vibe & Weather Matcher", page_icon="🎧", layout="centered")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

# Expanded dictionary for local music vibes
country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british", "United States": "pop", "Canada": "pop", 
    "Italy": "italian", "Sweden": "swedish", "Turkey": "turkish"
}

# --- 3. DYNAMIC UI & ANIMATIONS LOGIC ---
# Default moving gradient before search
bg_gradient = "linear-gradient(-45deg, #ff9a9e, #fecfef, #a1c4fd, #c2e9fb)"
app_message = "Type a city to unlock the vibes!"
text_color = "#845EC2" 
accent_color = "#FF9671"

# --- SMART SEARCH BAR ---
user_input = st.text_input("🔍 Search City or 'City, Country' (e.g., Paris, France):", placeholder="Enter location here...")

if user_input:
    search_city = user_input.split(',')[0].strip()
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"Oops! We couldn't find '{user_input}'. Please check the spelling and try again.")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        resolved_city = geo_response['results'][0]['name']
        country = geo_response['results'][0].get('country', 'Unknown Location')
        
        # Fetch weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        weather_data = requests.get(weather_url).json()
        
        current_temp_c = weather_data['current_weather']['temperature']
        current_temp_f = round((current_temp_c * 9/5) + 32, 1)
        
        raw_time = weather_data['current_weather']['time']
        try:
            local_time_obj = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M")
            local_time_formatted = local_time_obj.strftime("%I:%M %p")
        except Exception:
            local_time_formatted = "Live"
        
        # Change the moving gradient and colors based on weather
        if current_temp_c > 25:
            bg_gradient = "linear-gradient(-45deg, #ff758c, #ff7eb3, #f5576c, #f093fb)"
            app_message = f"🔥 Hot & High Energy in {resolved_city}"
            text_color = "#D9138A"
            accent_color = "#FF4B2B"
            recs = df[(df['energy'] > 0.6)]
        elif current_temp_c > 10:
            bg_gradient = "linear-gradient(-45deg, #4facfe, #00f2fe, #43e97b, #38f9d7)"
            app_message = f"🌤️ Perfect Vibes in {resolved_city}"
            text_color = "#0081C9"
            accent_color = "#00B4DB"
            recs = df[df['valence'] > 0.5]
        else:
            bg_gradient = "linear-gradient(-45deg, #a1c4fd, #c2e9fb, #e0c3fc, #8ec5fc)"
            app_message = f"❄️ Chill & Acoustic in {resolved_city}"
            text_color = "#2C3E50"
            accent_color = "#4CA1AF"
            recs = df[(df['energy'] < 0.5)]

        # --- ADVANCED CSS ANIMATIONS & TRANSITIONS ---
        st.markdown(f"""
            <style>
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .stApp {{
                background: {bg_gradient};
                background-size: 300% 300%;
                animation: gradientShift 10s ease infinite;
            }}
            
            .colorful-title {{
                font-size: 45px;
                font-weight: 900;
                color: #ffffff;
                text-align: center;
                margin-bottom: 5px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            }}
            
            .weather-dashboard {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                border: 3px solid {accent_color};
            }}
            
            .metric-text {{
                font-size: 20px;
                font-weight: bold;
                color: {text_color};
                margin: 5px 0;
            }}
            
            @keyframes slideUpFade {{
                from {{ opacity: 0; transform: translateY(40px) scale(0.95); }}
                to {{ opacity: 1; transform: translateY(0) scale(1); }}
            }}
            
            .vibe-card {{
                background-color: #ffffff;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-left: 8px solid {accent_color};
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
                opacity: 0; 
                animation: slideUpFade 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .vibe-card:hover {{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0px 15px 30px rgba(0, 0, 0, 0.2);
            }}
            
            .song-info {{
                flex: 1;
            }}
            
            .song-name {{ font-size: 22px; font-weight: 900; color: {text_color}; margin: 0; }}
            .artist-name {{ font-size: 16px; color: #555; margin-top: 5px; font-weight: bold; }}
            
            .btn-container {{
                display: flex;
                gap: 10px;
                flex-direction: column;
            }}
            
            .listen-btn {{
                text-decoration: none;
                padding: 10px 15px;
                border-radius: 30px;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                transition: all 0.3s ease;
                color: white !important;
            }}
            
            .spotify-btn {{ background-color: #1DB954; box-shadow: 0px 4px 10px rgba(29, 185, 84, 0.4); }}
            .spotify-btn:hover {{ background-color: #1ed760; transform: scale(1.05); }}
            
            .youtube-btn {{ background-color: #FF0000; box-shadow: 0px 4px 10px rgba(255, 0, 0, 0.4); }}
            .youtube-btn:hover {{ background-color: #ff3333; transform: scale(1.05); }}
            
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="colorful-title">🎶 Live Vibe Matcher</div>', unsafe_allow_html=True)
        
        # Display the custom Weather & Time Dashboard
        st.markdown(f"""
        <div class="weather-dashboard">
            <h2 style="margin:0; color: {text_color}; font-weight: 900;">{app_message}</h2>
            <p class="metric-text">📍 {resolved_city}, {country} &nbsp;|&nbsp; 🕒 Local Time: {local_time_formatted}</p>
            <p class="metric-text" style="font-size: 26px;">🌡️ {current_temp_c}°C / {current_temp_f}°F</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Determine Local Genre
        local_genre = country_to_genre.get(country, "pop")
        genre_df = recs[recs['track_genre'] == local_genre] if 'track_genre' in recs.columns else recs
        if genre_df.empty: genre_df = recs
            
        # PULL 10 SONGS
        if not genre_df.empty:
            top_10 = genre_df.sample(min(10, len(genre_df)))
            
            st.markdown(f"<h3 style='color: white; text-align: center; text-shadow: 1px 1px 4px rgba(0,0,0,0.2);'>Top 10 {local_genre.title()} Matches</h3>", unsafe_allow_html=True)
            
            for index, (i, row) in enumerate(top_10.iterrows()):
                # Create secure URL search queries for Spotify and YouTube
                search_query = urllib.parse.quote(f"{row['track_name']} {row['artists']}")
                spotify_link = f"https://open.spotify.com/search/{search_query}"
                youtube_link = f"https://www.youtube.com/results?search_query={search_query}"
                
                # HTML for the card with built-in buttons
                st.markdown(f"""
                <div class="vibe-card" style="animation-delay: {index * 0.1}s;">
                    <div class="song-info">
                        <p class="song-name">🎵 {row['track_name']}</p>
                        <p class="artist-name">🎤 {row['artists']}</p>
                        <p style="color: {accent_color}; font-size: 13px; font-weight: bold; margin-top: 5px;">Vibe: {local_genre.title()}</p>
                    </div>
                    <div class="btn-container">
                        <a href="{spotify_link}" target="_blank" class="listen-btn spotify-btn">🎧 Spotify</a>
                        <a href="{youtube_link}" target="_blank" class="listen-btn youtube-btn">▶️ YouTube</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("We could not find the perfect song, try another location!")
else:
    # Default State (Before searching)
    st.markdown(f"""
        <style>
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .stApp {{
            background: {bg_gradient};
            background-size: 300% 300%;
            animation: gradientShift 10s ease infinite;
        }}
        .colorful-title {{
            font-size: 45px;
            font-weight: 900;
            color: #ffffff;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        }}
        .colorful-subtitle {{
            font-size: 24px;
            color: #ffffff;
            text-align: center;
            font-weight: bold;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.2);
        }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="colorful-title">🎶 Live Vibe Matcher</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="colorful-subtitle">{app_message}</div>', unsafe_allow_html=True)