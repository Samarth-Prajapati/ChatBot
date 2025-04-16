# "AIzaSyDksOHkRvp6sIY23kgU7gcbP9VsWT6zVIQ"
# conda activate chatbot_env
import streamlit as st
import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from typing import Dict, List, TypedDict
import asyncio
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyDksOHkRvp6sIY23kgU7gcbP9VsWT6zVIQ")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

# State for LangGraph
class ChatState(TypedDict):
    messages: List[dict]

# Initialize LangChain components
prompt = ChatPromptTemplate.from_template("You are a helpful assistant. Answer the following: {input}")

# Define LangGraph nodes
async def call_llm(state: ChatState) -> ChatState:
    last_message = state["messages"][-1]["content"]
    formatted_prompt = prompt.format(input=last_message)
    response = await model.generate_content_async(formatted_prompt)
    state["messages"].append({"role": "assistant", "content": response.text})
    return state

# Build LangGraph workflow
workflow = StateGraph(ChatState)
workflow.add_node("llm", call_llm)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)
app = workflow.compile()

# Streamlit UI
st.set_page_config(page_title="ChatBot", layout="centered")

# Minimal CSS for clean, attractive UI
st.markdown("""
    <style>
    .main { 
        background-color: #ffffff; 
        padding: 10px; 
        font-family: 'Arial', sans-serif; 
    }
    .title { 
        text-align: center; 
        color: #1e3a8a; 
        font-size: 32px; 
        font-weight: bold; 
        margin: 10px 0 5px 0; 
    }
    .subtitle { 
        text-align: center; 
        color: #6b7280; 
        font-size: 16px; 
        margin-bottom: 15px; 
    }
    
    .chat-history { 
        flex-grow: 1; 
        overflow-y: auto; 
        padding: 10px 0; 
    }
    .user-message { 
        background-color: #eff6ff; 
        color: #1e40af; 
        border-radius: 8px; 
        padding: 10px; 
        margin: 5px 10px; 
        max-width: 100%; 
        align-self: flex-end; 
    }
    .bot-message { 
        background-color: #1e3a8a; 
        color: white; 
        border-radius: 8px; 
        padding: 10px; 
        margin: 5px 10px; 
        max-width: 100%; 
        align-self: flex-start; 
    }
    .input-container { 
        position: fixed; 
        bottom: 10px; 
        left: 50%; 
        transform: translateX(-50%); 
        max-width: 600px; 
        width: 100%; 
        display: flex; 
        gap: 10px; 
        padding: 10px; 
        background-color: #ffffff; 
        border-top: 1px solid #e5e7eb; 
    }
    .stButton > button { 
        background-color: #3b82f6; 
        color: white; 
        border-radius: 8px; 
        padding: 10px 20px; 
        font-size: 14px; 
        border: none; 
    }
    .stButton > button:hover { 
        background-color: #2563eb; 
    }
    .sidebar .sidebar-content { 
        background-color: #f9fafb; 
        padding: 10px; 
        border-radius: 8px; 
    }
    ::-webkit-scrollbar { 
        width: 6px; 
    }
    ::-webkit-scrollbar-thumb { 
        background: #3b82f6; 
        border-radius: 8px; 
    }
    ::-webkit-scrollbar-track { 
        background: #f9fafb; 
    }
    </style>
""", unsafe_allow_html=True)

# JavaScript for popup every 15 seconds
st.markdown("""
    <script>
    function showPopup() {
        alert("Meet ChatBot 🤖! I'm powered by Gemini AI, built with LangChain and LangGraph, ready to answer your questions!");
    }
    setInterval(showPopup, 15000);
    </script>
""", unsafe_allow_html=True)

# Sidebar with bot details
with st.sidebar:
    st.header("Bot Details")
    st.write("**Name**: ChatBot 🤖")
    st.write("**Powered by**: Gemini 1.5 Flash")
    st.write("**Framework**: LangChain & LangGraph")
    st.write("**Purpose**: Answer your questions with AI precision!")
    st.write("**Version**: 1.0")

# Main chat UI
st.markdown('<div class="title">ChatBot 🤖</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Chat With Us</div>', unsafe_allow_html=True)

# Chat container
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Chat history
    with st.container():
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">You: {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 Bot: {msg["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fixed input area
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input("Your message:", key="user_input")
    send_button = st.button("Send")
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(f'<div class="user-message">You: {user_input}</div>', unsafe_allow_html=True)
        
        # Show generating message
        with st.spinner("Generating answer..."):
            # Run LangGraph workflow
            initial_state = {"messages": [{"role": "user", "content": user_input}]}
            result = asyncio.run(app.ainvoke(initial_state))
            response = result["messages"][-1]["content"]
        
        # Display response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(f'<div class="bot-message">🤖 Bot: {response}</div>', unsafe_allow_html=True)
        
        # Clear input
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)