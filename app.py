import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI YouTube Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

LLM_MODEL = "llama-3.1-8b-instant"
MAX_TRANSCRIPT_CHARS = 12000

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

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
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] h1 {
    color: #111827;
}

/* Main heading */

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

/* Tabs */

.tab-title {
    font-size: 18px;
    font-weight: 600;
    padding-bottom: 12px;
    border-bottom: 3px solid #ff4b4b;
    display: inline-block;
}

/* Labels */

label {
    font-weight: 600 !important;
}

/* Button */

.stButton > button {
    width: 100%;
    height: 58px;
    border-radius: 12px;
    border: none;
    background: #ff4b4b;
    color: white;
    font-size: 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #e63e3e;
    color: white;
}

/* Summary */

.summary-box {
    background: #ffffff;
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

/* Info box */

.info-box {
    background: #e8f3ff;
    border-radius: 12px;
    padding: 18px;
    color: #1f2937;
    font-size: 17px;
}

/* Feature cards */

.feature-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 20px;
    height: 100%;
}

.feature-card h3 {
    color: #111827;
}

.feature-card p {
    color: #4b5563;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------

def extract_video_id(url):
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def get_transcript(video_id):

    # Current youtube-transcript-api
    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    text = " ".join(
        snippet.text
        for snippet in transcript
    )

    return text


def summarize(transcript, api_key, style, language):

    client = Groq(api_key=api_key)

    transcript = transcript[:MAX_TRANSCRIPT_CHARS]

    styles = {
        "Concise Summary":
            "Create a concise and easy-to-read summary in 3-5 paragraphs.",

        "Key Takeaways":
            "Create 6-10 important key takeaways using bullet points.",

        "Detailed Breakdown":
            "Create a detailed breakdown of the video with headings and bullet points.",

        "Study Notes":
            "Convert the video into clear study notes with headings, definitions, important points and examples."
    }

    language_instruction = ""

    if language != "Auto":
        language_instruction = f"""
Write the final answer in {language}.
"""

    prompt = f"""
You are an expert YouTube video summarizer.

{styles[style]}

{language_instruction}

Rules:
- Use ONLY information contained in the transcript.
- Do not invent facts.
- Make the answer easy to read.
- Use Markdown headings and bullet points where appropriate.
- Focus on useful information.
- Remove unnecessary repetition.

Transcript:

{transcript}

Summary:
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
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


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# GET API KEY FROM STREAMLIT SECRETS
# ---------------------------------------------------------

try:

    api_key = st.secrets["GROQ_API_KEY"]

except Exception:

    api_key = None


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# SOURCE TABS
# ---------------------------------------------------------

tabs = st.tabs([
    "▶ YouTube Video",
    "♪ TikTok Video",
    "◎ Instagram Video",
    "📁 Files"
])

with tabs[0]:

    st.markdown(
        '<div class="tab-title">YouTube Video</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    url = st.text_input(
        "YouTube Video URL",
        placeholder="Paste the YouTube video link here...",
        label_visibility="visible"
    )

    # -----------------------------------------------------
    # OPTIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    generate = st.button(
        "✨ Generate AI Summary",
        type="primary"
    )

    if generate:

        if not url:

            st.warning(
                "Please paste a YouTube video URL first."
            )

        elif not api_key:

            st.error(
                "AI configuration is missing. "
                "Please configure GROQ_API_KEY in Streamlit Secrets."
            )

        else:

            video_id = extract_video_id(url)

            if not video_id:

                st.error(
                    "Invalid YouTube URL. "
                    "Please enter a valid YouTube video link."
                )

            else:

                try:

                    # -----------------------------------------
                    # TRANSCRIPT
                    # -----------------------------------------

                    with st.spinner(
                        "🎧 Fetching video transcript..."
                    ):

                        transcript = get_transcript(
                            video_id
                        )

                    if not transcript.strip():

                        st.error(
                            "No transcript text was found for this video."
                        )

                    else:

                        # -------------------------------------
                        # AI SUMMARY
                        # -------------------------------------

                        with st.spinner(
                            "🤖 AI is generating your summary..."
                        ):

                            summary = summarize(
                                transcript,
                                api_key,
                                style,
                                language
                            )

                        st.success(
                            "✓ Summary generated successfully!"
                        )

                        # -------------------------------------
                        # RESULT
                        # -------------------------------------

                        video_col, summary_col = st.columns(
                            [1, 2]
                        )

                        with video_col:

                            st.video(
                                url
                            )

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

                        # -------------------------------------
                        # TRANSCRIPT
                        # -------------------------------------

                        with st.expander(
                            "📄 Show Full Transcript"
                        ):

                            st.write(
                                transcript
                            )

                except Exception as e:

                    error_text = str(e)

                    if (
                        "TranscriptsDisabled"
                        in error_text
                    ):

                        st.error(
                            "❌ Transcripts are disabled "
                            "for this video."
                        )

                    elif (
                        "NoTranscriptFound"
                        in error_text
                    ):

                        st.error(
                            "❌ No transcript was found "
                            "for this video."
                        )

                    elif (
                        "Could not retrieve a transcript"
                        in error_text
                    ):

                        st.error(
                            "❌ YouTube did not provide "
                            "a transcript for this video."
                        )

                    else:

                        st.error(
                            f"❌ Something went wrong: {error_text}"
                        )


with tabs[1]:

    st.info(
        "TikTok summarization is coming soon."
    )


with tabs[2]:

    st.info(
        "Instagram summarization is coming soon."
    )


with tabs[3]:

    st.info(
        "File summarization is coming soon."
    )


# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------

st.markdown("---")

st.markdown(
    "### ✨ Why use AI Video Summarizer?"
)

f1, f2, f3 = st.columns(3)

with f1:

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

with f2:

    st.markdown(
        """
        <div class="feature-card">
        <h3>🧠 AI Powered</h3>
        <p>
        Get concise summaries, key takeaways
        and study notes.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:

    st.markdown(
        """
        <div class="feature-card">
        <h3>🔒 Private API</h3>
        <p>
        Visitors don't need to enter an API key.
        The AI key stays securely on the server.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )