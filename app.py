import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Vibe & Weather Matcher", page_icon="🎧", layout="centered")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british", "United States": "pop"
}

# --- 3. DYNAMIC UI & ANIMATIONS LOGIC ---
# Default moving gradient before search
bg_gradient = "linear-gradient(-45deg, #ff9a9e, #fecfef, #a1c4fd, #c2e9fb)"
app_message = "Type a city to unlock the vibes!"
text_color = "#845EC2" 
accent_color = "#FF9671"

st.markdown("""
    <style>
    /* Floating Music Notes Animation */
    @keyframes floatNotes {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-20vh) rotate(360deg); opacity: 0; }
    }
    .music-note {
        position: fixed;
        color: rgba(255, 255, 255, 0.6);
        font-size: 30px;
        animation: floatNotes 10s linear infinite;
        z-index: 0;
    }
    .note-1 { left: 10%; animation-duration: 8s; animation-delay: 1s; }
    .note-2 { left: 30%; animation-duration: 12s; animation-delay: 3s; font-size: 40px; }
    .note-3 { left: 70%; animation-duration: 9s; animation-delay: 0s; font-size: 25px; }
    .note-4 { left: 85%; animation-duration: 11s; animation-delay: 2s; font-size: 35px; }
    </style>
    <div class="music-note note-1">🎵</div>
    <div class="music-note note-2">🎶</div>
    <div class="music-note note-3">🎧</div>
    <div class="music-note note-4">🎸</div>
""", unsafe_allow_html=True)

# Smart Search Bar (Allows "City" or "City, Country")
user_input = st.text_input("🔍 Search City or 'City, Country' (e.g., Paris, France):", placeholder="Enter location here...")

if user_input:
    # If the user types a comma, we grab the first part for the API to ensure a safe search
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
        
        # Fetch weather WITH automatic timezone handling
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        weather_data = requests.get(weather_url).json()
        
        # Temperature Logic (Celsius & Fahrenheit)
        current_temp_c = weather_data['current_weather']['temperature']
        current_temp_f = round((current_temp_c * 9/5) + 32, 1)
        
        # Time Logic
        raw_time = weather_data['current_weather']['time'] # Format: 2023-10-25T14:00
        try:
            local_time_obj = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M")
            local_time_formatted = local_time_obj.strftime("%I:%M %p") # Converts to 02:30 PM
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

        # --- FANCY CSS ANIMATIONS & TRANSITIONS ---
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
                position: relative;
                z-index: 10;
            }}
            
            .weather-dashboard {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                border: 3px solid {accent_color};
                position: relative;
                z-index: 10;
            }}
            
            .metric-text {{
                font-size: 22px;
                font-weight: bold;
                color: {text_color};
                margin: 5px 0;
            }}
            
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .white-card {{
                background-color: #ffffff;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                text-align: center;
                border-left: 8px solid {accent_color};
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
                opacity: 0; 
                animation: slideUp 0.6s ease forwards;
                transition: transform 0.3s ease;
                position: relative;
                z-index: 10;
            }}
            
            .white-card:hover {{
                transform: scale(1.03);
                box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.15);
            }}
            
            .song-name {{ font-size: 24px; font-weight: 900; color: {text_color}; margin: 0; }}
            .artist-name {{ font-size: 18px; color: #555; margin-top: 5px; font-weight: bold; }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="colorful-title">🎶 Live Vibe Matcher</div>', unsafe_allow_html=True)
        
        # Display the custom Weather & Time Dashboard
        st.markdown(f"""
        <div class="weather-dashboard">
            <h2 style="margin:0; color: {text_color}; font-weight: 900;">{app_message}</h2>
            <p class="metric-text">📍 {resolved_city}, {country}</p>
            <p class="metric-text">🕒 Local Time: {local_time_formatted}</p>
            <p class="metric-text">🌡️ Temperature: {current_temp_c}°C / {current_temp_f}°F</p>
        </div>
        """, unsafe_allow_html=True)
        
        local_genre = country_to_genre.get(country, "pop")
        genre_df = recs[recs['track_genre'] == local_genre] if 'track_genre' in recs.columns else recs
        if genre_df.empty: genre_df = recs
            
        if not genre_df.empty:
            top_3 = genre_df.sample(min(3, len(genre_df)))
            
            for index, (i, row) in enumerate(top_3.iterrows()):
                st.markdown(f"""
                <div class="white-card" style="animation-delay: {index * 0.15}s;">
                    <p class="song-name">🎵 {row['track_name']}</p>
                    <p class="artist-name">🎤 By: {row['artists']}</p>
                    <p style="color: {accent_color}; font-size: 14px; font-weight: bold; margin-top: 10px;">
                        Regional Vibe: {local_genre.title()}
                    </p>
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
            position: relative;
            z-index: 10;
        }}
        .colorful-subtitle {{
            font-size: 24px;
            color: #ffffff;
            text-align: center;
            font-weight: bold;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 10;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="colorful-title">🎶 Live Vibe Matcher</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="colorful-subtitle">{app_message}</div>', unsafe_allow_html=True)