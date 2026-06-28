import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# Set up the page layout
st.set_page_config(page_title="Ultra Agent Console", layout="wide", page_icon="🚀")

st.title("🚀 Ultra Agent Console (Gemini 1.5)")
st.markdown("---")

# --- 1. API KEY SETUP ---
# It checks Render Environment Variables first, then the sidebar
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.title("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.info("Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)")
    else:
        st.success("API Key loaded from Render!")
    
    st.markdown("---")
    st.title("📁 Multimodal Uploads")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Image, PDF, or Video", 
        type=["pdf", "png", "jpg", "jpeg", "mp4"]
    )
    
    if uploaded_file:
        st.sidebar.info(f"File uploaded: {uploaded_file.name}")

# --- 2. CHAT HISTORY SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. CHAT LOGIC ---
if prompt := st.chat_input("Ask about your files or anything else..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if API Key exists
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar to continue.")
        st.stop()

    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # 'gemini-1.5-flash-latest' is the most stable version string
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Prepare content parts for the AI
        # It starts with the user's text prompt
        content_parts = [prompt]

        # If a file is uploaded, process it
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                # Extract text from PDF
                reader = PdfReader(uploaded_file)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()
                content_parts.append(f"\n\n[Attached PDF Content]:\n{pdf_text}")
            
            elif uploaded_file.type in ["image/png", "image/jpeg", "video/mp4"]:
                # Images and Videos are sent as raw bytes directly to Gemini
                file_data = uploaded_file.getvalue()
                content_parts.append({
                    "mime_type": uploaded_file.type,
                    "data": file_data
                })

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):
                response = model.generate_content(content_parts)
                full_response = response.text
                st.markdown(full_response)
            
        # Save Assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error: {e}")