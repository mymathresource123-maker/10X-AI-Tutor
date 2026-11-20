import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Video Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor Agent")

agent_instructions = """
You are an autonomous AI Tutor for 10X International Schools.
1. When a student names a topic, use Google Search to find a real, reputable educational YouTube video (e.g., Khan Academy, CrashCourse, TED-Ed, Amoeba Sisters) on that topic.
2. Share the exact YouTube link, explain the core concept clearly in 3-4 simple bullet points, and ask ONE diagnostic multiple-choice question.
3. Wait for the student's reply. Never give away answers immediately—give a helpful hint if they get it wrong.
4. After 2-3 correct answers, congratulate them and ask if they want a harder challenge or a new topic.
"""

# Keep BOTH the client and the chat alive across browser reruns
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=agent_instructions,
            tools=[{"google_search": {}}],
        ),
    )
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! What school topic would you like to master today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type a topic or your answer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Finding YouTube lesson..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply_text = response.text
            except Exception as e:
                reply_text = f"⚠️ Temporary connection hiccup—please try sending that again! ({e})"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
