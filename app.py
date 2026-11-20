import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Assistant", page_icon="🎓")
st.title("🎓 10X International Schools — AI Assistant")

assistant_instructions = """
You are a helpful, intelligent, and friendly AI assistant for 10X International Schools.
- Have a natural, conversational chat with the user about any query they ask (science, math, coding, writing, ideas, general knowledge, or school topics).
- Give clear, direct, well-structured answers tailored to what the user asks.
- Only include YouTube video links or quiz questions if the user specifically asks for them.
"""

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
                http_options=types.HttpOptions(api_version="v1beta", timeout=45000),
            )
            
            # Automatically find all text-generation Gemini models enabled on your API key
            if "available_models" not in st.session_state:
                discovered = []
                try:
                    for m in client.models.list():
                        if "gemini" in m.name.lower() and "embed" not in m.name.lower() and "image" not in m.name.lower():
                            discovered.append(m.name.replace("models/", ""))
                except Exception:
                    pass
                # Prioritize flash models first, then any other discovered Gemini models
                flash_first = [m for m in discovered if "flash" in m] + [m for m in discovered if "flash" not in m]
                st.session_state.available_models = flash_first or ["gemini-3.8-flash", "gemini-3.1-pro-preview"]

            conversation = "\n".join(
                [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
            )
            reply_text = None
            last_error = ""
            for model_name in st.session_state.available_models[:4]:
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
                except Exception as e:
                    last_error = f"({model_name}): {e}"
                    time.sleep(1)

            if not reply_text:
                reply_text = f"⚠️ Could not generate response. Tried: {st.session_state.available_models[:4]}. Last error: `{last_error}`"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
