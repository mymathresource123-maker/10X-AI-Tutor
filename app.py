import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Video Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor Agent")

agent_instructions = """
You are an intelligent, friendly AI Tutor and Learning Companion for 10X International Schools.
Adapt your response based on what the student asks:

MODE 1: GENERAL QUESTIONS & DOUBTS (e.g., "What can AI do?", "How do I study better?", or quick concept questions)
- Answer clearly, warmly, and directly in plain English appropriate for a school student.
- Do NOT force a YouTube video or a multiple-choice quiz unless the student asks to learn or practice a full school topic.
- End by briefly offering: "Would you like a video lesson and a quick quiz on this, or do you have another question?"

MODE 2: SCHOOL TOPIC MASTERY (e.g., "Photosynthesis", "Teach me Quadratic Equations", "Newton's Laws")
- Recommend a reputable educational YouTube video (from Khan Academy, CrashCourse, TED-Ed, or Amoeba Sisters) with a clickable YouTube search link (e.g., https://www.youtube.com/results?search_query=photosynthesis+amoeba+sisters).
- Explain the core concept clearly in 3-4 simple bullet points, and ask ONE diagnostic multiple-choice question.
- Wait for the student's reply. Never give away answers immediately—give a helpful hint if they get it wrong.
- After 2-3 correct answers, congratulate them and ask if they want a harder challenge or a new topic.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me any question, or name a school topic you'd like to master with a video lesson and quiz!"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question, enter a topic, or type your answer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"],
                http_options=types.HttpOptions(timeout=45000),
            )
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
                            system_instruction=agent_instructions,
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
