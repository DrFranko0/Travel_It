import asyncio
from datetime import datetime, timedelta
import streamlit as st
from pydantic_ai.usage import Usage, UsageLimits
from dotenv import load_dotenv

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.trip_planner import trip_planner_agent, TripPlannerDeps
from models.trip import TripPlan
from config import OPENROUTER_API_KEY

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY environment variable not set!")
    print("Set this variable to use the OpenRouter API.")

st.set_page_config(
    page_title="Travel_It - AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

async def run_async(func, *args, **kwargs):
    return await func(*args, **kwargs)

def main():
    # Header
    st.title(" Travel_It - AI Travel Planner")
    st.markdown("""
    Let our AI agents plan your perfect trip! We specialize in finding less crowded, 
    underrated locations while optimizing your budget.
    """)
    
    if not OPENROUTER_API_KEY:
        st.error("""
        ⚠️ OpenRouter API key not found! 
        
        Please set the OPENROUTER_API_KEY environment variable to use this application.
        See the README.md file for instructions.
        """)
        st.stop()
    
    with st.sidebar:
        st.header("Trip Details")
        
        origin = st.text_input("Origin", "New York")
        destination = st.text_input("Destination", "Paris")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now() + timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now() + timedelta(days=37)
            )
        
        travelers = st.number_input("Number of Travelers", min_value=1, value=2)
        budget = st.number_input("Total Budget (USD)", min_value=500, value=5000)
        
        st.subheader("Preferences")
        
        accommodation_options = ["budget", "mid-range", "luxury"]
        accommodation_preference = st.select_slider(
            "Accommodation",
            options=accommodation_options,
            value="mid-range"
        )
        
        transportation_options = ["public", "rental car", "taxi"]
        transportation_preference = st.select_slider(
            "Transportation",
            options=transportation_options,
            value="public"
        )
        
        dining_options = ["budget", "mid-range", "fine dining"]
        dining_preference = st.select_slider(
            "Dining",
            options=dining_options,
            value="mid-range"
        )
        
        st.subheader("Interests")
        interests = st.multiselect(
            "Select your interests",
            [
                "Art", "History", "Food", "Nature", "Architecture", 
                "Shopping", "Museums", "Nightlife", "Adventure", "Relaxation",
                "Photography", "Local Culture", "Music", "Beach", "Sports"
            ],
            ["Art", "Food", "History"]
        )
        
        plan_trip_button = st.button("Plan My Trip")
    
    if "trip_plan" not in st.session_state:
        st.session_state.trip_plan = None
    
    if plan_trip_button:
        # Show spinner while planning
        with st.spinner("Our AI agents are planning your perfect trip... This may take a minute."):
            # Create dependencies for the Trip Planner Agent
            deps = TripPlannerDeps(
                origin=origin,
                destination=destination,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                travelers=travelers,
                budget=budget,
                interests=[interest.lower() for interest in interests],
                accommodation_preference=accommodation_preference,
                transportation_preference=transportation_preference,
                dining_preference=dining_preference
            )
            
            usage = Usage()
            usage_limits = UsageLimits(request_limit=50)

            result = asyncio.run(run_async(
                trip_planner_agent.run,
                f"Plan a trip from {origin} to {destination}",
                deps=deps,
                usage=usage,
                usage_limits=usage_limits
            ))
            
            if hasattr(result, "output") and isinstance(result.output, TripPlan):
                st.session_state.trip_plan = result.output
            else:
                st.error("Failed to create a trip plan. Please try again with different parameters.")
                if hasattr(result, "output"):
                    st.write(f"Reason: {result.output.reason}")
                    st.write("Suggestions:")
                    for suggestion in result.output.suggestions:
                        st.write(f"- {suggestion}")
    
    if st.session_state.trip_plan:
        trip = st.session_state.trip_plan
        
        st.header("Your Trip Plan")
        st.subheader(f" {trip.origin} to {trip.destination}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dates", f"{trip.start_date} to {trip.end_date}")
        with col2:
            st.metric("Travelers", str(trip.travelers))
        with col3:
            st.metric("Total Cost", f"${trip.total_estimated_cost:.2f}")
        
        st.subheader(" Budget Breakdown")
        
        budget_data = {k: v for k, v in trip.budget_breakdown.items()}
        
        cols = st.columns(len(budget_data))
        for i, (category, amount) in enumerate(budget_data.items()):
            cols[i].metric(
                category.replace("_", " ").title(),
                f"${amount:.2f}",
                f"{(amount / trip.total_estimated_cost) * 100:.1f}%"
            )
        
        if trip.outbound_flight:
            st.subheader(" Flight Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Outbound Flight**")
                st.write(f"Airline: {trip.outbound_flight.airline}")
                st.write(f"Flight Number: {trip.outbound_flight.flight_number}")
                st.write(f"Departure: {trip.outbound_flight.departure_time}")
                st.write(f"Arrival: {trip.outbound_flight.arrival_time}")
                st.write(f"Price: ${trip.outbound_flight.price:.2f}")
            
            if trip.return_flight:
                with col2:
                    st.write("**Return Flight**")
                    st.write(f"Airline: {trip.return_flight.airline}")
                    st.write(f"Flight Number: {trip.return_flight.flight_number}")
                    st.write(f"Departure: {trip.return_flight.departure_time}")
                    st.write(f"Arrival: {trip.return_flight.arrival_time}")
                    st.write(f"Price: ${trip.return_flight.price:.2f}")

        if trip.accommodation:
            st.subheader(" Accommodation")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{trip.accommodation.name}**")
                st.write(f"Type: {trip.accommodation.accommodation_type}")
                st.write(f"Address: {trip.accommodation.address}")
                st.write(f"Check-in: {trip.accommodation.check_in_date}")
                st.write(f"Check-out: {trip.accommodation.check_out_date}")
            
            with col2:
                st.write(f"Price per night: ${trip.accommodation.price_per_night:.2f}")
                st.write(f"Total price: ${trip.accommodation.total_price:.2f}")
                if trip.accommodation.rating:
                    st.write(f"Rating: {trip.accommodation.rating}/5")
                if trip.accommodation.amenities:
                    st.write("Amenities: " + ", ".join(trip.accommodation.amenities))

        st.subheader(" Itinerary")
        
        for day in trip.daily_itinerary:
            with st.expander(f"Day {day.day}: {day.date}"):
                for activity in day.activities:
                    st.markdown(f"**{activity.name}** - {activity.duration_hours} hours")
                    st.markdown(f"*{activity.description}*")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"Category: {activity.category}")
                    if activity.estimated_cost:
                        col2.write(f"Cost: ${activity.estimated_cost:.2f}")
                    col3.write(f"Crowdedness: {activity.crowdedness}")
                    
                    if activity.tips:
                        st.write("Tips:")
                        for tip in activity.tips:
                            st.write(f"- {tip}")
                    
                    st.markdown("---")
                
                if day.notes:
                    st.write(f"**Notes:** {day.notes}")
        
        if trip.underrated_locations:
            st.subheader(" Hidden Gems & Underrated Locations")
            for location in trip.underrated_locations:
                st.write(f"- {location}")
        
        st.subheader(" Travel Tips")
        for tip in trip.travel_tips:
            st.write(f"- {tip}")

if __name__ == "__main__":
    main()
