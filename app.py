import json
import streamlit as st
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
import os
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)

try:
    from weathertools import get_current_weather, get_weather_forecast, get_historical_weather
    from weathertools2 import recommend_best_time_to_visit
    from wikipediatools import get_city_highlights, get_sport_clubs_info,get_sportsman_info,get_best_travel_package
except ImportError as e:
    logging.error(f"Error importing modules: {e}")
    st.error(f"Error importing modules: {e}")

# Load environment variables
load_dotenv()

# Ensure AWS_DEFAULT_REGION is set
if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'  # Set your default region here

# Bind tools to model
chat_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
chat_model = None
try:
    chat_model = ChatBedrock(model_id=chat_model_id).bind_tools([get_current_weather, get_weather_forecast, get_city_highlights, get_historical_weather, get_sport_clubs_info,get_sportsman_info,recommend_best_time_to_visit,get_best_travel_package])
except Exception as e:
    logging.error(f"Error initializing ChatBedrock: {e}")
    st.error(f"Error initializing ChatBedrock: {e}")

# Create agent with prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the tools at your disposal to answer questions."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Initialize memory for chat history
memory = ChatMessageHistory()

# Define tools
tools = [get_current_weather, get_weather_forecast, get_city_highlights, get_historical_weather, get_sport_clubs_info,get_sportsman_info,recommend_best_time_to_visit,get_best_travel_package]

# Create agent and executor
agent_executor = None
if chat_model:
    try:
        agent = create_tool_calling_agent(chat_model, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        with_message_history = RunnableWithMessageHistory(agent_executor, lambda x: memory, input_messages_key="input")
    except Exception as e:
        logging.error(f"Error creating agent and executor: {e}")
        st.error(f"Error creating agent and executor: {e}")

# Function to handle user input
def handle_user_input(user_input):
    if not agent_executor:
        return "Agent executor is not initialized."
    try:
        response = with_message_history.invoke({"input": user_input}, config={"configurable": {"session_id": "stringx"}})
        logging.debug(f"Response from agent: {response}")
        # Extract and format the bot's response
        bot_response = response.get('output', [])
        if bot_response and isinstance(bot_response, list) and len(bot_response) > 0:
            first_response = bot_response[0]
            if isinstance(first_response, dict) and 'text' in first_response:
                clean_response = first_response['text']
            else:
                clean_response = "Sorry, I couldn't understand the response."
        else:
            clean_response = "Sorry, I couldn't understand the response."
        return clean_response
    except Exception as e:
        logging.error(f"Error handling user input: {e}")
        return f"An error occurred: {e}"

# Streamlit UI
st.title("Weather and Olympic Data Chatbot")

# Images for user and bot
user_image = "images/user.png"
bot_image = "images/bot.png"

# Function to display messages
def display_message(image_url, sender, message, is_user=True):
    col1, col2 = st.columns([1, 9])
    with col1:
        st.image(image_url, width=50)
    with col2:
        if is_user:
            st.write(f"**{sender}:** {message}", unsafe_allow_html=True)
        else:
            st.write(f"**{sender}:** {message}", unsafe_allow_html=True)

user_input = st.text_input("Enter your query:")
if st.button("Send"):
    display_message(user_image, "User", user_input, is_user=True)
    response = handle_user_input(user_input)
    if response:  # Only display the bot's response if it's not empty
        display_message(bot_image, "Bot", response, is_user=False)