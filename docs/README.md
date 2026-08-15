# Project docs

## Product flow

```text
YouTube URL
    ↓
Extract video ID
    ↓
Fetch available transcript
    ↓
Choose summary style
    ↓
LLM summarizes transcript
    ↓
Structured takeaways
    ↓
Read / copy / explore
```

## Design goals

- Keep the workflow simple: paste → choose → summarize.
- Ground the generated summary in the available transcript.
- Make the output useful for both quick scanning and deeper review.
- Keep the project easy to run with free-tier tooling.

## Future UX ideas

- Timestamp-linked takeaways
- Transcript search
- Saved summaries
- Multi-language output
- Shareable summary links
