import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

# Set up the page layout
st.set_page_config(page_title="Ultra Agent Console", layout="wide", page_icon="🚀")

st.title("🚀 Ultra Agent Console (Gemini 1.5)")
st.markdown("---")

# --- 1. API KEY SETUP ---
api_key = os.environ.get("GEMINI_API_KEY")

with st.sidebar:
    st.title("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.info("Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)")
    else:
        st.success("API Key loaded from Render!")
    
    # Model Selection (In case one gives a 404)
    st.markdown("---")
    model_choice = st.selectbox(
        "Select Model Version",
        ["gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-pro"]
    )
    
    st.markdown("---")
    st.title("📁 Multimodal Uploads")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Image, PDF, or Video", 
        type=["pdf", "png", "jpg", "jpeg", "mp4"]
    )

# --- 2. CHAT HISTORY SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. CHAT LOGIC ---
if prompt := st.chat_input("Ask about your files..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar.")
        st.stop()

    try:
        genai.configure(api_key=api_key)
        
        # We use the selection from the sidebar
        model = genai.GenerativeModel(model_choice)
        
        content_parts = [prompt]

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()
                content_parts.append(f"\n\n[Attached PDF Content]:\n{pdf_text}")
            
            elif uploaded_file.type in ["image/png", "image/jpeg", "video/mp4"]:
                file_data = uploaded_file.getvalue()
                content_parts.append({
                    "mime_type": uploaded_file.type,
                    "data": file_data
                })

        with st.chat_message("assistant"):
            with st.spinner(f"Agent ({model_choice}) is thinking..."):
                response = model.generate_content(content_parts)
                full_response = response.text
                st.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Try switching the 'Model Version' in the sidebar.")
