import streamlit as st
import pandas as pd
import random
import time
from ai_model import ai_model
import numpy as np

st.set_page_config(page_title="Rescue Coordination Dashboard", layout="wide")

st.markdown("""
    <style>
    .stButton > button,
    .stButton > button:hover,
    .stButton > button:active,
    .stButton > button:focus {
        cursor: default !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚑 Rescue Team Coordination Dashboard")

# Base location (example area)
BASE_LAT = 13.0827
BASE_LON = 80.2707

teams = []

tasks = [
    "Search Operation",
    "Medical Assistance",
    "Evacuation Support",
    "Supply Distribution",
    "Damage Assessment"
]

statuses = ["Active", "In Transit", "Idle", "Emergency"]

# Generate team data
for i in range(1, 11):
    lat = BASE_LAT + random.uniform(-0.01, 0.01)
    lon = BASE_LON + random.uniform(-0.01, 0.01)
    battery = random.randint(40, 100)
    signal_strength = random.uniform(0.5, 1.0)  # Assume good signal
    distance_from_base = np.sqrt((lat - BASE_LAT)**2 + (lon - BASE_LON)**2)
    num_neighbors = random.randint(1, 5)
    avg_neighbor_battery = random.randint(40, 100)
    active_neighbors = random.randint(1, num_neighbors)

    # AI Predictions
    will_fail = ai_model.predict_device_failure(
        lat, lon, battery, signal_strength, distance_from_base,
        num_neighbors, avg_neighbor_battery, active_neighbors
    )
    path_cost = ai_model.predict_path_cost(
        lat, lon, battery, signal_strength, distance_from_base,
        num_neighbors, avg_neighbor_battery, active_neighbors
    )

    team = {
        "Team": f"Rescue Team {i}",
        "Latitude": round(lat, 6),
        "Longitude": round(lon, 6),
        "Task": random.choice(tasks),
        "Status": random.choice(statuses),
        "Battery (%)": battery,
        "AI Reliability": "High" if not will_fail else "Low",
        "AI Route Cost": round(path_cost, 2) if path_cost else "N/A"
    }
    teams.append(team)

df = pd.DataFrame(teams)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Team Locations")
    st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

with col2:
    st.subheader("📋 Team Status")
    st.dataframe(df)

st.subheader("🤖 AI Insights")
st.markdown("**Reliability Analysis:** Teams with 'Low' reliability may need battery checks or repositioning.")
st.markdown("**Route Optimization:** Lower AI Route Cost indicates better positioning for emergency response.")

low_reliability_teams = [team for team in teams if team["AI Reliability"] == "Low"]
if low_reliability_teams:
    st.warning(f"⚠️ Teams with low reliability: {', '.join([t['Team'] for t in low_reliability_teams])}")

st.subheader("🚨 System Alerts")

for team in teams:
    if team["Status"] == "Emergency":
        st.error(f"{team['Team']} requires immediate assistance!")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.experimental_rerun()
