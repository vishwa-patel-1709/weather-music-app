import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Dynamic Vibe Matcher", page_icon="🎵", layout="centered")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british",
}

# --- 3. DYNAMIC ANIMATED UI LOGIC ---
# Default moving gradient before search
bg_gradient = "linear-gradient(-45deg, #fbc2eb, #a6c1ee, #fbc2eb, #a6c1ee)"
app_message = "Type a city to watch the vibes shift!"
text_color = "#845EC2" 
accent_color = "#FF9671"

city = st.text_input("🔍 Where are you? (e.g., Tokyo, London, Mumbai):", placeholder="Enter city name here...")

if city:
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error("Oops! We couldn't find that city. Please try another one.")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', 'United States')
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        # Change the moving gradient and colors based on weather
        if current_temp > 25:
            # Hot: Moving oranges, yellows, and warm pinks
            bg_gradient = "linear-gradient(-45deg, #ff9a9e, #fecfef, #f6d365, #fda085)"
            app_message = f"🔥 Hot & Sunny! {current_temp}°C in {city.title()}"
            text_color = "#FF5E7E"
            accent_color = "#FF9A44"
            recs = df[(df['energy'] > 0.6)]
        elif current_temp > 10:
            # Pleasant: Moving sky blues and soft greens
            bg_gradient = "linear-gradient(-45deg, #a1c4fd, #c2e9fb, #84fab0, #8fd3f4)"
            app_message = f"🌤️ Perfect Weather! {current_temp}°C in {city.title()}"
            text_color = "#0081C9"
            accent_color = "#5CDB95"
            recs = df[df['valence'] > 0.5]
        else:
            # Cold: Moving icy blues and lavenders
            bg_gradient = "linear-gradient(-45deg, #e0c3fc, #8ec5fc, #cfd9df, #e2ebf0)"
            app_message = f"❄️ Brrr, it's chilly! {current_temp}°C in {city.title()}"
            text_color = "#4B4453"
            accent_color = "#008F7A"
            recs = df[(df['energy'] < 0.5)]

        # --- FANCY CSS ANIMATIONS & TRANSITIONS ---
        st.markdown(f"""
            <style>
            /* 1. The Moving Background Animation */
            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            .stApp {{
                background: {bg_gradient};
                background-size: 300% 300%;
                animation: gradientShift 12s ease infinite;
                color: #333333;
            }}
            
            /* 2. Colorful, Popping Typography */
            .colorful-title {{
                font-size: 48px;
                font-weight: 900;
                color: {text_color};
                text-align: center;
                margin-bottom: 5px;
                text-shadow: 2px 2px 4px rgba(255,255,255,0.6);
            }}
            .colorful-subtitle {{
                font-size: 22px;
                color: {text_color};
                text-align: center;
                margin-bottom: 35px;
                font-weight: 700;
                background: rgba(255,255,255,0.4);
                display: inline-block;
                padding: 10px 25px;
                border-radius: 30px;
            }}
            
            /* 3. The Fade-In & Float-Up Card Animation */
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(40px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            /* 4. White Cards with Hover Transitions */
            .animated-card {{
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                text-align: center;
                border-bottom: 6px solid {accent_color};
                box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.05);
                opacity: 0; 
                animation: fadeInUp 0.8s ease forwards;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            /* The Hover Effect */
            .animated-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0px 15px 30px rgba(0, 0, 0, 0.15);
            }}
            
            .song-name {{
                font-size: 26px;
                font-weight: 800;
                color: {text_color};
                margin: 0;
            }}
            .artist-name {{
                font-size: 18px;
                color: #666666;
                margin-top: 5px;
                font-weight: 600;
            }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="colorful-title">🎶 Vibe & Weather Matcher</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center;"><div class="colorful-subtitle">{app_message}</div></div>', unsafe_allow_html=True)
        
        local_genre = country_to_genre.get(country, "pop")
        genre_df = recs[recs['track_genre'] == local_genre] if 'track_genre' in recs.columns else recs
        if genre_df.empty: genre_df = recs
            
        if not genre_df.empty:
            top_3 = genre_df.sample(min(3, len(genre_df)))
            
            # Using enumerate to create a staggered entrance effect!
            for index, (i, row) in enumerate(top_3.iterrows()):
                st.markdown(f"""
                <div class="animated-card" style="animation-delay: {index * 0.2}s;">
                    <p class="song-name">🎵 {row['track_name']}</p>
                    <p class="artist-name">🎤 By: {row['artists']}</p>
                    <span style="background-color: {accent_color}; color: white; padding: 5px 15px; border-radius: 15px; font-size: 13px; font-weight: bold; margin-top: 15px; display: inline-block;">
                        Local Vibe: {local_genre.title()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("We could not find the perfect song, try another city!")
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
            animation: gradientShift 12s ease infinite;
        }}
        .colorful-title {{
            font-size: 48px;
            font-weight: 900;
            color: {text_color};
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.6);
        }}
        .colorful-subtitle {{
            font-size: 22px;
            color: {text_color};
            text-align: center;
            font-weight: 700;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="colorful-title">🎶 Vibe & Weather Matcher</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="colorful-subtitle">{app_message}</div>', unsafe_allow_html=True)