import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor")

WELCOME_MSG = (
    "Hey there! 👋 I'm your **10X AI Tutor**, and I'm super excited to help you explore, "
    "watch, and master any subject today! 🚀\n\n"
    "**What topic shall we learn today?**"
)

tutor_instructions = """
You are an enthusiastic, encouraging AI Tutor for 10X International Schools. Follow this exact learning loop:

1. **When the student names a topic to learn:**
   - Excite them briefly about why the topic is cool (1-2 sentences).
   - Provide a clickable YouTube video lesson link using a clean YouTube search URL formatted like this:
     `📺 **Watch Your Mini Video Lesson:** [Click here to watch a short YouTube lesson on <Topic>](https://www.youtube.com/results?search_query=<topic+short+lesson+for+students>)`
     (Replace spaces in the URL with `+`, and recommend a specific trusted channel like Amoeba Sisters, CrashCourse, TED-Ed, or Khan Academy to look for).
   - Give a crisp, easy-to-read 3-bullet summary of the core idea.
   - Ask **ONE** diagnostic question to check their understanding, and invite them to watch the video and reply with their answer.

2. **When the student answers your question:**
   - Do NOT repeat the YouTube video link unless they ask for a new video or a new topic.
   - If they are right: Celebrate their answer, explain briefly why it's correct, and ask a slightly deeper follow-up question to build mastery.
   - If they are wrong or unsure: Encourage them, give a helpful hint without giving away the answer, and let them try again.
   - After 2-3 correct answers, congratulate them on mastering the concept and ask what topic they want to tackle next!

3. **If the student asks a general question (not a lesson topic):**
   - Answer helpfully and warmly, then invite them to pick a topic whenever they're ready to learn.
"""

with st.sidebar:
    st.header("Tutor Controls")
    if st.button("🗑️ Start New Lesson", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MSG}]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MSG}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tell me a topic to learn, or type your answer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Preparing your lesson..."):
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"],
                http_options=types.HttpOptions(api_version="v1beta", timeout=45000),
            )

            if "available_models" not in st.session_state:
                discovered = []
                try:
                    for m in client.models.list():
                        if "gemini" in m.name.lower() and "embed" not in m.name.lower() and "image" not in m.name.lower():
                            discovered.append(m.name.replace("models/", ""))
                except Exception:
                    pass
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
                            system_instruction=tutor_instructions,
                        ),
                    )
                    reply_text = response.text
                    break
                except Exception as e:
                    last_error = f"({model_name}): {e}"
                    time.sleep(1)

            if not reply_text:
                reply_text = f"⚠️ Temporary connection hiccup. Please try again! `{last_error}`"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
