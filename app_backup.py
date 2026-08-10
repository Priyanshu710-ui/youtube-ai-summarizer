import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
from groq import Groq


# CONFIG
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="🎬",
    layout="wide"
)

LLM_MODEL_NAME = "llama-3.1-8b-instant"
MAX_TRANSCRIPT_CHARS = 12000


# GET YOUTUBE VIDEO ID
def extract_video_id(url):
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?/]|$)",
        r"youtu\.be/([0-9A-Za-z_-]{11})(?:[&?/]|$)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# GET TRANSCRIPT
def get_transcript(video_id):
    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["en", "hi"]
    )

    full_text = " ".join(
        snippet.text for snippet in transcript
    )

    return full_text


# SUMMARIZE
def summarize(transcript, api_key, style):
    client = Groq(api_key=api_key)

    trimmed = transcript[:MAX_TRANSCRIPT_CHARS]

    style_instructions = {
        "Concise summary":
            "Write a concise 3-4 paragraph summary of the video.",

        "Bullet-point takeaways":
            "Extract the 5-8 most important takeaways as a bullet list.",

        "Detailed breakdown":
            "Write a detailed section-by-section breakdown of what is covered, in order."
    }

    prompt = f"""
You are an AI assistant that summarizes YouTube videos.

The transcript below comes directly from a YouTube video.

{style_instructions[style]}

IMPORTANT RULES:
- Only use information present in the transcript.
- Do not invent facts.
- Do not add information from outside sources.
- Keep the summary clear and easy to understand.

Transcript:
{trimmed}

Summary:
"""

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content


# UI
st.title("🎬 AI-Powered YouTube Video Summarizer")

st.caption(
    "Paste a YouTube link and get an instant AI summary "
    "from the video's transcript."
)


# SIDEBAR
with st.sidebar:
    st.header("⚙️ Setup")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API key."
    )

    st.markdown("---")

    st.markdown(
        """
        ### How it works

        **1. Parse**
        
        Extract the YouTube video ID.

        **2. Fetch**
        
        Get the video's transcript.

        **3. Process**
        
        Send the transcript to the AI model.

        **4. Generate**
        
        Generate a summary using only the transcript.
        """
    )


# INPUT
url = st.text_input(
    "YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

style = st.radio(
    "Summary style",
    [
        "Concise summary",
        "Bullet-point takeaways",
        "Detailed breakdown"
    ],
    horizontal=True
)


# SUMMARIZE BUTTON
if st.button("Summarize", type="primary"):

    if not url:
        st.warning("Please paste a YouTube URL first.")
        st.stop()

    if not api_key:
        st.warning("Please enter your Groq API key in the sidebar.")
        st.stop()

    video_id = extract_video_id(url)

    if not video_id:
        st.error("Couldn't recognize the YouTube URL.")
        st.stop()

    try:

        with st.spinner("📄 Fetching video transcript..."):
            transcript = get_transcript(video_id)

        if not transcript.strip():
            st.error("The transcript is empty.")
            st.stop()

        with st.spinner("🤖 AI is generating your summary..."):
            summary = summarize(
                transcript,
                api_key,
                style
            )

        st.success("Summary generated successfully! 🎉")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.video(url)

        with col2:
            st.markdown("### 📝 Summary")
            st.write(summary)

        with st.expander("📄 Show full transcript"):
            st.write(transcript)

    except TranscriptsDisabled:
        st.error("❌ Transcripts are disabled for this video.")

    except NoTranscriptFound:
        st.error(
            "❌ No transcript was found for this video. "
            "The video may not have captions."
        )

    except VideoUnavailable:
        st.error("❌ This YouTube video is unavailable.")

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")

else:
    st.info("Paste a YouTube link and click Summarize to get started.")