import streamlit as st
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types

st.set_page_config(page_title="10X AI Video Tutor", page_icon="🎓")
st.title("🎓 10X International Schools — AI Tutor Agent")

# Connects securely to your hidden API key
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Tool the AI Agent controls autonomously
def search_youtube_lesson(search_query: str) -> str:
    """Searches YouTube for an educational video and returns its link and transcript."""
    video = YoutubeSearch(search_query, max_results=1).to_dict()[0]
    video_id = video["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        transcript = " ".join([t.text for t in YouTubeTranscriptApi().fetch(video_id)])
        return f"Title: {video['title']}\nURL: {url}\nTranscript:\n{transcript[:12000]}"
    except Exception:
        return f"Found {url}, but captions were unavailable. Try another search."

agent_instructions = """
You are an autonomous AI Tutor for 10X International Schools.
1. When a student names a topic, call `search_youtube_lesson` to find a video with captions.
2. Share the YouTube link, explain the core idea simply, and ask ONE diagnostic question.
3. Wait for the student's reply. Never give away answers—give hints or find a simpler video if they struggle.
4. After 2-3 correct answers, congratulate them and offer a harder challenge or new topic.
"""

# Initialize chat memory for the student's browser session
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=agent_instructions,
            tools=[search_youtube_lesson],
        ),
    )
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! What school topic would you like to master today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Student chat input box
if prompt := st.chat_input("Type a topic or your answer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking & checking YouTube..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
