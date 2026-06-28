import streamlit as st
from openai import OpenAI
import os
import base64
from PyPDF2 import PdfReader

st.set_page_config(page_title="Samba Agent Console", layout="wide", page_icon="⚡")

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("⚡ SambaNova Stable Agent")
st.caption("Auto-detects available models • Vision • PDFs")

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
    
    # SAFE LIST OF CURRENTLY ACTIVE SAMBANOVA MODELS
    safe_models = [
        "Meta-Llama-3.3-70B-Instruct",
        "Meta-Llama-3.1-8B-Instruct",
        "Qwen2.5-72B-Instruct",
        "Llama-3.2-11B-Vision-Instruct"
    ]
    model_choice = st.selectbox("Select Model", safe_models)
    
    st.markdown("---")
    st.title("📁 Upload Files")
    uploaded_file = st.file_uploader("Upload Image or PDF", type=["pdf", "png", "jpg", "jpeg"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your files..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please add your API Key in the sidebar.")
        st.stop()

    try:
        client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key
        )
        
        user_content = [{"type": "text", "text": prompt}]
        
        if uploaded_file and uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            pdf_text = "".join([page.extract_text() for page in reader.pages])
            user_content[0]["text"] += f"\n\nContext from PDF:\n{pdf_text}"
        
        if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
            base64_image = encode_image(uploaded_file)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": user_content}],
                    temperature=0.1
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    except Exception as e:
        st.error(f"Error: {e}")