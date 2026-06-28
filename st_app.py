import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="Ultra Agent Console", layout="wide")

st.title("🚀 High-Performance Agent (Gemini 1.5)")

# --- API KEY ---
# Change the Env Variable name in Render to GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- SIDEBAR: FILE UPLOADER ---
st.sidebar.title("📁 Multimodal Uploads")
uploaded_file = st.sidebar.file_uploader(
    "Upload Image, PDF, or Video", 
    type=["pdf", "png", "jpg", "jpeg", "mp4"]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask about your files..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Missing Gemini API Key!")
        st.stop()

    try:
        genai.configure(api_key=api_key)
        # Use Gemini 1.5 Flash (Fast, Free, and High Quality)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        content_parts = [prompt]

        # Handle File inputs for Gemini
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                content_parts.append(f"\nPDF Context: {text}")
            else:
                # Images and Videos are handled natively by Gemini!
                file_data = uploaded_file.getvalue()
                content_parts.append({
                    "mime_type": uploaded_file.type,
                    "data": file_data
                })

        with st.chat_message("assistant"):
            response = model.generate_content(content_parts)
            full_response = response.text
            st.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error: {e}")