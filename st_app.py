import streamlit as st
from groq import Groq
import os
from PyPDF2 import PdfReader

st.set_page_config(page_title="Agent Console", layout="wide")

st.title("🤖 Advanced Agent Console")

# --- RENDER KEY LOGIC ---
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# --- SIDEBAR: FILE UPLOADER ---
st.sidebar.title("📁 File Uploads")
uploaded_files = st.sidebar.file_uploader(
    "Upload Media or PDFs", 
    type=["pdf", "png", "jpg", "jpeg", "mp4"], 
    accept_multiple_files=True
)

# Variable to hold extracted text from PDFs
context_text = ""

if uploaded_files:
    st.sidebar.write("### File Preview")
    for uploaded_file in uploaded_files:
        # HANDLE PDFs
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                context_text += page.extract_text()
            st.sidebar.success(f"Loaded: {uploaded_file.name} (Text Extracted)")

        # HANDLE IMAGES
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            st.sidebar.image(uploaded_file, caption=uploaded_file.name)

        # HANDLE VIDEOS
        elif uploaded_file.type == "video/mp4":
            st.sidebar.video(uploaded_file)

# --- MODEL SETTINGS ---
st.sidebar.title("Model Settings")
model = st.sidebar.selectbox("Choose Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask about your files or anything else..."):
    # If a PDF was uploaded, attach its text to the prompt secretly
    full_prompt = prompt
    if context_text:
        full_prompt = f"Context from uploaded files:\n{context_text}\n\nUser Question: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Missing API Key!")
        st.stop()

    try:
        client = Groq(api_key=api_key)
        with st.chat_message("assistant"):
            # We send the full_prompt (with PDF data) to the AI
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}]
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error: {e}")