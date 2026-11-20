import time
import streamlit as st
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Video Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor Agent")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
def search_youtube_lesson(search_query: str) -> str:
    """Searches YouTube for an educational video and returns its link and transcript."""
    try:
        results = YoutubeSearch(search_query, max_results=2).to_dict()
        if not results:
            return "No YouTube videos found. Teach the topic directly using your own knowledge."
        video = results[0]
        video_id = video["id"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            transcript = " ".join([t.text for t in YouTubeTranscriptApi().fetch(video_id)])
            return f"Title: {video['title']}\nURL: {url}\nTranscript:\n{transcript[:12000]}"
        except Exception:
            return f"Title: {video['title']}\nURL: {url}\n(Subtitles unavailable on server—share this video link with the student and teach the topic clearly based on the title and your curriculum knowledge.)"
    except Exception:
        return "YouTube search temporarily unavailable. Teach the topic directly and quiz the student."

agent_instructions = """
You are an autonomous AI Tutor for 10X International Schools.
1. When a student names a topic, call `search_youtube_lesson` to find an educational video.
2. Share the YouTube link, explain the core idea simply, and ask ONE diagnostic question.
3. Wait for the student's reply. Never give away answers—give hints or simplify if they struggle.
4. After 2-3 correct answers, congratulate them and offer a harder challenge or new topic.
"""

def create_agent_chat(model_name: str):
    return client.chats.create(
        model=model_name,
        config=types.GenerateContentConfig(
            system_instruction=agent_instructions,
            tools=[search_youtube_lesson],
        ),
    )

if "chat" not in st.session_state:
    st.session_state.chat = create_agent_chat("gemini-3.8-flash")
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
        with st.spinner("Thinking & checking YouTube..."):
            reply_text = None
            for model_option in ["gemini-3.8-flash", "gemini-3.8-flash-lite"]:
                try:
                    if model_option != "gemini-3.8-flash":
                        st.session_state.chat = create_agent_chat(model_option)
                    response = st.session_state.chat.send_message(prompt)
                    reply_text = response.text
                    break
                except Exception:
                    time.sleep(2)
            
            if not reply_text:
                reply_text = "⚠️ Google's AI servers are momentarily busy. Please send your message again in 5 seconds!"
            st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
