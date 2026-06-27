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
if prompt := st.chat_input("Ask your agent anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.info("Please add your Groq API key in the sidebar.")
        st.stop()

    # Call the Model
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