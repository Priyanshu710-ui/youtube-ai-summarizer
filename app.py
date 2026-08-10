import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Video Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SECURE API KEY
# =========================================================

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    API_KEY = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =========================
   REMOVE DEFAULT STREAMLIT UI
   ========================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* =========================
   MAIN APP
   ========================= */

.stApp {
    background: #ffffff;
}


/* =========================
   SIDEBAR
   ========================= */

[data-testid="stSidebar"] {
    background: #f7f9fc;
    border-right: 1px solid #e5e7eb;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}


/* Logo */

.logo {
    font-size: 25px;
    font-weight: 800;
    color: #111827 !important;
    margin-bottom: 25px;
}

.logo-icon {
    background: #3155ff;
    color: #ffffff !important;
    padding: 8px 11px;
    border-radius: 9px;
    margin-right: 8px;
}


/* Sidebar menu */

.side-item {
    padding: 12px 10px;
    color: #4b5563 !important;
    font-size: 16px;
    border-radius: 8px;
    margin: 3px 0;
}

.side-item.active {
    background: #e5ebf5;
    color: #111827 !important;
    font-weight: 700;
}


/* =========================
   HERO
   ========================= */

.hero {
    text-align: center;
    padding: 45px 20px 25px 20px;
}

.hero h1 {
    font-size: 58px;
    line-height: 1.05;
    font-weight: 800;
    color: #111827 !important;
    margin-bottom: 22px;
}

.hero p {
    font-size: 19px;
    color: #64748b !important;
    max-width: 850px;
    margin: auto;
}


/* =========================
   TEXT
   ========================= */

.input-title {
    font-size: 16px;
    font-weight: 700;
    color: #334155 !important;
    margin-bottom: 8px;
}

label {
    color: #334155 !important;
}


/* =========================
   TEXT INPUT
   ========================= */

.stTextInput input {
    color: #111827 !important;
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    font-size: 16px !important;
}

.stTextInput input::placeholder {
    color: #94a3b8 !important;
}


/* =========================
   SELECTBOX
   ========================= */

/* Main select box */

[data-baseweb="select"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}


/* Select box inner area */

[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border-color: #cbd5e1 !important;
}


/* Selected text */

[data-baseweb="select"] span {
    color: #111827 !important;
}


/* Arrow */

[data-baseweb="select"] svg {
    fill: #111827 !important;
    color: #111827 !important;
}


/* Dropdown popup */

[role="listbox"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
}


/* Dropdown options */

[role="option"] {
    background: #ffffff !important;
    color: #111827 !important;
}


/* Dropdown option text */

[role="option"] * {
    color: #111827 !important;
}


/* Hover */

[role="option"]:hover {
    background: #eef2ff !important;
    color: #111827 !important;
}


/* =========================
   TABS
   ========================= */

button[data-baseweb="tab"] {
    color: #475569 !important;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #3155ff !important;
}


/* =========================
   BUTTON
   ========================= */

.stButton button {
    font-weight: 700 !important;
}


/* =========================
   SUMMARY
   ========================= */

.summary-heading {
    font-size: 30px;
    font-weight: 800;
    color: #111827 !important;
    margin-bottom: 18px;
}

.summary-text {
    color: #111827 !important;
    font-size: 17px;
    line-height: 1.75;
}

.summary-text p {
    color: #111827 !important;
}

.summary-text li {
    color: #111827 !important;
}

.summary-text strong {
    color: #111827 !important;
}

.summary-text h1,
.summary-text h2,
.summary-text h3,
.summary-text h4 {
    color: #111827 !important;
}


/* =========================
   MARKDOWN
   ========================= */

[data-testid="stMarkdownContainer"] p {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] li {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] strong {
    color: #111827 !important;
}


/* =========================
   SUCCESS MESSAGE
   ========================= */

.success-box {
    background: #dcfce7;
    border: 1px solid #86efac;
    color: #166534 !important;
    padding: 15px;
    border-radius: 10px;
    font-weight: 600;
    margin-top: 25px;
}


/* =========================
   ALERTS
   ========================= */

[data-testid="stAlert"] {
    color: #111827 !important;
}


/* =========================
   VIDEO
   ========================= */

iframe {
    border-radius: 14px;
}


/* =========================
   MOBILE
   ========================= */

@media (max-width: 900px) {

    .hero h1 {
        font-size: 40px;
    }

    .hero p {
        font-size: 16px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCTIONS
# =========================================================

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


def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["en", "hi"]
    )

    return " ".join(
        snippet.text for snippet in transcript
    )


def summarize(transcript, style, language):

    client = Groq(api_key=API_KEY)

    trimmed = transcript[:12000]

    instructions = {

        "Concise Summary": """
        Write a clear 3-4 paragraph summary.
        Focus on the main topic, important arguments,
        facts and conclusions.
        """,

        "Key Takeaways": """
        Extract the 6-10 most important points.
        Use clear bullet points.
        """,

        "Detailed Breakdown": """
        Create a detailed section-by-section breakdown.
        Explain the topics in the order they appear.
        """,

        "Study Notes": """
        Convert the transcript into clean study notes.
        Use headings, subheadings and bullet points.
        Highlight important concepts.
        """
    }

    prompt = f"""
You are an expert AI video summarizer.

Summarize the following YouTube video transcript.

SUMMARY STYLE:
{instructions[style]}

OUTPUT LANGUAGE:
{language}

IMPORTANT RULES:
- Only use information present in the transcript.
- Do not invent facts.
- Do not add information from outside the transcript.
- Keep the answer accurate.
- Make it easy to read.
- Use Markdown headings and bullet points where useful.

TRANSCRIPT:
{trimmed}

Generate the summary now.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
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

    st.markdown("""
    <div class="logo">
        <span class="logo-icon">▤</span>
        AI Video Summarizer
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "＋  New Video",
        use_container_width=True
    ):

        st.session_state.clear()
        st.rerun()

    st.markdown("""
    <div class="side-item active">
        ⌂ &nbsp; Home
    </div>

    <div class="side-item">
        ▶ &nbsp; YouTube Video
    </div>

    <div class="side-item">
        📝 &nbsp; Transcript
    </div>

    <div class="side-item">
        📄 &nbsp; My Summaries
    </div>

    <div class="side-item">
        ⚙ &nbsp; Settings
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### ✨ AI Powered")

    st.caption(
        "Paste a video link and let AI do the work."
    )


# =========================================================
# CHECK API KEY
# =========================================================

if API_KEY is None:

    st.error(
        "⚠️ Groq API key is not configured. "
        "Please add GROQ_API_KEY to "
        ".streamlit/secrets.toml."
    )

    st.stop()


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">

<h1>
Summarize Any Video<br>
Instantly with AI
</h1>

<p>
Get clear summaries, key takeaways and study notes
from YouTube videos in seconds.
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "▶ YouTube Video",
    "♪ TikTok Video",
    "◎ Instagram Video",
    "📁 Files"
])


# =========================================================
# YOUTUBE TAB
# =========================================================

with tab1:

    st.markdown(
        '<div class="input-title">YouTube Video URL</div>',
        unsafe_allow_html=True
    )

    url = st.text_input(
        "YouTube URL",
        placeholder="Paste the YouTube video link here...",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        language = st.selectbox(
            "Output Language",
            [
                "Auto",
                "English",
                "Hindi"
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

    st.markdown("<br>", unsafe_allow_html=True)

    generate = st.button(
        "✨  Generate AI Summary",
        type="primary",
        use_container_width=True
    )


# =========================================================
# OTHER TABS
# =========================================================

with tab2:

    st.info(
        "TikTok summarization is coming soon."
    )


with tab3:

    st.info(
        "Instagram video summarization is coming soon."
    )


with tab4:

    st.info(
        "PDF, video and audio summarization are coming soon."
    )


# =========================================================
# GENERATE SUMMARY
# =========================================================

if generate:

    if not url:

        st.warning(
            "Please paste a YouTube video URL."
        )

        st.stop()


    video_id = extract_video_id(url)

    if not video_id:

        st.error(
            "Invalid YouTube URL. Please check the link."
        )

        st.stop()


    try:

        # =================================================
        # FETCH TRANSCRIPT
        # =================================================

        with st.spinner(
            "🔎 Fetching video transcript..."
        ):

            transcript = get_transcript(video_id)


        if not transcript.strip():

            st.error(
                "No transcript was found for this video."
            )

            st.stop()


        # =================================================
        # GENERATE SUMMARY
        # =================================================

        with st.spinner(
            "🤖 AI is creating your summary..."
        ):

            summary = summarize(
                transcript,
                style,
                language
            )


        # =================================================
        # SUCCESS
        # =================================================

        st.markdown(
            """
            <div class="success-box">
                ✓ Summary generated successfully!
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)


        # =================================================
        # RESULT
        # =================================================

        left, right = st.columns(
            [1, 1.5],
            gap="large"
        )


        # VIDEO

        with left:

            st.video(url)


        # SUMMARY

        with right:

            st.markdown(
                '<div class="summary-heading">📝 AI Summary</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="summary-text">{summary}</div>',
                unsafe_allow_html=True
            )


        # =================================================
        # TRANSCRIPT
        # =================================================

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander(
            "📄 View Full Transcript"
        ):

            st.write(transcript)


        # =================================================
        # DOWNLOAD
        # =================================================

        st.download_button(
            "⬇ Download Summary",
            summary,
            file_name="youtube_summary.txt",
            mime="text/plain"
        )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except TranscriptsDisabled:

        st.error(
            "❌ Transcripts are disabled for this video."
        )


    except NoTranscriptFound:

        st.error(
            "❌ No transcript was found for this video."
        )


    except VideoUnavailable:

        st.error(
            "❌ This YouTube video is unavailable."
        )


    except Exception as e:

        st.error(
            f"❌ Something went wrong: {e}"
        )


# =========================================================
# INITIAL MESSAGE
# =========================================================

else:

    st.info(
        "Paste a YouTube link and click "
        "Generate AI Summary to get started."
    )