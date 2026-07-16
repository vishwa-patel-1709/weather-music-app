import streamlit as st
import pandas as pd
import requests
import random

# --- PAGE SETUP (Makes it look fancy) ---
st.set_page_config(page_title="Live Vibe Check", page_icon="🎧", layout="centered")

st.title("🎧 The Live Weather Vibe Check")
st.write("Type in a city, get the live weather, and let our algorithm recommend the perfect tracks for right now.")

# --- LOAD DATA ---
@st.cache_data
def load_music():
    return pd.read_csv('dataset.csv')

df = load_music()

# --- INTERACTIVE SEARCH ---
st.markdown("### 🌍 Where are you right now?")
city = st.text_input("Enter any city in the world (e.g., London, Tokyo, Mumbai):", "")

if city:
    # 1. Geocoding: Turn the city name into coordinates using a free API
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    geo_response = requests.get(geo_url).json()
    
    if 'results' not in geo_response:
        st.error(f"Could not find the city '{city}'. Try another one!")
    else:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        country = geo_response['results'][0].get('country', '')
        
        # 2. Get Live Weather for those coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        current_temp = weather_data['current_weather']['temperature']
        
        st.success("Live data successfully fetched!")
        
        # --- FANCY DISPLAY ---
        st.markdown("---")
        
        # Show weather in big metric cards
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Location", f"{city.title()}, {country}")
        with col2:
            st.metric("Live Temperature", f"{current_temp}°C")
            
        st.markdown("---")
        
        # 3. The Recommender Algorithm
        st.subheader("🎶 Your Real-Time Playlist")
        
        # Logic: Hotter weather = higher energy/danceability. Colder weather = lower energy/acoustic.
        if current_temp > 25:
            st.write("🔥 It's hot out! Recommending high-energy, danceable tracks:")
            recommendations = df[(df['energy'] > 0.7) & (df['danceability'] > 0.7)]
        elif current_temp > 15:
            st.write("🌤️ It's pleasant. Recommending upbeat, happy tracks:")
            recommendations = df[df['valence'] > 0.6]
        else:
            st.write("❄️ It's chilly. Recommending chill, acoustic tracks:")
            recommendations = df[(df['energy'] < 0.5) & (df['danceability'] < 0.5)]
            
        # Pick 3 random songs from our filtered list so it's different every time
        if not recommendations.empty:
            top_3 = recommendations.sample(3)
            
            # Display them beautifully
            for index, row in top_3.iterrows():
                with st.container():
                    st.markdown(f"### 🎵 **{row['track_name']}**")
                    st.markdown(f"**Artist:** {row['artists']}")
                    st.write("") # Add a little space between songs
        else:
            st.write("Could not find the perfect match for this weather in our dataset!")