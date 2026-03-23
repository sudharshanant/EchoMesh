import streamlit as st
import pandas as pd
import random
import time

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

BASE_LAT = 13.0827
BASE_LON = 80.2707


def calculate_priority(message):
    score = 10

    keywords_high = ["injured", "bleeding", "trapped", "fire", "collapsed"]
    keywords_medium = ["help", "urgent", "stuck"]

    msg = message.lower()

    for k in keywords_high:
        if k in msg:
            score += 50

    for k in keywords_medium:
        if k in msg:
            score += 25

    score += random.randint(0, 20)

    if score > 80:
        level = "Critical"
    elif score > 50:
        level = "High"
    elif score > 20:
        level = "Medium"
    else:
        level = "Low"

    return score, level


if "public_requests" not in st.session_state:
    st.session_state.public_requests = []

if "teams" not in st.session_state:
    teams = []
    for i in range(5):
        teams.append({
            "Team": f"Rescue_{i+1}",
            "Latitude": BASE_LAT + random.uniform(-0.01, 0.01),
            "Longitude": BASE_LON + random.uniform(-0.01, 0.01),
            "Status": "Available"
        })
    st.session_state.teams = teams

mode = st.sidebar.selectbox(
    "Select Interface",
    ["Public SOS", "Rescue Dashboard"]
)


if mode == "Public SOS":

    st.title("🆘 Public Emergency System")

    col1, col2 = st.columns(2)

    with col1:
        lat = st.number_input("Latitude", value=BASE_LAT)
        lon = st.number_input("Longitude", value=BASE_LON)

        message = st.text_area(
            "Emergency Message",
            placeholder="Describe your situation..."
        )

        if st.button("🚨 Send SOS", use_container_width=True):

            score, level = calculate_priority(message)

            request = {
                "Latitude": lat,
                "Longitude": lon,
                "Message": message,
                "Status": "Pending",
                "Assigned Team": "Not Assigned",
                "Chat": [],
                "Priority Score": score,
                "Priority Level": level
            }

            st.session_state.public_requests.append(request)
            st.success(f"SOS Sent! Priority: {level}")

    with col2:
        map_df = pd.DataFrame([{"lat": lat, "lon": lon}])
        st.map(map_df)

    st.divider()

    # Show user requests + chat
    if st.session_state.public_requests:

        st.subheader("📋 Your Requests")

        for i, req in enumerate(st.session_state.public_requests):

            st.write(f"### Request {i+1}")
            st.write(req)

            # Chat view
            st.write("💬 Chat")

            for msg in req["Chat"]:
                st.write(msg)

            user_msg = st.text_input(
                f"Type message for request {i}",
                key=f"user_chat_{i}"
            )

            if st.button(f"Send Message {i}"):

                req["Chat"].append(f"Public: {user_msg}")
                st.rerun()


if mode == "Rescue Dashboard":

    st.title("🚑 Rescue Coordination Dashboard")

    # Teams
    st.subheader("👨‍🚒 Rescue Teams")

    teams_df = pd.DataFrame(st.session_state.teams)
    st.dataframe(teams_df)

    st.map(teams_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

    st.divider()

    # Requests
    if st.session_state.public_requests:

        df = pd.DataFrame(st.session_state.public_requests)

        st.subheader("🆘 Public Requests (AI Priority Ranked)")
        st.dataframe(df.sort_values("Priority Score", ascending=False))

        st.subheader("📍 SOS Locations")
        st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

        st.divider()

        # Select request
        req_index = st.selectbox(
            "Select Request",
            range(len(st.session_state.public_requests))
        )

        request = st.session_state.public_requests[req_index]

        st.write("### Selected Request Details")
        st.write(request)

        # Assign team
        team_names = [t["Team"] for t in st.session_state.teams]

        selected_team = st.selectbox("Assign Team", team_names)

        if st.button("Assign Team"):

            request["Assigned Team"] = selected_team
            request["Status"] = "Team Assigned"
            st.success("Team Assigned!")

        st.divider()

        st.subheader("💬 Communication")

        for msg in request["Chat"]:
            st.write(msg)

        rescue_msg = st.text_input("Message to Public")

        if st.button("Send Message"):

            request["Chat"].append(f"Rescue: {rescue_msg}")
            st.rerun()

    else:
        st.info("No SOS requests yet.")