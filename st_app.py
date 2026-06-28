import streamlit as st
from openai import OpenAI
import os
import base64
from PyPDF2 import PdfReader

# Page setup
st.set_page_config(page_title="Samba Agent Console", layout="wide", page_icon="⚡")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("⚡ SambaNova High-Speed Agent")
st.caption("Llama 3.2 Vision • Stable • Ultra-Fast")

# --- 1. API KEY SETUP ---
api_key = os.environ.get("SAMBANOVA_API_KEY")

with st.sidebar:
    st.title("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter SambaNova API Key", type="password")
        st.info("Get your free key at [cloud.sambanova.ai](https://cloud.sambanova.ai/)")
    else:
        st.success("API Key loaded from Render.")
    
    st.markdown("---")
    # Using Llama 3.2 Vision (The most capable free multimodal model)
    model_choice = "Llama-3.2-11B-Vision-Instruct"
    
    st.title("📁 Upload Files")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["pdf", "png", "jpg", "jpeg"])

# --- 2. CHAT HISTORY ---
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
        st.error("Please add your API Key in the sidebar.")
        st.stop()

    try:
        # SambaNova is OpenAI compatible!
        client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key
        )
        
        # Prepare content
        user_content = [{"type": "text", "text": prompt}]
        
        # Handle PDF
        if uploaded_file and uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages])
            user_content[0]["text"] += f"\n\nContext from PDF:\n{pdf_text}"
        
        # Handle Images (Vision)
        if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
            base64_image = encode_image(uploaded_file)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        with st.chat_message("assistant"):
            with st.spinner("SambaNova is thinking..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": user_content}],
                    temperature=0.1 # Lower is more stable
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        st.error(f"Error: {e}")