# 🎬 AI-Powered YouTube Video Summarizer

Paste a YouTube link, get an instant summary pulled straight from the video's transcript — no watching required.

<!-- Add a demo GIF/screenshot here once deployed. -->
<!-- ![demo](assets/demo.gif) -->

## 🚀 Live Demo

[Add your deployed Streamlit link here once you deploy]

## ✨ Features

- Paste any YouTube URL and get a summary in seconds
- Choose your summary style: concise summary, bullet-point takeaways, or a detailed section-by-section breakdown
- View the full raw transcript alongside the summary
- Runs on free-tier infrastructure end-to-end — no paid API keys required

## 🧠 How It Works

1. **Parse** — The video ID is extracted from the pasted URL
2. **Fetch** — The video's transcript/captions are pulled using `youtube-transcript-api` (no downloading or scraping needed)
3. **Prompt** — The transcript plus your chosen summary style is sent to an LLM
4. **Generate** — The LLM (via Groq's free API) returns a summary grounded only in the transcript

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Transcript extraction | youtube-transcript-api |
| LLM | Groq API (Llama 3.1 8B, free tier) |

## 📦 Setup & Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/youtube-summarizer.git
cd youtube-summarizer

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Then, in the sidebar, paste a free Groq API key (get one at [console.groq.com/keys](https://console.groq.com/keys)), paste a YouTube link, and click Summarize.

## 📁 Project Structure

```
youtube-summarizer/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── .env.example         # Template for environment variables
└── README.md
```

## ⚠️ Limitations

- Only works on videos that have captions/transcripts available (auto-generated or manual)
- Very long videos are trimmed to stay within the LLM's context budget

## 🗺️ Roadmap / What I'd Improve Next

- [ ] Support timestamped summaries (jump to the relevant part of the video)
- [ ] Add multi-language transcript support
- [ ] Cache transcripts to avoid re-fetching on repeated runs
- [ ] Deploy with Docker for easier hosting

## 📄 License

MIT — feel free to use this as a learning reference or starting point.
