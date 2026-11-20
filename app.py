import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Assistant", page_icon="🎓")
st.title("🎓 10X International Schools — AI Assistant")

# General, helpful AI assistant instructions
assistant_instructions = """
You are a helpful, intelligent, and friendly AI assistant for 10X International Schools.
- Have a natural, conversational chat with the user about any query they ask (science, math, coding, writing, ideas, general knowledge, or school topics).
- Give clear, direct, well-structured answers tailored to what the user asks.
- Only include YouTube video links or quiz questions if the user specifically asks for them.
"""

# Sidebar with a "New Chat" button to clear conversation anytime
with st.sidebar:
    st.header("Chat Controls")
    if st.button("🗑️ Start New Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm the 10X AI Assistant. Ask me anything!"}
        ]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm the 10X AI Assistant. Ask me anything!"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"],
                http_options=types.HttpOptions(timeout=45000),
            )
            # Send full chat history so it remembers earlier messages in the conversation
            conversation = "\n".join(
                [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
            )
            reply_text = None
            for model_name in ["gemini-3.8-flash", "gemini-3.8-flash", "gemini-2.5-pro"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=conversation,
                        config=types.GenerateContentConfig(
                            system_instruction=assistant_instructions,
                        ),
                    )
                    reply_text = response.text
                    break
                except Exception:
                    time.sleep(2)

            if not reply_text:
                reply_text = "⚠️ Google's AI servers are experiencing a brief traffic spike. Please send your message again in a few seconds!"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
