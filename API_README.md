# API Guide

How the Career Skill-Gap Finder talks to the LLM API.

An API works like this: **request in, JSON out.**

## Overview

| Item | Value |
|------|-------|
| Provider | Google Gemini API (free tier, via Google AI Studio) |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/<MODEL>:generateContent` |
| Method | `POST` |
| Library | `requests` |
| Auth | API key from `.env`, sent in the `x-goog-api-key` header |
| Model | Copy the exact current model name from Google's docs (example: `gemini-2.5-flash-lite`) |

> Check Google's Gemini API docs for the current endpoint, model names and free-tier limits. They change often.

## Flow: how the app connects to the API

```
.env file  ->  load key  ->  questionnaire answers  ->  build prompt
   ->  POST request to Gemini  ->  JSON response  ->  read the text
   ->  show 3 career suggestions
```

1. **Load the key** from `.env` with `python-dotenv`.
2. **Collect answers** from the questionnaire into a Python dictionary (kept in memory).
3. **Build a prompt** that includes the answers and asks for exactly 3 career suggestions.
4. **Send the request** with `requests.post(...)`.
5. **Check the status code.** Anything other than 200 is handled as an error (see below).
6. **Parse the JSON** and pull out the text.
7. **Show the 3 suggestions** to the user.

No database is needed in Phase 1. Answers live in memory while the program runs.

## Setup

1. Get a free key from Google AI Studio (aistudio.google.com/apikey).
2. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Load it in Python:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()
   api_key = os.getenv("GEMINI_API_KEY")
   ```
4. Make sure `.env` is listed in `.gitignore`. **Never commit your key.**

## Request

```python
import requests

url = "https://generativelanguage.googleapis.com/v1beta/models/<MODEL>:generateContent"
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key,
}
body = {
    "contents": [
        {"parts": [{"text": prompt}]}
    ]
}
response = requests.post(url, headers=headers, json=body, timeout=30)
```

`prompt` is the text built from the questionnaire answers.

## Prompt

The prompt asks the model for exactly 3 career suggestions with a short reason each.

--Final prompt would be paster over here--

## Response

The API returns JSON. The generated text is inside the `candidates` list.

```python
data = response.json()
text = data["candidates"][0]["content"]["parts"][0]["text"]
```

_Verify this shape against Google's docs and one real response before relying on it._

## Free tier limits

- The free tier is rate limited (requests per minute and per day vary by model).
- Check the current limits table in Google's docs.
- Free tier access depends on your country being eligible.

## Error handling

| Problem | Likely cause | What the app does |
|---------|--------------|-------------------|
| 400 | Bad request body or model name | Show a friendly error, check the request |
| 401 / 403 | Wrong, missing or restricted API key | Show a key error message |
| 429 | Rate limit hit | Tell the user to wait and retry |
| 5xx | Provider problem | Tell the user to try later |
| Timeout | Slow or no connection | Stop after the timeout, show message |
| Missing `candidates` in JSON | Blocked or empty response | Show a friendly error, do not crash |

## Security notes

- Key lives only in `.env`, never in code or commits.
- If a key is ever pushed to GitHub, delete it in Google AI Studio and create a new one.
- Free-tier data terms: read Google's terms. Questionnaire answers are sent to Google's API.

## Baseline note

The output of this API call is the **Phase 1 baseline**. In Phase 2, my own matching engine will be compared against it.
