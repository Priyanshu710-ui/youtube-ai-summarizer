<div align="center">

# 🎬 YouTube AI Summarizer

### Turn any YouTube video into a clear, useful summary in seconds.

<p>
  <a href="https://github.com/Priyanshu710-ui/youtube-ai-summarizer"><strong>⭐ GitHub Repo</strong></a>
  ·
  <a href="#-how-it-works">How it works</a>
  ·
  <a href="#-run-locally">Run locally</a>
  ·
  <a href="#-roadmap">Roadmap</a>
</p>

<p>
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge" alt="Streamlit" />
  <img src="https://img.shields.io/badge/LLM-Groq%20%2B%20Llama%203.1-111827?style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/Transcript-YouTube-FF0000?style=for-the-badge" alt="YouTube" />
  <img src="https://img.shields.io/github/license/Priyanshu710-ui/youtube-ai-summarizer?style=for-the-badge" alt="License" />
</p>

<p><em>Watch less. Learn faster.</em></p>

</div>

---

## 🧠 What is this?

**YouTube AI Summarizer** takes a YouTube URL, extracts the video's available transcript, and turns it into a structured summary using an LLM.

No video download. No manual note-taking. Just paste the link, choose the level of detail, and get the useful parts.

> **Core idea:** transcript retrieval + grounded LLM summarization in a lightweight app.

---

## ✨ What you can do

| | Capability | Result |
|---|---|---|
| 🔗 | **Paste a YouTube URL** | Automatically extracts the video ID |
| 📝 | **Transcript extraction** | Pulls available captions/transcript text |
| 🧠 | **AI summarization** | Generates a summary grounded in the transcript |
| 🎚️ | **Multiple summary styles** | Concise, bullet-point, or detailed output |
| 📖 | **Raw transcript view** | Inspect the source text alongside the summary |
| ⚡ | **Fast interaction** | Lightweight Streamlit interface |
| 💸 | **Free-tier friendly** | Designed around free API infrastructure |

---

## 🖥️ Product Flow

```text
┌───────────────────────────┐
│       YouTube URL         │
│  youtube.com/watch?v=...  │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│      Video ID Parser      │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│   Transcript Extraction   │
│ youtube-transcript-api    │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│      Summary Strategy      │
│ concise / bullets / detail │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│       Groq + Llama         │
│   transcript-grounded LLM  │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│      Useful Summary        │
│ + Raw Transcript View      │
└───────────────────────────┘
```

---

## 🔄 How It Works

1. **Parse** — Extract the YouTube video ID from the supplied URL.
2. **Fetch** — Retrieve the video's available transcript/captions.
3. **Prepare** — Combine the transcript with the selected summary style.
4. **Generate** — Send the transcript to Groq's LLM endpoint with instructions to stay grounded in the source text.
5. **Present** — Render the summary and raw transcript in Streamlit.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | **Streamlit** |
| Transcript extraction | **youtube-transcript-api** |
| LLM | **Groq API · Llama 3.1 8B** |
| Language | **Python** |

---

## 📁 Project Structure

```text
youtube-ai-summarizer/
│
├── app.py                # Streamlit application
├── app_backup.py         # Backup implementation
├── index.html            # Supporting web page / metadata
├── requirements.txt      # Dependencies
├── .env.example          # Environment variable template
├── .streamlit/           # Streamlit configuration
└── README.md
```

---

## 🔐 Environment Setup

Keep credentials local and never commit real API keys.

Create your environment from the template and add your Groq key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The existing project is designed around Groq's free API tier.

---

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Priyanshu710-ui/youtube-ai-summarizer.git
cd youtube-ai-summarizer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run app.py
```

Open the local Streamlit URL, paste a YouTube link, choose your summary style, and run the summarizer.

---

## 🧪 Example Use Cases

- 🎓 Turn a long lecture into revision notes.
- 💼 Extract the key ideas from a business talk.
- 💻 Summarize programming tutorials before coding.
- 📚 Convert educational videos into bullet-point notes.
- 🎙️ Quickly scan interviews and podcasts with available captions.

---

## ⚠️ Limitations

- The video must have an accessible transcript/captions.
- Very long transcripts may be trimmed to stay within the model context budget.
- Summary quality depends on the quality and completeness of the source transcript.

---

## 🗺️ Roadmap

- [x] YouTube URL parsing
- [x] Transcript extraction
- [x] Transcript-grounded AI summaries
- [x] Multiple summary styles
- [x] Raw transcript view
- [ ] Timestamped summaries with clickable jumps
- [ ] Multi-language transcript support
- [ ] Transcript caching
- [ ] Better long-video chunking and map-reduce summarization
- [ ] Export summaries to PDF / Markdown
- [ ] Dockerized deployment

---

## 🎯 Why this is a good portfolio project

This project is intentionally small, but it demonstrates a useful end-to-end AI workflow:

- **External data retrieval** from YouTube transcripts
- **Prompt-controlled LLM generation**
- **Grounded summarization** from source text
- **User-selectable generation modes**
- **A usable interactive frontend**
- **API-key-aware application design**

It is a compact example of taking an AI capability and turning it into a real user-facing tool.

---

## 👨‍💻 Built By

**Priyanshu Sharma**

Built with Python, Streamlit, YouTube transcript extraction, Groq, and Llama.

<div align="center">

### ⭐ Star the repo if you found it useful.

</div>

---

## 📄 License

MIT — feel free to use this as a learning reference or starting point.
