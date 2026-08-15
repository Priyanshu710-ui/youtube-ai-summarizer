# 🎬 YouTube AI Summarizer — Portfolio Showcase

## The problem
Long-form videos are useful, but not every viewer has time to watch an entire lecture, tutorial, interview, or explainer.

## The product
Paste a YouTube URL and turn an available transcript into a focused summary. Choose between a concise overview, bullet-point takeaways, or a detailed breakdown.

## The engineering
```text
YouTube URL
    ↓
Video ID extraction
    ↓
youtube-transcript-api
    ↓
Transcript text
    ↓
Prompt + summary mode
    ↓
Groq / Llama
    ↓
Structured summary
```

## What makes it useful
- ⚡ Faster information triage
- 🎯 Multiple summary depths for different use cases
- 📜 Full transcript remains available for verification
- 🧠 LLM output is grounded in the fetched transcript
- 🆓 Designed around free-tier tooling

## Strong portfolio talking points
- API integration and error handling
- Prompt design and output control
- Streamlit UI state management
- Transcript extraction and preprocessing
- LLM-powered text transformation
- Environment-variable based secret management

## Next-level ideas
1. Timestamp-linked summaries
2. Multi-language translation + summarization
3. Transcript caching
4. Chapter detection
5. Export to Markdown/PDF
6. Ask questions about the transcript
