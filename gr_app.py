import streamlit as st
from openai import OpenAI
import os
import base64
from PyPDF2 import PdfReader

# --- PAGE CONFIG ---
st.set_page_config(page_title="Universal Agent Console", layout="wide", page_icon="🌐")

# Helper to handle image encoding for Vision models
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("🌐 Universal Agent Console")
st.markdown("---")

# --- 1. API KEY SETUP ---
# Checks Render Environment Variables first, then Sidebar
api_key = os.environ.get("OPENROUTER_API_KEY")

with st.sidebar:
    st.title("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter OpenRouter API Key", type="password")
        st.info("Get a free key at [openrouter.ai](https://openrouter.ai/)")
    else:
        st.success("API Key loaded from Render!")
    
    st.markdown("---")
    # Selection of the most stable FREE models on OpenRouter
    model_choice = st.selectbox(
        "Select AI Model (Free)",
        [
            "google/gemini-flash-1.5-8b:free", 
            "meta-llama/llama-3.1-8b-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free"
        ]
    )
    st.caption("Tip: If you get a 404, switch to Gemini Flash.")
    
    st.markdown("---")
    st.title("📁 Upload Files")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["pdf", "png", "jpg", "jpeg"])

# --- 2. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. CHAT LOGIC ---
if prompt := st.chat_input("Ask about your files or anything else..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please add your OpenRouter API Key in the sidebar.")
        st.stop()

    try:
        # Initialize OpenAI client with OpenRouter base URL
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://render.com", # Required for OpenRouter
                "X-Title": "Agent Console",
            }
        )
        
        # Prepare the message content structure
        # We start with the text prompt
        user_content = [{"type": "text", "text": prompt}]
        
        # --- Handle PDF (Extract Text) ---
        if uploaded_file and uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()
            user_content[0]["text"] += f"\n\n[CONTEXT FROM PDF]:\n{pdf_text}"
        
        # --- Handle Images (Vision) ---
        if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
            base64_image = encode_image(uploaded_file)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        # Generate the response
        with st.chat_message("assistant"):
            with st.spinner(f"Agent using {model_choice}..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": user_content}]
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
            
        # Save response to history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Troubleshooting: This 404/500 usually means the specific free model is overloaded. Try switching the 'Model' in the sidebar to Gemini Flash or Llama.")