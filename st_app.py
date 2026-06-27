import streamlit as st
from groq import Groq
import os

st.set_page_config(page_title="Agent Console", layout="wide")

st.title("🤖 My No-Code Agent Console")

# --- API KEY LOGIC ---
# First, try to get the key from Render's hidden settings
api_key = os.environ.get("GROQ_API_KEY")

# If it's not in Render settings, show a sidebar input as a backup
if not api_key:
    st.sidebar.warning("API Key not found in Render Settings. Please enter it below.")
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# --- MODEL SETTINGS ---
st.sidebar.title("Model Settings")
# These are the current active Groq models
model_options = [
    "llama-3.3-70b-versatile", 
    "llama-3.1-8b-instant", 
    "gemma2-9b-it"
]
model = st.sidebar.selectbox("Choose Model", model_options)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your agent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Missing API Key!")
        st.stop()

    try:
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error: {e}")
        