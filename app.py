import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CONFIG
# =========================================================

MODEL = "llama-3.1-8b-instant"
MAX_TRANSCRIPT_CHARS = 12000

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #f5f7fb;
}

/* HERO */

.hero-title {
    text-align: center;
    font-size: 64px;
    font-weight: 800;
    line-height: 1.08;
    color: #111827;
    margin-top: 20px;
    margin-bottom: 25px;
}

.hero-subtitle {
    text-align: center;
    font-size: 22px;
    color: #374151;
    margin-bottom: 45px;
}

/* BUTTON */

.stButton > button {
    width: 100%;
    height: 58px;
    border-radius: 12px;
    border: none;
    background-color: #ff4b4b;
    color: white;
    font-size: 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #e63e3e;
    color: white;
}

/* SUMMARY */

.summary-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 30px;
    margin-top: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.summary-title {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 20px;
}

/* FEATURE CARDS */

.feature-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 20px;
    min-height: 150px;
}

.feature-card h3 {
    color: #111827;
}

.feature-card p {
    color: #4b5563;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# API KEY
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = None

# =========================================================
# FUNCTIONS
# =========================================================

def extract_video_id(url):
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    text = " ".join(
        snippet.text
        for snippet in transcript
    )

    return text


def generate_summary(transcript, style, language):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    transcript = transcript[:MAX_TRANSCRIPT_CHARS]

    style_instructions = {

        "Concise Summary":
            """
            Create a concise summary in 3-5 paragraphs.
            Keep it simple and easy to understand.
            """,

        "Key Takeaways":
            """
            Extract 6-10 important key takeaways.
            Use clear bullet points.
            """,

        "Detailed Breakdown":
            """
            Create a detailed breakdown of the video.
            Use headings and bullet points.
            Follow the order of topics in the video.
            """,

        "Study Notes":
            """
            Convert the video into clear study notes.
            Include headings, important concepts,
            definitions, examples and key points.
            """
    }

    language_instruction = ""

    if language != "Auto":
        language_instruction = f"""
Write the final answer in {language}.
"""

    prompt = f"""
You are an expert YouTube video summarizer.

{style_instructions[style]}

{language_instruction}

IMPORTANT RULES:

1. Use ONLY information present in the transcript.
2. Do not invent facts.
3. Do not add information that is not in the transcript.
4. Make the answer easy to understand.
5. Use Markdown headings and bullet points.
6. Remove unnecessary repetition.
7. Focus on the most useful information.

VIDEO TRANSCRIPT:

{transcript}

FINAL SUMMARY:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1200
    )

    return response.choices[0].message.content


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style="font-size:28px;">
        📄 AI Video<br>
        Summarizer
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.button("＋ New Video")

    st.markdown("---")

    st.markdown("### 🏠 Home")
    st.markdown("▶️ YouTube Video")
    st.markdown("📝 Transcript")
    st.markdown("📄 My Summaries")
    st.markdown("⚙️ Settings")

    st.markdown("---")

    st.markdown("### ✨ AI Powered")

    st.caption(
        "Paste a video link and let AI do the work."
    )


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero-title">
        Summarize Any Video<br>
        Instantly with AI
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-subtitle">
        Get clear summaries, key takeaways and study notes
        from YouTube videos in seconds.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TABS
# =========================================================

youtube_tab, tiktok_tab, instagram_tab, files_tab = st.tabs(
    [
        "▶ YouTube Video",
        "♪ TikTok Video",
        "◎ Instagram Video",
        "📁 Files"
    ]
)

# =========================================================
# YOUTUBE
# =========================================================

with youtube_tab:

    st.markdown("## YouTube Video")

    url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    col1, col2 = st.columns(2)

    with col1:

        language = st.selectbox(
            "Output Language",
            [
                "Auto",
                "English",
                "Hindi",
                "Spanish",
                "French",
                "German"
            ]
        )

    with col2:

        style = st.selectbox(
            "Summary Template",
            [
                "Concise Summary",
                "Key Takeaways",
                "Detailed Breakdown",
                "Study Notes"
            ]
        )

    st.write("")

    generate = st.button(
        "✨ Generate AI Summary",
        type="primary"
    )

    if generate:

        # -------------------------------------------------
        # CHECK API
        # -------------------------------------------------

        if not GROQ_API_KEY:

            st.error(
                "❌ GROQ_API_KEY is not configured."
            )

            st.info(
                "Add GROQ_API_KEY in Streamlit Cloud → "
                "Manage app → Settings → Secrets."
            )

        # -------------------------------------------------
        # CHECK URL
        # -------------------------------------------------

        elif not url:

            st.warning(
                "Please paste a YouTube video URL first."
            )

        else:

            video_id = extract_video_id(url)

            if not video_id:

                st.error(
                    "❌ Invalid YouTube URL."
                )

            else:

                try:

                    # =====================================
                    # TRANSCRIPT
                    # =====================================

                    with st.spinner(
                        "🎧 Fetching video transcript..."
                    ):

                        transcript = get_transcript(
                            video_id
                        )

                    if not transcript.strip():

                        st.error(
                            "❌ No transcript was found."
                        )

                    else:

                        # =================================
                        # AI SUMMARY
                        # =================================

                        with st.spinner(
                            "🤖 AI is generating your summary..."
                        ):

                            summary = generate_summary(
                                transcript,
                                style,
                                language
                            )

                        st.success(
                            "✓ Summary generated successfully!"
                        )

                        # =================================
                        # RESULT
                        # =================================

                        video_col, summary_col = st.columns(
                            [1, 2]
                        )

                        with video_col:

                            st.video(url)

                        with summary_col:

                            st.markdown(
                                """
                                <div class="summary-title">
                                📝 AI Summary
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            st.markdown(
                                summary
                            )

                        # =================================
                        # TRANSCRIPT
                        # =================================

                        with st.expander(
                            "📄 Show Full Transcript"
                        ):

                            st.write(
                                transcript
                            )

                except Exception as e:

                    error = str(e)

                    # -------------------------------------
                    # FRIENDLY ERRORS
                    # -------------------------------------

                    if "TranscriptsDisabled" in error:

                        st.error(
                            "❌ Transcripts are disabled "
                            "for this video."
                        )

                    elif "NoTranscriptFound" in error:

                        st.error(
                            "❌ No transcript was found "
                            "for this video."
                        )

                    elif "Could not retrieve" in error:

                        st.error(
                            "❌ YouTube did not provide "
                            "an accessible transcript."
                        )

                    else:

                        st.error(
                            f"❌ Something went wrong: {error}"
                        )


# =========================================================
# TIKTOK
# =========================================================

with tiktok_tab:

    st.info(
        "♪ TikTok summarization is coming soon."
    )


# =========================================================
# INSTAGRAM
# =========================================================

with instagram_tab:

    st.info(
        "◎ Instagram summarization is coming soon."
    )


# =========================================================
# FILES
# =========================================================

with files_tab:

    st.info(
        "📁 File summarization is coming soon."
    )


# =========================================================
# FEATURES
# =========================================================

st.markdown("---")

st.markdown(
    "### ✨ Why use AI Video Summarizer?"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        """
        <div class="feature-card">
        <h3>⚡ Fast</h3>
        <p>
        Turn long YouTube videos into useful
        summaries in seconds.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        """
        <div class="feature-card">
        <h3>🧠 AI Powered</h3>
        <p>
        Get concise summaries, key takeaways
        and study notes automatically.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        """
        <div class="feature-card">
        <h3>🔒 Secure</h3>
        <p>
        Visitors don't need to enter an API key.
        Your Groq key stays in Streamlit Secrets.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )