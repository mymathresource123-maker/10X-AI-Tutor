import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Video Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor Agent")

agent_instructions = """
You are an autonomous AI Tutor for 10X International Schools.
1. When a student names a topic, recommend a reputable educational YouTube video (from Khan Academy, CrashCourse, TED-Ed, or Amoeba Sisters) with a clickable YouTube search link (e.g., https://www.youtube.com/results?search_query=sunlight+for+kids+science) so the link never breaks.
2. Explain the core concept clearly in 3-4 simple bullet points, and ask ONE diagnostic multiple-choice question.
3. Wait for the student's reply. Never give away answers immediately—give a helpful hint if they get it wrong.
4. After 2-3 correct answers, congratulate them and ask if they want a harder challenge or a new topic.
"""

if "messages" not in st.session_state:
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
        with st.spinner("Preparing your lesson..."):
            try:
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"],
                    http_options=types.HttpOptions(timeout=15000),  # 15-second max wait
                )
                # Send full conversation history cleanly on each turn
                conversation = "\n".join(
                    [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
                )
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        system_instruction=agent_instructions,
                    ),
                )
                reply_text = response.text
            except Exception as e:
                reply_text = f"⚠️ Could not connect in time: {e}"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
