import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="My Data App", layout="wide")

# This creates a Sidebar
st.sidebar.title("Settings")
name = st.sidebar.text_input("Enter your name")
chart_data_size = st.sidebar.slider("Select number of data points", 10, 100, 20)

st.title(f"Welcome to the Dashboard, {name}!")

# Create some random data
chart_data = pd.DataFrame(
    np.random.randn(chart_data_size, 3),
    columns=['A', 'B', 'C']
)

# Display a line chart
st.subheader("Interactive Trend Chart")
st.line_chart(chart_data)

# Display a button that triggers a balloon celebration
if st.button("Celebrate!"):
    st.balloons()
 import streamlit as st
from groq import Groq

st.set_page_config(page_title="Agent Console", layout="wide")

st.title("🤖 My No-Code Agent Console")

# Sidebar for Settings
st.sidebar.title("Model Settings")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
model = st.sidebar.selectbox("Choose Model", ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Explain a complex concept..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.info("Please add your Groq API key to continue.")
        st.stop()

    # Call the Model
    client = Groq(api_key=api_key)
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})   