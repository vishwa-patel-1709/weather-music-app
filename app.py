import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Music & Weather Matcher", page_icon="🌤️", layout="centered")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

# Simple language for countries
country_to_genre = {
    "India": "indian", "France": "french", "Germany": "german", "Spain": "spanish",
    "Mexico": "latino", "Japan": "j-pop", "South Korea": "k-pop", "Brazil": "brazil",
    "United Kingdom": "british",
}

# --- 3. DYNAMIC WHITE & COLORFUL UI ---
# Default to a clean white background
bg_color = "#ffffff"
app_message = "Search for a city to see the magic!"
text_color = "#ff4b4b" # Colorful default text!

city = st.text_input("🔍 Type a City Name (like Tokyo, Paris, or Mumbai):", placeholder="Enter city name here...")

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
        
        # Change background based on weather, but keep it light and bright!
        if current_temp > 25:
            bg_color = "linear-gradient(to right, #ffecd2 0%, #fcb69f 100%)" # Warm / Sunny
            app_message = f"🔥 It is hot! {current_temp}°C in {city.title()}"
            text_color = "#ff4500" # Orange-red text
            recs = df[(df['energy'] > 0.6)]
        elif current_temp > 10:
            bg_color = "linear-gradient(to right, #e0c3fc 0%, #8ec5fc 100%)" # Cool / Pleasant
            app_message = f"🌤️ Nice and pleasant! {current_temp}°C in {city.title()}"
            text_color = "#4a90e2" # Bright Blue text
            recs = df[df['valence'] > 0.5]
        else:
            bg_color = "linear-gradient(to right, #cfd9df 0%, #e2ebf0 100%)" # Cold / Snowy
            app_message = f"❄️ Brrr, it is cold! {current_temp}°C in {city.title()}"
            text_color = "#008b8b" # Dark Cyan text
            recs = df[(df['energy'] < 0.5)]

        # Apply custom CSS for the background and colorful text
        st.markdown(f"""
            <style>
            .stApp {{
                background: {bg_color};
                color: #333333;
            }}
            .colorful-title {{
                font-size: 45px;
                font-weight: bold;
                color: {text_color};
                text-align: center;
                margin-bottom: 10px;
            }}
            .colorful-subtitle {{
                font-size: 25px;
                color: {text_color};
                text-align: center;
                margin-bottom: 30px;
                font-weight: bold;
            }}
            .white-card {{
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
                border-top: 5px solid {text_color};
            }}
            .song-name {{
                font-size: 24px;
                font-weight: bold;
                color: {text_color};
                margin: 0;
            }}
            .artist-name {{
                font-size: 18px;
                color: #555555;
                margin-top: 5px;
            }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="colorful-title">🌤️ Music & Weather Matcher</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="colorful-subtitle">{app_message}</div>', unsafe_allow_html=True)
        
        # Determine Local Genre
        local_genre = country_to_genre.get(country, "pop")
        genre_df = recs[recs['track_genre'] == local_genre] if 'track_genre' in recs.columns else recs
        if genre_df.empty: genre_df = recs
            
        if not genre_df.empty:
            top_3 = genre_df.sample(min(3, len(genre_df)))
            for index, row in top_3.iterrows():
                st.markdown(f"""
                <div class="white-card">
                    <p class="song-name">🎵 {row['track_name']}</p>
                    <p class="artist-name">🎤 By: {row['artists']}</p>
                    <p style="color: #888; font-size: 14px; margin-top: 10px;">Vibe: {local_genre.title()}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("We could not find the perfect song, try another city!")
else:
    # Default White UI before searching
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg_color};
        }}
        .colorful-title {{
            font-size: 45px;
            font-weight: bold;
            color: #ff4b4b;
            text-align: center;
            margin-bottom: 10px;
        }}
        .colorful-subtitle {{
            font-size: 20px;
            color: #ff4b4b;
            text-align: center;
            margin-bottom: 30px;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="colorful-title">🌤️ Music & Weather Matcher</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="colorful-subtitle">{app_message}</div>', unsafe_allow_html=True)