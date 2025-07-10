import os
import chainlit as cl
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import random
from typing import Optional, Dict, List

load_dotenv()

@function_tool
def get_flights(origin: str, destination: str, travel_date: str) -> str:
    """Mock flight information tool"""
    mock_flights = [
        {"airline": "AirLine X", "flight_no": "AX101", "departure_time": "08:00 AM", "arrival_time": "12:00 PM", "price": "$350"},
        {"airline": "FlyWell", "flight_no": "FW205", "departure_time": "09:30 AM", "arrival_time": "01:30 PM", "price": "$400"},
        {"airline": "SkyPath Airways", "flight_no": "SP310", "departure_time": "02:00 PM", "arrival_time": "06:00 PM", "price": "$320"}
    ]

    response = f"Flights from {origin} to {destination} on {travel_date}:\n\n"
    for flight in mock_flights:
        response += f"- {flight['airline']} ({flight['flight_no']}): {flight['departure_time']} to {flight['arrival_time']}, {flight['price']}\n"
    return response + "\n*Simulated data*"

@function_tool
def get_attractions(city: str) -> str:
    """Mock attractions tool"""
    attractions = {
        "paris": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral"],
        "tokyo": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Skytree"],
        "london": ["Buckingham Palace", "Tower of London", "London Eye"]
    }
    city_lower = city.lower()
    if city_lower in attractions:
        return f"Attractions in {city}:\n- " + "\n- ".join(random.sample(attractions[city_lower], 3))
    return f"No attraction data for {city}"

@function_tool
def get_restaurants(city: str, cuisine: str = "any") -> str:
    """Mock restaurants tool"""
    restaurants = {
        "paris": {
            "any": ["Le Relais de l'Entrecôte", "Septime", "L'As du Fallafel"],
            "french": ["Le Comptoir du Relais", "Frenchie"]
        },
        "tokyo": {
            "any": ["Tsukiji Outer Market", "Ichiran Ramen"],
            "japanese": ["Sushi Saito", "Tempura Kondo"]
        }
    }
    city_lower = city.lower()
    cuisine_lower = cuisine.lower()
    if city_lower in restaurants:
        if cuisine_lower in restaurants[city_lower]:
            suggestions = restaurants[city_lower][cuisine_lower]
        else:
            suggestions = restaurants[city_lower]["any"]
        return f"Restaurants in {city} ({cuisine}):\n- " + "\n- ".join(suggestions)
    return f"No restaurant data for {city}"

@function_tool
def suggest_hotels(destination: str, budget: str) -> str:
    """Mock hotels tool"""
    hotels = {
        "economy": [
            {"name": "Budget Stay Inn", "price": "$80", "rating": "3/5"},
            {"name": "Traveler's Nook", "price": "$95", "rating": "3.5/5"}
        ],
        "mid-range": [
            {"name": "City View Hotel", "price": "$150", "rating": "4/5"},
            {"name": "Comfort Suites", "price": "$170", "rating": "4/5"}
        ],
        "luxury": [
            {"name": "Grand Palace Hotel", "price": "$350", "rating": "5/5"},
            {"name": "Elite Residency", "price": "$400", "rating": "4.8/5"}
        ]
    }
    selected = hotels.get(budget.lower(), hotels["mid-range"])
    response = f"Hotels in {destination} ({budget}):\n\n"
    for hotel in selected:
        response += f"- {hotel['name']}: {hotel['price']}/night, Rating: {hotel['rating']}\n"
    return response + "\n*Simulated data*"

@cl.on_chat_start
async def start():
    """Initialize agents"""
    destination_agent = Agent(
        name="Destination Expert",
        instructions="Suggest travel destinations based on user preferences",
        model="gpt-3.5-turbo",
        tools=[]
    )
    
    booking_agent = Agent(
        name="Booking Agent",
        instructions="Help with flight and hotel bookings",
        model="gpt-3.5-turbo",
        tools=[get_flights, suggest_hotels]
    )
    
    explore_agent = Agent(
        name="Local Guide",
        instructions="Provide attraction and restaurant recommendations",
        model="gpt-3.5-turbo",
        tools=[get_attractions, get_restaurants]
    )
    
    orchestrator = Agent(
        name="Travel Designer",
        instructions="Coordinate between specialized agents to plan trips",
        model="gpt-4",
        tools=[],
        handoffs=[destination_agent, booking_agent, explore_agent]
    )
    
    cl.user_session.set("orchestrator", orchestrator)
    
    await cl.Message(
        content="""**Welcome to Travel Assistant!** 🌍✈️

I can help with:
- Destination ideas
- Flight & hotel bookings
- Local attractions & restaurants

Where would you like to go today?""",
        author="Travel Assistant"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages"""
    orchestrator = cl.user_session.get("orchestrator")
    user_query = message.content
    
    try:
        # Get the response from Runner
        response = await Runner.run(orchestrator, user_query)
        
        # Access response attributes properly
        await cl.Message(
            content=response.final_output,  # Changed from response["final_output"]
             # Changed from response["source_agent"]
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"Error processing request: {str(e)}",
            author="System"
        ).send()

if __name__ == "__main__":
    # Run with: chainlit run travel_assistant.py
    pass