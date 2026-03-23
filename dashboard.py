import streamlit as st
import pandas as pd
import random
import time

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
    team = {
        "Team": f"Rescue Team {i}",
        "Latitude": BASE_LAT + random.uniform(-0.01, 0.01),
        "Longitude": BASE_LON + random.uniform(-0.01, 0.01),
        "Task": random.choice(tasks),
        "Status": random.choice(statuses),
        "Battery (%)": random.randint(40, 100)
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

st.subheader("🚨 System Alerts")

for team in teams:
    if team["Status"] == "Emergency":
        st.error(f"{team['Team']} requires immediate assistance!")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.experimental_rerun()
