import streamlit as st
import pandas as pd
import requests
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Weather & Music Vibes Analyzer 🌦️🎶")
st.write("Does the weather affect the kind of music people listen to? Let's find out!")

# 1. Load Music Data
@st.cache_data
def load_music_data():
    return pd.read_csv('dataset.csv')

df = load_music_data()
st.success("✅ Spotify track data loaded!")

# 2. Fetch Weather Data
url = "https://archive-api.open-meteo.com/v1/archive?latitude=51.5074&longitude=-0.1278&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_mean,precipitation_sum&timezone=auto"
response = requests.get(url)
weather_df = pd.DataFrame(response.json()['daily'])
st.success("✅ Weather data from Open-Meteo loaded!")

# 3. Merge Data 
analysis_df = df[['track_name', 'artists', 'danceability', 'energy', 'valence', 'tempo']].copy()
analysis_df['date'] = np.random.choice(weather_df['time'], size=len(analysis_df))
merged_df = pd.merge(analysis_df, weather_df, left_on='date', right_on='time')

# --- NEW INTERACTIVE SECTION ---

st.subheader("Explore the Data")
st.write("Choose a musical feature to compare against the daily temperature:")

# Create a dropdown menu
feature_choice = st.selectbox(
    "Select Audio Feature:",
    ("energy", "danceability", "valence", "tempo")
)

# 4. Display the Interactive Graph
fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(
    data=merged_df.sample(500), 
    x='temperature_2m_mean', 
    y=feature_choice, # THIS NOW CHANGES BASED ON THE MENU!
    scatter_kws={'alpha':0.5, 'color': 'skyblue'}, 
    line_kws={'color': 'red', 'linewidth': 2},
    ax=ax
)
ax.set_xlabel('Mean Temperature (°C)')
ax.set_ylabel(f'Song {feature_choice.capitalize()} level')

# Tell Streamlit to draw the plot
st.pyplot(fig)