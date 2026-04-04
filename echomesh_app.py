import streamlit as st
import pandas as pd
import numpy as np
import math
import pydeck as pdk
import json
import os
import random
from datetime import datetime
from ai_model import ai_model

# ---------------- FIREBASE SETUP ----------------

FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "serviceAccountKey.json")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "").strip()
DATA_FILE = os.getenv("ECHO_DATA_FILE", "local_requests.json")

FIREBASE_ENABLED = False

try:
    import firebase_admin
    from firebase_admin import credentials, db
    
    if FIREBASE_DATABASE_URL and os.path.exists(FIREBASE_KEY_PATH):
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_KEY_PATH)
            firebase_admin.initialize_app(cred, {
                "databaseURL": FIREBASE_DATABASE_URL
            })
        ref = db.reference("requests")
        FIREBASE_ENABLED = True
except (FileNotFoundError, ImportError, Exception):
    pass

# Local data storage fallback
if not FIREBASE_ENABLED:
    class LocalDB:
        def get(self):
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            return {}
        
        def push(self, data):
            existing = self.get()
            new_id = str(max([int(k) for k in existing.keys()], default=0) + 1)
            existing[new_id] = data
            with open(DATA_FILE, 'w') as f:
                json.dump(existing, f, indent=2)
            return new_id
        
        def child(self, key):
            return LocalChild(key)
    
    class LocalChild:
        def __init__(self, key):
            self.key = key
        
        def update(self, data):
            existing = LocalDB().get()
            if self.key in existing:
                existing[self.key].update(data)
                with open(DATA_FILE, 'w') as f:
                    json.dump(existing, f, indent=2)
    
    ref = LocalDB()

# Initialize demo data if empty
def init_demo_data():
    if not ref.get():
        demo_data = {
            "1": {
                "lat": 13.0827,
                "lon": 80.2707,
                "message": "Person injured in building collapse",
                "priority": "HIGH",
                "status": "Pending",
                "team": "Not Assigned",
                "chat": [],
                "timestamp": datetime.now().isoformat()
            },
            "2": {
                "lat": 13.0850,
                "lon": 80.2750,
                "message": "Urgent medical help needed",
                "priority": "HIGH",
                "status": "Assigned",
                "team": "Rescue_2",
                "chat": ["Rescue: ETA 5 minutes"],
                "timestamp": datetime.now().isoformat()
            },
            "3": {
                "lat": 13.0800,
                "lon": 80.2650,
                "message": "Help needed immediately",
                "priority": "MEDIUM",
                "status": "Pending",
                "team": "Not Assigned",
                "chat": [],
                "timestamp": datetime.now().isoformat()
            }
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(demo_data, f, indent=2)

# ---------------- PAGE ----------------

st.set_page_config(layout="wide")

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

# Initialize demo data
init_demo_data()

BASE_LAT = 13.0827
BASE_LON = 80.2707

# ---------------- RESCUE TEAMS ----------------

teams = [
    {"Team": "Rescue_1", "lat": 13.0827, "lon": 80.2707},
    {"Team": "Rescue_2", "lat": 13.0800, "lon": 80.2650},
    {"Team": "Rescue_3", "lat": 13.0850, "lon": 80.2750},
    {"Team": "Rescue_4", "lat": 13.0780, "lon": 80.2720},
    {"Team": "Rescue_5", "lat": 13.0900, "lon": 80.2680},
]

# ---------------- PRIORITY ----------------

def get_priority(msg):

    msg = msg.lower()

    if "injured" in msg or "trapped" in msg:
        return "HIGH"
    elif "urgent" in msg or "help" in msg:
        return "MEDIUM"
    else:
        return "LOW"

# ---------------- DISTANCE ----------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

# ---------------- MENU ----------------

menu = st.sidebar.selectbox(
    "Navigation",
    ["Public App", "Rescue Dashboard"]
)

# =====================================================
# PUBLIC APP
# =====================================================

if menu == "Public App":

    st.title("📱 EchoMesh Public SOS")

    if not FIREBASE_ENABLED:
        st.info("ℹ️ Using local storage (Firebase not configured)")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📍 Your Location")
        lat = st.number_input("Latitude", value=BASE_LAT)
        lon = st.number_input("Longitude", value=BASE_LON)

        message = st.text_area("Emergency Message", placeholder="Describe your emergency...")

        if st.button("SEND SOS", use_container_width=True):

            data = {
                "lat": lat,
                "lon": lon,
                "message": message,
                "priority": get_priority(message),
                "status": "Pending",
                "team": "Not Assigned",
                "chat": [],
                "timestamp": datetime.now().isoformat()
            }

            ref.push(data)

            st.success("✅ SOS Sent Successfully")
            st.balloons()

    with col2:
        st.subheader("🗺️ SOS Location Map")
        
        # Create map for SOS location
        layers = []
        
        # Mark SOS location in blue
        sos_point = pd.DataFrame({
            'lon': [lon],
            'lat': [lat]
        })
        
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                sos_point,
                get_position='[lon, lat]',
                get_fill_color="[0, 100, 255]",
                get_radius=200,
            )
        )
        
        # Add nearby rescue teams
        teams_df = pd.DataFrame(teams)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                teams_df,
                get_position='[lon, lat]',
                get_fill_color="[0, 200, 0]",
                get_radius=150,
            )
        )
        
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=13,
            pitch=40
        )
        
        st.pydeck_chart(pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip={"text": "Blue: Your Location | Green: Rescue Teams"}
        ))

# =====================================================
# RESCUE DASHBOARD
# =====================================================

if menu == "Rescue Dashboard":

    st.title("🚑 EchoMesh Rescue Command Center")

    if not FIREBASE_ENABLED:
        st.info("ℹ️ Using local storage (Firebase not configured)")

    data = ref.get()

    if not data:
        st.warning("No SOS Requests Yet - Showing Demo Data")
        init_demo_data()
        data = ref.get()

    df = pd.DataFrame(data).T

    st.subheader("📊 All SOS Requests")
    st.dataframe(df[['message', 'priority', 'status', 'team', 'lat', 'lon']], use_container_width=True)

    # ---------- GENERATE TEAM DATA WITH AI PREDICTIONS ----------

    tasks = [
        "Search Operation",
        "Medical Assistance",
        "Evacuation Support",
        "Supply Distribution",
        "Damage Assessment"
    ]

    statuses = ["Active", "In Transit", "Idle", "Emergency"]

    ai_teams = []

    for i in range(1, 11):
        lat = BASE_LAT + random.uniform(-0.01, 0.01)
        lon = BASE_LON + random.uniform(-0.01, 0.01)
        battery = random.randint(40, 100)
        signal_strength = random.uniform(0.5, 1.0)
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
        ai_teams.append(team)

    ai_df = pd.DataFrame(ai_teams)

    # ---------- AI TEAM STATUS TABLE ----------

    st.subheader("📋 Rescue Teams - AI Enhanced")
    st.dataframe(ai_df, use_container_width=True)

    # ---------- AI INSIGHTS ----------

    st.subheader("🤖 AI Insights & Optimization")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Reliability Analysis:** Teams with 'Low' reliability may need battery checks or repositioning.")

    with col2:
        st.markdown("**Route Optimization:** Lower AI Route Cost indicates better positioning for emergency response.")

    low_reliability_teams = [team for team in ai_teams if team["AI Reliability"] == "Low"]
    if low_reliability_teams:
        st.warning(f"⚠️ Low Reliability Alert: {', '.join([t['Team'] for t in low_reliability_teams])} require attention")
    else:
        st.success("✅ All teams have high reliability")

    # ---------- SYSTEM ALERTS ----------

    st.subheader("🚨 System Alerts")

    emergency_teams = [team for team in ai_teams if team["Status"] == "Emergency"]
    if emergency_teams:
        for team in emergency_teams:
            st.error(f"🚨 {team['Team']} ({team['Task']}) is in EMERGENCY status - requires immediate support!")
    else:
        st.info("✓ No emergency alerts")

    st.divider()

    st.subheader("🛰 Emergency Map - Real-time Tracking")

    layers = []

    # Victim points
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position='[lon, lat]',
            get_fill_color="[255, 0, 0]",
            get_radius=150,
        )
    )

    # Routes
    route_data = []

    for i, row in df.iterrows():

        team = ai_teams[0]  # Use first AI team for routing

        route_data.append({
            "path": [
                [team["Longitude"], team["Latitude"]],
                [row["lon"], row["lat"]]
            ]
        })

    route_df = pd.DataFrame(route_data)

    layers.append(
        pdk.Layer(
            "PathLayer",
            route_df,
            get_path="path",
            width_scale=5,
            width_min_pixels=3,
            get_color=[0, 255, 0],
        )
    )

    # Add rescue team locations
    teams_for_map = pd.DataFrame(ai_teams)
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            teams_for_map,
            get_position='[Longitude, Latitude]',
            get_fill_color="[0, 100, 255]",
            get_radius=120,
        )
    )

    view_state = pdk.ViewState(
        latitude=BASE_LAT,
        longitude=BASE_LON,
        zoom=12,
        pitch=40
    )

    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip={"text": "Red: SOS Locations | Blue: Rescue Teams | Green: Routes"}
    ), use_container_width=True)

    st.divider()

    # ---------- SELECT REQUEST ----------

    selected = st.selectbox(
        "Select SOS",
        df.index
    )

    req = df.loc[selected]

    st.subheader("🆘 Request Details")

    priority_color = {
        "HIGH": "🔴 HIGH",
        "MEDIUM": "🟠 MEDIUM",
        "LOW": "🟢 LOW"
    }

    st.write("Priority:", priority_color[req["priority"]])
    st.write("Message:", req["message"])
    st.write("Status:", req["status"])

    # ---------- TEAM ASSIGNMENT ----------

    st.subheader("🚑 Assign Team")

    cols = st.columns(len(ai_teams))

    for i, team in enumerate(ai_teams):

        if cols[i].button(team["Team"]):

            ref.child(selected).update({
                "team": team["Team"],
                "status": "Assigned"
            })

            st.success(f"{team['Team']} Assigned")
            st.rerun()

    st.divider()

    # ---------- DISTANCE ----------

    team = ai_teams[0]

    dist = calculate_distance(
        team["Latitude"], team["Longitude"],
        req["lat"], req["lon"]
    )

    st.success(f"Distance: {dist:.2f} km")
    st.info(f"ETA: {(dist/40)*60:.1f} minutes")

    st.divider()

    # ---------- CHAT ----------

    st.subheader("💬 Communication")

    chat_data = req.get("chat", [])

    for msg in chat_data:
        st.write(msg)

    msg = st.text_input("Message")

    if st.button("Send"):

        chat_data.append(f"Rescue: {msg}")

        ref.child(selected).update({
            "chat": chat_data
        })

        st.rerun()