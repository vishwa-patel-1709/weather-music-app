import streamlit as st
import pandas as pd
import requests

# --- 1. FANCY PAGE SETUP ---
st.set_page_config(page_title="Global Vibe Check", page_icon="🌎", layout="centered")

# Inject Custom CSS for a beautiful, modern UI
st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-weight: bold;
        background: -webkit-linear-gradient(45deg, #1DB954, #191414);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }
    .stTextInput>div>div>input {
        border-radius: 50px;
        border: 2px solid #1DB954;
        padding: 15px;
    }
    .song-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #1DB954;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🌎 The Global Vibe Check</p>', unsafe_allow_html=True)
st.write("<center>Type a city to get live weather and locally-tailored music recommendations.</center>", unsafe_allow_html=True)
st.write("---")

# --- 2. LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

# --- 3. LANGUAGE MAPPING LOGIC ---
# Map countries to the genres available in our specific Kaggle dataset
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

# --- 4. INTERACTIVE SEARCH & LOGIC ---
city = st.text_input("🔍 Search any city (e.g., Ahmedabad, Chicago, Tokyo):", placeholder="Press enter to search...")

if city:
    # Get Location & Country
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"Could not find '{city}'. Check the spelling and try again!")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', 'United States')
        
        # Get Live Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        # Determine Local Genre
        local_genre = country_to_genre.get(country, "pop") # Defaults to 'pop' if country isn't in our list
        
        # UI: Display Weather and Location
        col1, col2, col3 = st.columns(3)
        col1.metric("📍 Location", f"{city.title()}")
        col2.metric("🌡️ Temperature", f"{current_temp}°C")
        col3.metric("🎧 Vibe Region", f"{country}")
        
        st.write("---")
        
        # Logic: Filter by the local genre FIRST
        if 'track_genre' in df.columns:
            genre_df = df[df['track_genre'] == local_genre]
            # Fallback if genre is empty
            if genre_df.empty:
                genre_df = df 
        else:
            genre_df = df
            
        # Logic: Filter the local music by the weather!
        if current_temp > 25:
            st.subheader(f"🔥 It's hot in {city.title()}! High-energy {local_genre.title()} tracks:")
            recommendations = genre_df[(genre_df['energy'] > 0.6)]
        elif current_temp > 10:
            st.subheader(f"🌤️ Beautiful weather in {city.title()}. Upbeat {local_genre.title()} tracks:")
            recommendations = genre_df[genre_df['valence'] > 0.5]
        else:
            st.subheader(f"❄️ It's chilly in {city.title()}. Chill, acoustic {local_genre.title()} tracks:")
            st.snow() # Adds a cool snow animation to the screen!
            recommendations = genre_df[(genre_df['energy'] < 0.5)]
            
        # Display the localized recommendations in fancy cards
        if not recommendations.empty:
            top_3 = recommendations.sample(min(3, len(recommendations)))
            
            for index, row in top_3.iterrows():
                # Using HTML inside markdown to create a clean, modern card look
                st.markdown(f"""
                <div class="song-card">
                    <h3 style="margin-bottom: 0px; color: white;">🎵 {row['track_name']}</h3>
                    <p style="color: #1DB954; font-size: 18px; margin-top: 5px;">👤 {row['artists']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("We couldn't find the perfect local match in our database. Try another city!")