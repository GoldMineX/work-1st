import streamlit as st
from groq import Groq
import os
import base64
from PyPDF2 import PdfReader

st.set_page_config(page_title="Vision Agent Console", layout="wide")

# Helper function to convert image to Base64
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

st.title("👁️ Vision & Document Agent")

# --- API KEY ---
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# --- SIDEBAR: FILE UPLOADER ---
st.sidebar.title("📁 Upload Files")
uploaded_file = st.sidebar.file_uploader(
    "Upload Image or PDF", 
    type=["pdf", "png", "jpg", "jpeg"]
)

context_text = ""
image_base64 = None

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            context_text += page.extract_text()
        st.sidebar.success("PDF Text Extracted")
    
    elif uploaded_file.type in ["image/png", "image/jpeg"]:
        st.sidebar.image(uploaded_file, caption="Vision Preview")
        # Convert image to base64 for the AI to "see" it
        image_base64 = encode_image(uploaded_file)
        st.sidebar.success("Image Ready for Vision")

# --- MODEL SETTINGS ---
# Use the Vision model as default
model = "llama-3.2-11b-vision-preview" 

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask about the image or document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error("Please add API Key!")
        st.stop()

    try:
        client = Groq(api_key=api_key)
        
        # Prepare the content list for Vision
        content = [{"type": "text", "text": f"{prompt}\n\nContext: {context_text}"}]
        
        # If there is an image, add it to the content list
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                },
            })

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error: {e}")