import streamlit as st
import pandas as pd
import random
import time
import numpy as np

st.set_page_config(
    page_title="EchoMesh Rescue Dashboard",
    layout="wide"
)

# ---------- Dark Theme Styling ----------
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stDataFrame {
        background-color: #1c1f26;
    }
    .stButton > button,
    .stButton > button:hover,
    .stButton > button:active,
    .stButton > button:focus {
        cursor: default !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚑 EchoMesh Rescue Coordination Dashboard")

BASE_LAT = 13.0827
BASE_LON = 80.2707

tasks = [
    "Search Operation",
    "Medical Support",
    "Evacuation",
    "Supply Distribution",
    "Damage Assessment"
]

statuses = ["Active", "Moving", "Idle", "Emergency"]

# ---------- Initialize Teams ----------
if "teams" not in st.session_state:
    teams = []

    for i in range(10):
        team = {
            "Team": f"Rescue_{i+1}",
            "Latitude": BASE_LAT + random.uniform(-0.01, 0.01),
            "Longitude": BASE_LON + random.uniform(-0.01, 0.01),
            "Task": random.choice(tasks),
            "Status": random.choice(statuses),
            "Battery": random.randint(40, 100)
        }

        teams.append(team)

    st.session_state.teams = teams

teams = st.session_state.teams

# ---------- Movement Simulation ----------
for team in teams:
    team["Latitude"] += np.random.uniform(-0.0005, 0.0005)
    team["Longitude"] += np.random.uniform(-0.0005, 0.0005)

df = pd.DataFrame(teams)

# ---------- Layout ----------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📍 Live Team Locations")
    map_df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    st.map(map_df)

with col2:
    st.subheader("📋 Team Status Table")
    st.dataframe(df, use_container_width=True)

# ---------- Alerts ----------
st.subheader("🚨 Emergency Alerts")

for team in teams:
    if team["Status"] == "Emergency":
        st.error(f"{team['Team']} requires immediate assistance!")

# ---------- Auto Refresh ----------
time.sleep(2)
st.rerun()