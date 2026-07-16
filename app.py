import streamlit as st
import pandas as pd
import requests
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set the page to be a bit wider
st.set_page_config(page_title="Music & Weather", layout="wide")

st.title("Weather & Music Vibes Analyzer 🌦️🎶")
st.write("Does the weather affect the kind of music people listen to? Let's find out!")

# 1. Load Data
@st.cache_data
def load_music_data():
    return pd.read_csv('dataset.csv')

df = load_music_data()

@st.cache_data
def load_weather_data():
    url = "https://archive-api.open-meteo.com/v1/archive?latitude=51.5074&longitude=-0.1278&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_mean,precipitation_sum&timezone=auto"
    response = requests.get(url)
    return pd.DataFrame(response.json()['daily'])

weather_df = load_weather_data()

# Merge Data 
analysis_df = df[['track_name', 'artists', 'danceability', 'energy', 'valence', 'tempo']].copy()
analysis_df['date'] = np.random.choice(weather_df['time'], size=len(analysis_df))
merged_df = pd.merge(analysis_df, weather_df, left_on='date', right_on='time')

# --- NEW SIDEBAR INTERACTIVITY ---
st.sidebar.header("Control Panel 🎛️")

# Dropdown menu in the sidebar
feature_choice = st.sidebar.selectbox(
    "1. Select Audio Feature:",
    ("energy", "danceability", "valence", "tempo")
)

# Temperature Slider in the sidebar
min_temp = float(merged_df['temperature_2m_mean'].min())
max_temp = float(merged_df['temperature_2m_mean'].max())

temp_range = st.sidebar.slider(
    "2. Filter by Temperature Range (°C):",
    min_value=min_temp,
    max_value=max_temp,
    value=(min_temp, max_temp) # Default to showing everything
)

# Filter the dataframe based on the slider
filtered_df = merged_df[
    (merged_df['temperature_2m_mean'] >= temp_range[0]) & 
    (merged_df['temperature_2m_mean'] <= temp_range[1])
]

# --- MAIN PAGE DASHBOARD ---

# Display some quick metrics at the top
col1, col2 = st.columns(2)
col1.metric("Total Songs Displayed", len(filtered_df))
col2.metric(f"Average {feature_choice.capitalize()}", round(filtered_df[feature_choice].mean(), 3))

# Display the Graph
fig, ax = plt.subplots(figsize=(10, 5))
sns.regplot(
    data=filtered_df.sample(min(500, len(filtered_df))), # Safe sampling
    x='temperature_2m_mean', 
    y=feature_choice, 
    scatter_kws={'alpha':0.5, 'color': '#1DB954'}, # Spotify Green!
    line_kws={'color': 'white', 'linewidth': 2},
    ax=ax
)
ax.set_xlabel('Mean Temperature (°C)')
ax.set_ylabel(f'Song {feature_choice.capitalize()} level')

# Make the chart look sleek with a dark background theme
fig.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')
ax.xaxis.label.set_color('white')
ax.yaxis.label.set_color('white')
ax.tick_params(colors='white')

st.pyplot(fig)

# Data Toggle
st.write("---")
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df[['track_name', 'artists', 'temperature_2m_mean', feature_choice]])