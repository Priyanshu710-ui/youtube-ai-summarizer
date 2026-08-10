import os
import re
import tempfile
from urllib.parse import urlparse

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import yt_dlp

try:
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Video Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CONFIG
# =========================================================

MODEL = "llama-3.1-8b-instant"
WHISPER_MODEL = "whisper-large-v3-turbo"
MAX_TEXT_CHARS = 12000
MAX_AUDIO_BYTES = 25 * 1024 * 1024


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background-color: #f5f7fb;
    }

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

    .stButton > button {
        width: 100%;
        min-height: 58px;
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

    .summary-title {
        font-size: 30px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 20px;
    }

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
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API KEY
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================================================
# HELPERS
# =========================================================

def get_groq_client():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it in Streamlit "
            "Cloud → Manage app → Settings → Secrets."
        )
    return Groq(api_key=GROQ_API_KEY)


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


def get_youtube_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    text = " ".join(
        snippet.text
        for snippet in transcript
    )

    return text


def generate_summary(text, style, language, source_name="video"):
    client = get_groq_client()

    text = text[:MAX_TEXT_CHARS]

    style_instructions = {
        "Concise Summary": """
Create a concise summary in 3-5 paragraphs.
Keep it simple and easy to understand.
""",
        "Key Takeaways": """
Extract 6-10 important key takeaways.
Use clear bullet points.
""",
        "Detailed Breakdown": """
Create a detailed breakdown.
Use headings and bullet points.
Follow the order of topics in the content.
""",
        "Study Notes": """
Convert the content into clear study notes.
Include headings, important concepts, definitions, examples and key points.
""",
    }

    language_instruction = ""
    if language != "Auto":
        language_instruction = f"Write the final answer in {language}."

    prompt = f"""
You are an expert {source_name} summarizer.

{style_instructions[style]}

{language_instruction}

IMPORTANT RULES:
1. Use ONLY information present in the supplied content.
2. Do not invent facts.
3. Do not add information that is not present.
4. Make the answer easy to understand.
5. Use Markdown headings and bullet points.
6. Remove unnecessary repetition.
7. Focus on useful information.

CONTENT:
{text}

FINAL SUMMARY:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1200,
    )

    return response.choices[0].message.content


def is_social_url(url, platform):
    try:
        host = urlparse(url).netloc.lower()
        host = host.split(":")[0]

        if platform == "TikTok":
            return host == "tiktok.com" or host.endswith(".tiktok.com")

        if platform == "Instagram":
            return host == "instagram.com" or host.endswith(".instagram.com")

    except Exception:
        return False

    return False


def download_social_media(url):
    """
    Download public TikTok/Instagram media to a temporary file.

    We intentionally avoid requiring ffmpeg here. The downloaded media
    is sent directly to Groq Whisper when it is one of the supported
    formats.
    """

    temp_dir = tempfile.mkdtemp(prefix="ai_video_")

    output_template = os.path.join(temp_dir, "media.%(ext)s")

    options = {
        "outtmpl": output_template,
        "format": (
            "bestaudio[ext=m4a]/"
            "bestaudio[ext=webm]/"
            "best[ext=mp4]/"
            "best"
        ),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "max_filesize": MAX_AUDIO_BYTES,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded = ydl.prepare_filename(info)

    if not os.path.exists(downloaded):
        candidates = [
            os.path.join(temp_dir, name)
            for name in os.listdir(temp_dir)
        ]

        if not candidates:
            raise RuntimeError("Media could not be downloaded.")

        downloaded = candidates[0]

    size = os.path.getsize(downloaded)

    if size > MAX_AUDIO_BYTES:
        raise RuntimeError(
            "The downloaded video/audio is larger than Groq's 25 MB "
            "file limit. Try a shorter video."
        )

    return downloaded


def transcribe_social_media(file_path, language):
    client = get_groq_client()

    with open(file_path, "rb") as media_file:
        kwargs = {
            "file": media_file,
            "model": WHISPER_MODEL,
            "response_format": "json",
            "temperature": 0.0,
        }

        if language != "Auto":
            language_codes = {
                "English": "en",
                "Hindi": "hi",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
            }

            if language in language_codes:
                kwargs["language"] = language_codes[language]

        result = client.audio.transcriptions.create(**kwargs)

    return result.text


def extract_pdf_text(uploaded_file):
    if PdfReader is None:
        raise RuntimeError(
            "PyPDF2 is not installed. Run: pip install PyPDF2"
        )

    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)

    return "\n\n".join(pages)


def extract_docx_text(uploaded_file):
    if Document is None:
        raise RuntimeError(
            "python-docx is not installed. Run: pip install python-docx"
        )

    document = Document(uploaded_file)
    return "\n\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )


def show_social_result(media_path, transcript, summary):
    st.success("✓ Summary generated successfully!")

    video_col, summary_col = st.columns([1, 2])

    with video_col:
        st.video(media_path)

    with summary_col:
        st.markdown(
            '<div class="summary-title">📝 AI Summary</div>',
            unsafe_allow_html=True,
        )
        st.markdown(summary)

    with st.expander("📄 Show Transcript"):
        st.write(transcript)


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
        unsafe_allow_html=True,
    )

    st.button("＋ New Video")

    st.markdown("---")
    st.markdown("### 🏠 Home")
    st.markdown("▶️ YouTube Video")
    st.markdown("🎵 TikTok Video")
    st.markdown("◎ Instagram Video")
    st.markdown("📝 Transcript")
    st.markdown("📄 My Summaries")
    st.markdown("⚙️ Settings")

    st.markdown("---")
    st.markdown("### ✨ AI Powered")
    st.caption("Paste a video link or upload a file and let AI do the work.")


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
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        Get clear summaries, key takeaways and study notes
        from videos in seconds.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

youtube_tab, tiktok_tab, instagram_tab, files_tab = st.tabs(
    [
        "▶ YouTube Video",
        "♪ TikTok Video",
        "◎ Instagram Video",
        "📁 Files",
    ]
)


# =========================================================
# YOUTUBE
# =========================================================

with youtube_tab:
    st.markdown("## YouTube Video")

    url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_url",
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
                "German",
            ],
            key="youtube_language",
        )

    with col2:
        style = st.selectbox(
            "Summary Template",
            [
                "Concise Summary",
                "Key Takeaways",
                "Detailed Breakdown",
                "Study Notes",
            ],
            key="youtube_style",
        )

    st.write("")

    generate_youtube = st.button(
        "✨ Generate AI Summary",
        type="primary",
        key="youtube_generate",
    )

    if generate_youtube:
        if not GROQ_API_KEY:
            st.error("❌ GROQ_API_KEY is not configured.")
            st.info(
                "Add GROQ_API_KEY in Streamlit Cloud → "
                "Manage app → Settings → Secrets."
            )

        elif not url:
            st.warning("Please paste a YouTube video URL first.")

        else:
            video_id = extract_video_id(url)

            if not video_id:
                st.error("❌ Invalid YouTube URL.")

            else:
                try:
                    with st.spinner("🎧 Fetching video transcript..."):
                        transcript = get_youtube_transcript(video_id)

                    if not transcript.strip():
                        st.error("❌ No transcript was found.")

                    else:
                        with st.spinner(
                            "🤖 AI is generating your summary..."
                        ):
                            summary = generate_summary(
                                transcript,
                                style,
                                language,
                                "YouTube video",
                            )

                        st.success("✓ Summary generated successfully!")

                        video_col, summary_col = st.columns([1, 2])

                        with video_col:
                            st.video(url)

                        with summary_col:
                            st.markdown(
                                '<div class="summary-title">'
                                '📝 AI Summary'
                                '</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(summary)

                        with st.expander("📄 Show Full Transcript"):
                            st.write(transcript)

                except TranscriptsDisabled:
                    st.error(
                        "❌ Transcripts are disabled for this video."
                    )

                except NoTranscriptFound:
                    st.error(
                        "❌ No transcript was found for this video."
                    )

                except Exception as e:
                    error = str(e)

                    if "Could not retrieve" in error:
                        st.error(
                            "❌ YouTube did not provide an accessible transcript."
                        )
                    else:
                        st.error(
                            f"❌ Something went wrong: {error}"
                        )


# =========================================================
# TIKTOK
# =========================================================

with tiktok_tab:
    st.markdown("## TikTok Video")

    tiktok_url = st.text_input(
        "TikTok Video URL",
        placeholder="https://www.tiktok.com/@username/video/...",
        key="tiktok_url",
    )

    col1, col2 = st.columns(2)

    with col1:
        tiktok_language = st.selectbox(
            "Output Language",
            [
                "Auto",
                "English",
                "Hindi",
                "Spanish",
                "French",
                "German",
            ],
            key="tiktok_language",
        )

    with col2:
        tiktok_style = st.selectbox(
            "Summary Template",
            [
                "Concise Summary",
                "Key Takeaways",
                "Detailed Breakdown",
                "Study Notes",
            ],
            key="tiktok_style",
        )

    st.write("")

    generate_tiktok = st.button(
        "✨ Generate TikTok Summary",
        type="primary",
        key="tiktok_generate",
    )

    if generate_tiktok:
        if not GROQ_API_KEY:
            st.error("❌ GROQ_API_KEY is not configured.")

        elif not tiktok_url:
            st.warning("Please paste a TikTok video URL first.")

        elif not is_social_url(tiktok_url, "TikTok"):
            st.error("❌ Please enter a valid TikTok URL.")

        else:
            temp_file = None

            try:
                with st.spinner("⬇️ Getting TikTok audio..."):
                    temp_file = download_social_media(tiktok_url)

                with st.spinner("🎧 Transcribing TikTok..."):
                    transcript = transcribe_social_media(
                        temp_file,
                        tiktok_language,
                    )

                if not transcript.strip():
                    st.error("❌ No speech was detected in this TikTok.")

                else:
                    with st.spinner("🤖 AI is generating your summary..."):
                        summary = generate_summary(
                            transcript,
                            tiktok_style,
                            tiktok_language,
                            "TikTok video",
                        )

                    show_social_result(
                        temp_file,
                        transcript,
                        summary,
                    )

            except Exception as e:
                st.error(
                    "❌ TikTok could not be processed."
                )
                st.info(
                    "Make sure the TikTok is public and accessible. "
                    "Private, deleted, region-restricted or login-required "
                    "videos may not work."
                )
                st.caption(f"Technical detail: {e}")

            finally:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        parent = os.path.dirname(temp_file)
                        if os.path.isdir(parent) and not os.listdir(parent):
                            os.rmdir(parent)
                    except Exception:
                        pass


# =========================================================
# INSTAGRAM
# =========================================================

with instagram_tab:
    st.markdown("## Instagram Video")

    instagram_url = st.text_input(
        "Instagram Video URL",
        placeholder="https://www.instagram.com/reel/...",
        key="instagram_url",
    )

    col1, col2 = st.columns(2)

    with col1:
        instagram_language = st.selectbox(
            "Output Language",
            [
                "Auto",
                "English",
                "Hindi",
                "Spanish",
                "French",
                "German",
            ],
            key="instagram_language",
        )

    with col2:
        instagram_style = st.selectbox(
            "Summary Template",
            [
                "Concise Summary",
                "Key Takeaways",
                "Detailed Breakdown",
                "Study Notes",
            ],
            key="instagram_style",
        )

    st.write("")

    generate_instagram = st.button(
        "✨ Generate Instagram Summary",
        type="primary",
        key="instagram_generate",
    )

    if generate_instagram:
        if not GROQ_API_KEY:
            st.error("❌ GROQ_API_KEY is not configured.")

        elif not instagram_url:
            st.warning("Please paste an Instagram Reel/Video URL first.")

        elif not is_social_url(instagram_url, "Instagram"):
            st.error("❌ Please enter a valid Instagram URL.")

        else:
            temp_file = None

            try:
                with st.spinner("⬇️ Getting Instagram audio..."):
                    temp_file = download_social_media(instagram_url)

                with st.spinner("🎧 Transcribing Instagram video..."):
                    transcript = transcribe_social_media(
                        temp_file,
                        instagram_language,
                    )

                if not transcript.strip():
                    st.error(
                        "❌ No speech was detected in this Instagram video."
                    )

                else:
                    with st.spinner("🤖 AI is generating your summary..."):
                        summary = generate_summary(
                            transcript,
                            instagram_style,
                            instagram_language,
                            "Instagram video",
                        )

                    show_social_result(
                        temp_file,
                        transcript,
                        summary,
                    )

            except Exception as e:
                st.error(
                    "❌ Instagram video could not be processed."
                )
                st.info(
                    "Make sure the Reel/video is public and accessible. "
                    "Private, deleted, region-restricted or login-required "
                    "videos may not work."
                )
                st.caption(f"Technical detail: {e}")

            finally:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        parent = os.path.dirname(temp_file)
                        if os.path.isdir(parent) and not os.listdir(parent):
                            os.rmdir(parent)
                    except Exception:
                        pass


# =========================================================
# FILES
# =========================================================

with files_tab:
    st.markdown("## 📁 File Summarizer")

    uploaded_file = st.file_uploader(
        "Upload a PDF or Word document",
        type=["pdf", "docx"],
        key="document_upload",
    )

    col1, col2 = st.columns(2)

    with col1:
        file_language = st.selectbox(
            "Output Language",
            [
                "Auto",
                "English",
                "Hindi",
                "Spanish",
                "French",
                "German",
            ],
            key="file_language",
        )

    with col2:
        file_style = st.selectbox(
            "Summary Template",
            [
                "Concise Summary",
                "Key Takeaways",
                "Detailed Breakdown",
                "Study Notes",
            ],
            key="file_style",
        )

    st.write("")

    generate_file = st.button(
        "✨ Generate File Summary",
        type="primary",
        key="file_generate",
    )

    if generate_file:
        if not GROQ_API_KEY:
            st.error("❌ GROQ_API_KEY is not configured.")

        elif not uploaded_file:
            st.warning("Please upload a PDF or DOCX file first.")

        else:
            try:
                with st.spinner("📖 Reading your file..."):
                    if uploaded_file.name.lower().endswith(".pdf"):
                        text = extract_pdf_text(uploaded_file)
                    else:
                        text = extract_docx_text(uploaded_file)

                if not text.strip():
                    st.error(
                        "❌ No readable text was found in this file."
                    )

                else:
                    with st.spinner(
                        "🤖 AI is generating your summary..."
                    ):
                        summary = generate_summary(
                            text,
                            file_style,
                            file_language,
                            "document",
                        )

                    st.success("✓ Summary generated successfully!")

                    st.markdown(
                        '<div class="summary-title">'
                        '📝 AI Summary'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown(summary)

                    with st.expander("📄 Show Extracted Text"):
                        st.write(text)

            except Exception as e:
                st.error(f"❌ Could not process the file: {e}")


# =========================================================
# FEATURES
# =========================================================

st.markdown("---")

st.markdown("### ✨ Why use AI Video Summarizer?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
        <h3>⚡ Fast</h3>
        <p>
        Turn videos and documents into useful summaries quickly.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
        <h3>🧠 AI Powered</h3>
        <p>
        Get concise summaries, key takeaways and study notes automatically.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
        <h3>🔒 Secure</h3>
        <p>
        Visitors do not need to enter an API key.
        Your Groq key stays in Streamlit Secrets.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )