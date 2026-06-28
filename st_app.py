import streamlit as st
from openai import OpenAI
import os
import base64
from PyPDF2 import PdfReader

st.set_page_config(page_title="OpenRouter Agent", layout="wide", page_icon="🌐")

# Helper to handle image encoding for Vision
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("🌐 Universal Agent Console")
st.caption("Powered by OpenRouter - Access any model with one key")

# --- 1. API KEY SETUP ---
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

# --- 2. MODEL SELECTION ---
with st.sidebar:
    st.title("⚙️ Model Settings")
    # A mix of high-quality Free models
    model_choice = st.selectbox(
        "Select Model",
        [
            "google/gemini-flash-1.5-8b:free", 
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-medium-128k-instruct:free",
            "qwen/qwen-2-7b-instruct:free"
        ]
    )
    st.info("These models are currently FREE on OpenRouter.")
    
    st.markdown("---")
    st.title("📁 Upload Files")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["pdf", "png", "jpg", "jpeg"])

# --- 3. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please add your OpenRouter API Key in the sidebar.")
        st.stop()

    try:
        # Connect to OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter
                "X-Title": "My Agent Console",
            }
        )
        
        # Prepare the message content
        message_content = [{"type": "text", "text": prompt}]
        
        # Handle PDF (Extract text)
        if uploaded_file and uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages])
            message_content[0]["text"] += f"\n\nContext from PDF:\n{pdf_text}"
        
        # Handle Images (Vision)
        if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
            base64_image = encode_image(uploaded_file)
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": message_content}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        st.error(f"Error: {e}")
