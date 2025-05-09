# app.py
import streamlit as st
from datetime import datetime, timedelta
import requests
import airportsdata

from flight_status import get_flight_info
from weather_api import get_current_weather
from traffic_api import get_travel_time
from agents import intent_agent, status_agent, delay_agent, trip_agent

st.set_page_config(page_title="Flight-Status Concierge")
st.title("✈️ Flight-Status Concierge")

intent = st.radio("Choose an action:", ["Live Status", "Delay Analysis", "Trip Planning"])

if intent == "Live Status":
    flight_code = st.text_input("Flight IATA code (e.g. BA2490):")
    if st.button("Check Status"):
        info = get_flight_info(flight_code)
        if not info:
            st.error("No data found.")
        else:
            dep = info["departure"]
            arr = info["arrival"]
            lg = info.get("live", {})
            status = info["status"]
            eta = arr.get("estimated") or arr.get("scheduled")
            gate = dep.get("gate") or "N/A"

            # weather
            iata = dep.get("iata")
            airport = airportsdata.load("IATA").get(iata, {})
            lat, lon = float(airport["lat"]), float(airport["lon"])
            wx = get_current_weather(lat, lon) or {}
            temp = wx.get("temperature", "N/A")

            # traffic (mock origin near airport)
            travel = get_travel_time(lat+0.01, lon+0.01, lat, lon)
            travel_text = f"{int(travel)} min" if travel else "N/A"

            prompt = (
                f"Flight {flight_code} status: {status}. ETA: {eta}. Gate: {gate}. "
                f"Weather at departure: {temp}°C. Drive time: {travel_text}."
            )
            summary = status_agent.run_sync(prompt).data
            st.success(summary)

elif intent == "Delay Analysis":
    flight_code = st.text_input("Flight IATA code (e.g. UA100):")
    if st.button("Analyze Delays"):
        if not flight_code:
            st.error("Enter a code.")
        else:
            import random
            delays = [random.randint(0, 60) for _ in range(30)]
            avg = sum(delays)/len(delays)
            prompt = (
                f"Delays (min) for {flight_code}: {delays}. Avg: {avg:.1f}. "
                "Summarize delay trends."
            )
            st.success(delay_agent.run_sync(prompt).data)

else:  # Trip Planning
    flight_code = st.text_input("Flight IATA code:")
    origin = st.text_input("Your city:")
    if st.button("Plan Trip"):
        if not flight_code or not origin:
            st.error("Enter both fields.")
        else:
            info = get_flight_info(flight_code)
            if not info:
                st.error("Flight not found.")
            else:
                dep = info["departure"]
                sched = dep.get("scheduled")
                try:
                    dep_time = datetime.fromisoformat(sched.replace(" ", "T"))
                except:
                    dep_time = None

                # geocode via Open-Meteo
                lat, lon = None, None
                try:
                    r = requests.get(
                        "https://geocoding-api.open-meteo.com/v1/search",
                        params={"name": origin, "count": 1}, timeout=5
                    )
                    loc = r.json()["results"][0]
                    lat, lon = loc["latitude"], loc["longitude"]
                except:
                    pass

                # traffic to airport
                airport = airportsdata.load("IATA").get(dep.get("iata"), {})
                dest_lat, dest_lon = float(airport["lat"]), float(airport["lon"])
                travel = get_travel_time(lat, lon, dest_lat, dest_lon) if lat else None

                # weather at origin
                wx = get_current_weather(lat, lon) if lat else {}
                temp = wx.get("temperature", "N/A")

                # compute leave-by
                leave = "Unknown"
                if dep_time and travel is not None:
                    leave_dt = dep_time - timedelta(minutes=travel + 30)
                    leave = leave_dt.strftime("%Y-%m-%d %H:%M")

                prompt = (
                    f"Flight at {dep_time}. Drive: {int(travel) if travel else 'N/A'} min. "
                    f"Weather: {temp}°C. When to leave?"
                )
                summary = trip_agent.run_sync(prompt).data
                st.success(f"{summary}\n\n**Leave by:** {leave}")
