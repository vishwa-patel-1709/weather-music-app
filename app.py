import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import urllib.parse
import pytz  # NEW: Added for exact time zone calculations

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Global Vibe Sync", page_icon="🎛️", layout="wide")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british", "United States": "pop", "Canada": "pop", 
    "Italy": "italian", "Sweden": "swedish", "Turkey": "turkish"
}

# --- 3. DYNAMIC UI LOGIC & ANIMATIONS ---
# Default moving gradient before search
bg_gradient = "linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%)"
app_message = "Search a city to sync the atmosphere."
weather_icon = "🌍"
theme_color = "#333333"

# --- SMART SEARCH BAR ---
col_spacer1, col_search, col_spacer2 = st.columns([1, 2, 1])
with col_search:
    user_input = st.text_input("🔍 Enter a City (e.g., Tokyo, Paris, Chicago):", placeholder="Where are you tuning in from?")

if user_input:
    search_city = user_input.split(',')[0].strip()
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"Oops! We couldn't find '{user_input}'. Please check the spelling.")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        resolved_city = geo_response['results'][0]['name']
        country = geo_response['results'][0].get('country', 'Unknown Location')
        # Grab the exact timezone string (e.g., 'Europe/Paris')
        timezone_str = geo_response['results'][0].get('timezone', 'UTC')
        
        # Fetch weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        
        current_temp_c = weather_data['current_weather']['temperature']
        current_temp_f = round((current_temp_c * 9/5) + 32, 1)
        
        # --- NEW EXACT TIME LOGIC ---
        try:
            target_tz = pytz.timezone(timezone_str)
            local_time_obj = datetime.now(target_tz)
            local_time_formatted = local_time_obj.strftime("%I:%M %p")
        except Exception:
            local_time_formatted = "Live"
        
        # --- ALGORITHM & COLOR LOGIC ---
        if current_temp_c > 25:
            bg_gradient = "linear-gradient(-45deg, #ff9a9e, #fecfef, #f6d365, #fda085)"
            app_message = f"Scorching Heat & High Energy"
            weather_icon = "☀️"
            theme_color = "#FF4500"
            recs = df[(df['energy'] > 0.6)]
        elif current_temp_c > 10:
            bg_gradient = "linear-gradient(-45deg, #84fab0, #8fd3f4, #a1c4fd, #c2e9fb)"
            app_message = f"Breezy & Euphoric Vibes"
            weather_icon = "🌤️"
            theme_color = "#0081C9"
            recs = df[df['valence'] > 0.5]
        else:
            bg_gradient = "linear-gradient(-45deg, #e0c3fc, #8ec5fc, #cfd9df, #e2ebf0)"
            app_message = f"Frosty & Acoustic Chills"
            weather_icon = "❄️"
            theme_color = "#4B4453"
            recs = df[(df['energy'] < 0.5)]

        # --- ADVANCED CSS INJECTION ---
        st.markdown(f"""
            <style>
            /* Fluid Background */
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .stApp {{
                background: {bg_gradient};
                background-size: 300% 300%;
                animation: gradientShift 15s ease infinite;
            }}
            
            /* Equalizer Animation */
            .equalizer {{
                display: flex;
                justify-content: center;
                align-items: flex-end;
                height: 40px;
                gap: 5px;
                margin-bottom: 20px;
            }}
            .bar {{
                width: 8px;
                background-color: {theme_color};
                border-radius: 5px;
                animation: bounce 1.2s ease infinite alternate;
            }}
            .bar:nth-child(1) {{ animation-delay: 0.1s; height: 10px; }}
            .bar:nth-child(2) {{ animation-delay: 0.4s; height: 35px; }}
            .bar:nth-child(3) {{ animation-delay: 0.2s; height: 20px; }}
            .bar:nth-child(4) {{ animation-delay: 0.6s; height: 40px; }}
            .bar:nth-child(5) {{ animation-delay: 0.3s; height: 15px; }}
            
            @keyframes bounce {{
                0% {{ transform: scaleY(0.3); opacity: 0.5; }}
                100% {{ transform: scaleY(1); opacity: 1; }}
            }}
            
            /* Typography & Dashboard */
            .main-title {{
                font-size: 50px; font-weight: 900; color: {theme_color};
                text-align: center; margin-bottom: 0px; letter-spacing: -1px;
            }}
            .dash-container {{
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border-radius: 20px; padding: 25px;
                text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.8);
                margin-bottom: 40px;
            }}
            
            /* Waterfall Card Animation */
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(50px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .music-card {{
                background: #ffffff;
                border-radius: 16px; padding: 20px; margin-bottom: 25px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.08);
                border-top: 5px solid {theme_color};
                opacity: 0; animation: slideIn 0.7s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .music-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.15);
            }}
            
            /* Data Science Progress Bars */
            .metric-label {{ font-size: 12px; font-weight: bold; color: #777; margin-bottom: 2px; text-transform: uppercase; }}
            .progress-bg {{ background-color: #eee; border-radius: 10px; height: 8px; width: 100%; margin-bottom: 10px; }}
            .progress-fill {{ background-color: {theme_color}; border-radius: 10px; height: 100%; transition: width 1s ease-in-out; }}
            
            /* Buttons */
            .btn-link {{
                display: inline-block; padding: 10px 20px; border-radius: 50px;
                font-weight: bold; text-decoration: none; color: white !important;
                font-size: 14px; transition: all 0.3s ease; margin-right: 10px; margin-top: 15px;
            }}
            .btn-spotify {{ background: #1DB954; box-shadow: 0 4px 15px rgba(29,185,84,0.3); }}
            .btn-youtube {{ background: #FF0000; box-shadow: 0 4px 15px rgba(255,0,0,0.3); }}
            .btn-link:hover {{ transform: scale(1.05) translateY(-2px); }}
            </style>
        """, unsafe_allow_html=True)

        # --- HEADER & DASHBOARD ---
        st.markdown(f"""
        <div class="equalizer">
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
        <h1 class="main-title">GLOBAL VIBE SYNC</h1>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="dash-container">
            <h2 style="margin:0; color: {theme_color}; font-weight: 800; font-size: 32px;">
                {weather_icon} {app_message}
            </h2>
            <hr style="border-top: 2px dashed rgba(0,0,0,0.1); margin: 15px 0;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div><span style="color:#666; font-size:14px;">LOCATION</span><br><b style="font-size:20px; color:#222;">{resolved_city}, {country}</b></div>
                <div><span style="color:#666; font-size:14px;">LOCAL TIME</span><br><b style="font-size:20px; color:#222;">{local_time_formatted}</b></div>
                <div><span style="color:#666; font-size:14px;">TEMPERATURE</span><br><b style="font-size:20px; color:#222;">{current_temp_c}°C / {current_temp_f}°F</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- RECOMMENDATION ENGINE (Up to 10 Tracks) ---
        local_genre = country_to_genre.get(country, "pop")
        genre_df = recs[recs['track_genre'] == local_genre] if 'track_genre' in recs.columns else recs
        if genre_df.empty: genre_df = recs
            
        if not genre_df.empty:
            top_tracks = genre_df.sample(min(10, len(genre_df)))
            
            st.markdown(f"<h3 style='text-align: center; color: #333; margin-bottom: 25px;'>Top {len(top_tracks)} Matches for {local_genre.title()}</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            for index, (i, row) in enumerate(top_tracks.iterrows()):
                search_query = urllib.parse.quote(f"{row['track_name']} {row['artists']}")
                spotify_url = f"https://open.spotify.com/search/{search_query}"
                youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
                
                energy_pct = int(row.get('energy', 0.5) * 100)
                happiness_pct = int(row.get('valence', 0.5) * 100)
                
                card_html = f"""<div class="music-card" style="animation-delay: {index * 0.15}s;">
<h3 style="margin: 0 0 5px 0; color: #222; font-size: 22px;">🎵 {row['track_name']}</h3>
<p style="margin: 0 0 15px 0; color: #666; font-size: 16px;">🎤 {row['artists']}</p>
<div class="metric-label">Audio Energy ({energy_pct}%)</div>
<div class="progress-bg"><div class="progress-fill" style="width: {energy_pct}%;"></div></div>
<div class="metric-label">Vibe / Happiness ({happiness_pct}%)</div>
<div class="progress-bg"><div class="progress-fill" style="width: {happiness_pct}%; background-color: #FFA500;"></div></div>
<div style="margin-top: 15px;">
<a href="{spotify_url}" target="_blank" class="btn-link btn-spotify">🎧 Listen on Spotify</a>
<a href="{youtube_url}" target="_blank" class="btn-link btn-youtube">▶️ Watch on YouTube</a>
</div>
</div>"""
                
                if index % 2 == 0:
                    with col1:
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    with col2:
                        st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning("We could not find the perfect song, try another location!")
else:
    # --- DEFAULT STATE (Before Searching) ---
    st.markdown(f"""
        <style>
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .stApp {{
            background: linear-gradient(-45deg, #a18cd1, #fbc2eb, #84fab0, #8fd3f4);
            background-size: 300% 300%;
            animation: gradientShift 15s ease infinite;
        }}
        .main-title {{
            font-size: 60px; font-weight: 900; color: white;
            text-align: center; text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            margin-top: 10vh;
        }}
        .sub-title {{
            font-size: 24px; color: white; text-align: center;
            font-weight: bold; text-shadow: 1px 1px 5px rgba(0,0,0,0.2);
        }}
        </style>
        <h1 class="main-title">GLOBAL VIBE SYNC</h1>
        <p class="sub-title">Enter a city above to connect the weather to the music.</p>
    """, unsafe_allow_html=True)