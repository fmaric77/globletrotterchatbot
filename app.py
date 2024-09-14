import streamlit as st
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from dotenv import load_dotenv
import os
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the Athena function and tool from x.py
from x import query_athena_tool

try:
    from weathertools import get_current_weather, get_weather_forecast, get_historical_weather
    from weathertools2 import recommend_best_time_to_visit
    from wikipediatools import get_city_highlights, get_sport_clubs_info, get_sportsman_info
    from wikipediatools2 import get_best_travel_package
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    st.error(f"Error importing modules: {e}")

# Load environment variables
load_dotenv()

# Define tools
tools = [
    get_current_weather,
    get_weather_forecast,
    get_city_highlights,
    get_historical_weather,
    get_sport_clubs_info,
    get_sportsman_info,
    recommend_best_time_to_visit,
    get_best_travel_package,
    query_athena_tool
]

# Ensure AWS_DEFAULT_REGION is set
if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'

# Initialize session state for memory and session ID
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Use StreamlitChatMessageHistory for persistent chat history
if 'message_history' not in st.session_state:
    st.session_state.message_history = StreamlitChatMessageHistory(key="chat_messages")

# Bind tools to model
chat_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
chat_model = None
try:
    chat_model = ChatBedrock(model_id=chat_model_id).bind_tools(tools)
except Exception as e:
    logger.error(f"Error initializing ChatBedrock: {e}")
    st.error(f"Error initializing ChatBedrock: {e}")

# Create agent with updated prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the tools at your disposal to answer questions. Maintain context from previous messages in the conversation. Remember details about the user that they've shared."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create agent and executor
agent_executor = None
if chat_model:
    try:
        agent = create_tool_calling_agent(chat_model, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        with_message_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: st.session_state.message_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )
    except Exception as e:
        logger.error(f"Error creating agent and executor: {e}")
        st.error(f"Error creating agent and executor: {e}")



def get_message_content(message):
    """Safely extract content from various message formats."""
    if isinstance(message, (HumanMessage, AIMessage)):
        return message.content
    elif isinstance(message, dict):
        return message.get('content', message.get('text', ''))
    elif isinstance(message, str):
        return message
    elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], dict):
        return message[0].get('text', '')
    else:
        return str(message)


def get_memory_contents():
    """Extract and format memory contents from the message history, prioritizing the latest messages."""
    memory_contents = []
    seen_contents = set()
    
    # Reverse the order of messages to prioritize the latest ones
    reversed_messages = reversed(st.session_state.message_history.messages)
    
    for msg in reversed_messages:
        content = get_message_content(msg)
        if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
            content = content[0].get('text', '')
        
        if content not in seen_contents:
            memory_contents.append(content)
            seen_contents.add(content)
    
    return "\n".join(memory_contents)

def handle_user_input(user_input):
    if not agent_executor:
        return "Agent executor is not initialized."
    
    try:
        # Add user input to history
        
        # Prepare the chat history for the model
        chat_history = []
        for msg in st.session_state.message_history.messages:
            content = get_message_content(msg)
            if isinstance(msg, HumanMessage) or (isinstance(msg, dict) and msg.get('type') == 'human'):
                chat_history.append((content, None))
            else:
                chat_history.append((None, content))
        
        # Extract memory contents and include it in the input
        memory_contents = get_memory_contents()
        full_input = f"{user_input}\n\nMemory Contents:\n{memory_contents}"
        
        # Invoke the agent with the updated memory
        response = with_message_history.invoke(
            {"input": full_input, "chat_history": chat_history},
            config={"configurable": {"session_id": st.session_state.session_id}}
        )
        logger.debug(f"Response from agent: {response}")
        
        # Extract and format the bot's response
        bot_response = ''
        
        if isinstance(response, dict) and 'output' in response:
            bot_response = response['output']
        elif isinstance(response, str):
            bot_response = response
        elif isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict):
            bot_response = response[0].get('text', '')
        
       
        
    except Exception as e:
        logger.error(f"Error handling user input: {e}")
        return f"An error occurred: {str(e)}"
    
    return bot_response

# Streamlit UI
st.title("Olympic Travel Chatbot")

# Images for user and bot
user_image = "images/user.png"
bot_image = "images/bot.png"

# Function to display messages
def display_message(image_url, sender, message, is_user=True):
    col1, col2 = st.columns([1, 9])
    with col1:
        st.image(image_url, width=50)
    with col2:
        content = get_message_content(message)
        if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
            content = content[0].get('text', '')
        st.write(f"**{sender}:** {content}", unsafe_allow_html=True)

# Display conversation history
for message in st.session_state.message_history.messages:
    if isinstance(message, HumanMessage) or (isinstance(message, dict) and message.get('type') == 'human'):
        display_message(user_image, "User", message, is_user=True)
    else:
        display_message(bot_image, "Bot", message, is_user=False)

user_input = st.text_input("Enter your query:")
if st.button("Send"):
    response = handle_user_input(user_input)
    if response:  # Only display the bot's response if it's not empty
        display_message(bot_image, "Bot", response, is_user=False)

# Debug information
if st.checkbox("Show Debug Info"):
    st.write(f"Session ID: {st.session_state.session_id}")
    st.write(f"Number of messages in memory: {len(st.session_state.message_history.messages)}")
    st.write("Memory contents:")
    for msg in st.session_state.message_history.messages:
        content = get_message_content(msg)
        if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
            content = content[0].get('text', '')
        st.write(f"- {type(msg).__name__}: {content[:50]}...")