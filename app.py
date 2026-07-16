import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Colorful Vibe Check", page_icon="🌈", layout="centered")

# --- 2. LOAD DATA ---
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

# --- 3. DYNAMIC UI LOGIC ---
# Default colorful background if no city is searched yet
bg_color = "linear-gradient(45deg, #a18cd1 0%, #fbc2eb 100%)"
app_vibe = "🎶 Search a city to change the vibe!"

# Header and Search bar
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.4);'>🌈 The Colorful Vibe Check</h1>", unsafe_allow_html=True)
city = st.text_input("", placeholder="Enter a city (e.g., Ahmedabad, Chicago, Paris)...")

if city:
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"Could not find '{city}'. Try again!")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', 'United States')
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        # Change the background colors and text based on the weather!
        if current_temp > 25:
            bg_color = "linear-gradient(120deg, #f6d365 0%, #fda085 100%)" # Hot / Sunny Sunset
            app_vibe = f"🔥 It's a hot {current_temp}°C in {city.title()}! Bringing the high energy."
        elif current_temp > 10:
            bg_color = "linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)" # Pleasant / Breezy Spring
            app_vibe = f"🌤️ A beautiful {current_temp}°C in {city.title()}. Good vibes only."
        else:
            bg_color = "linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%)" # Cold / Chill Winter
            app_vibe = f"❄️ A chilly {current_temp}°C in {city.title()}. Acoustic and chill vibes."
            st.snow()
        
        # Inject the dynamic CSS for the entire page and the glass cards
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: {bg_color};
                background-attachment: fixed;
            }}
            .glass-card {{
                background: rgba(255, 255, 255, 0.3);
                border-radius: 16px;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.4);
                padding: 25px;
                margin: 15px 0px;
                color: #222;
                text-align: center;
                transition: transform 0.3s ease;
            }}
            .glass-card:hover {{
                transform: scale(1.02);
            }}
            .stTextInput > div > div > input {{
                border-radius: 30px;
                border: none;
                background: rgba(255, 255, 255, 0.6);
                padding: 15px;
                font-size: 16px;
            }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"<h3 style='text-align: center; color: #333; text-shadow: 1px 1px 2px rgba(255,255,255,0.5);'>{app_vibe}</h3>", unsafe_allow_html=True)
        
        # Filtering logic based on localized genre and weather
        local_genre = country_to_genre.get(country, "pop")
        genre_df = df[df['track_genre'] == local_genre] if 'track_genre' in df.columns else df
        if genre_df.empty: genre_df = df
        
        if current_temp > 25:
            recs = genre_df[(genre_df['energy'] > 0.6)]
        elif current_temp > 10:
            recs = genre_df[genre_df['valence'] > 0.5]
        else:
            recs = genre_df[(genre_df['energy'] < 0.5)]
            
        # Display the songs in the beautiful glass cards
        if not recs.empty:
            top_3 = recs.sample(min(3, len(recs)))
            for index, row in top_3.iterrows():
                st.markdown(f"""
                <div class="glass-card">
                    <h2 style="margin:0; color: #111;">🎵 {row['track_name']}</h2>
                    <p style="font-size: 20px; margin: 5px 0 0 0; color: #333;">🎤 {row['artists']}</p>
                    <p style="font-size: 14px; margin: 10px 0 0 0; color: #555;"><b>🌍 Region Mix:</b> {local_genre.title()}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Could not find a perfect match. Try another city!")
else:
    # Default CSS styling before the user searches for a city
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: {bg_color};
            background-attachment: fixed;
        }}
        .stTextInput > div > div > input {{
            border-radius: 30px;
            border: none;
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
        }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{app_vibe}</h3>", unsafe_allow_html=True)