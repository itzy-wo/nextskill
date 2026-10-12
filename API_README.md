# API Guide

How NEXT-SKILL turns six chat answers into 3 career suggestions.

An API works like this: **request in, JSON out.** This project has two of them. The chat page calls our own API, and our API calls Google Gemini.

## Flow

```
Chat page (chat.js)
   |  POST /api/suggest  (6 answers as JSON)
   v
api.py (FastAPI)  ->  core.py: get_suggestions()
   |  build prompt -> call Gemini (JSON mode) -> parse and check the reply
   v
Google Gemini API
   |
   v
3 suggestions back to the chat page
```

No database is used. Answers live in the browser and in memory only for the length of a request.

## Files

| File | Job |
|------|-----|
| `api.py` | The web API: `POST /api/suggest`, and it serves the `static/` folder |
| `core.py` | The logic: build the prompt, call Gemini, check the reply |
| `test_gemini.py` | First test script that sends one prompt to Gemini |
| `test_terminal.py` | Runs the whole flow with sample answers in the terminal |

## Setup

1. Get a free key from Google AI Studio (aistudio.google.com/apikey).
2. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   ```
3. Install the packages:
   ```
   pip install -r requirements.txt
   ```
4. Start the server:
   ```
   python -m uvicorn api:app --port 8000
   ```
5. Open `http://localhost:8000`.

`.env` is listed in `.gitignore`. **Never commit your key.**

> Model names change. If you get a 404 from Gemini, copy the current model name from Google's docs into `GEMINI_MODEL`.

## Our endpoint: `POST /api/suggest`

### Request

```json
{
  "field": "BCA",
  "interest": "Data and AI",
  "enjoy": "Digging into data",
  "skills": ["Python", "SQL"],
  "level": "Can build small things",
  "goal": "An internship"
}
```

| Field | Type | Rules |
|-------|------|-------|
| `field` | text | What they study, max 100 characters |
| `interest` | text | Area they like most, max 100 characters |
| `enjoy` | text | What they enjoy doing, max 100 characters |
| `skills` | list of text | Skills they already have |
| `level` | text | Comfort with their strongest skill, max 100 characters |
| `goal` | text | What they want in the next year, max 100 characters |

### Response (200)

```json
{
  "suggestions": [
    {
      "role": "Data Analyst",
      "why": "It aligns with your BCA background and passion for digging into data using Python and SQL.",
      "learn_next": ["Pandas", "Tableau", "Statistics"]
    }
  ]
}
```

The real response holds 3 items. Each has a role, a one-sentence reason (`why`), and 2-3 skills to learn next (`learn_next`).

### Status codes

| Code | Meaning | Cause |
|------|---------|-------|
| 200 | Success | 3 suggestions returned |
| 422 | Bad input | A field is missing, too long, or the wrong type |
| 502 | Gemini problem | Missing or rejected key, rate limit, no connection, or an unreadable reply |

## How we call Gemini (inside `core.py`)

| Item | Value |
|------|-------|
| Provider | Google Gemini API (free tier, via Google AI Studio) |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/<MODEL>:generateContent` |
| Method | `POST` using the `requests` library |
| Auth | Key from `.env`, sent in the `x-goog-api-key` header |
| Model | `GEMINI_MODEL` from `.env` (default `gemini-3.5-flash-lite`) |
| Reply format | JSON mode, so Gemini answers with JSON only |

Steps inside `get_suggestions(answers)`:
1. **Build the prompt.** The six answers go into one prompt that asks for exactly 3 careers. Answers are capped at 100 characters, and the prompt tells Gemini they are data, not instructions.
2. **Call Gemini** with JSON mode on.
3. **Parse the reply.** Keep only `role`, `why` and `learn_next`, and return at most 3 items.
4. **Fail safely.** If the reply isn't valid or is empty, raise an error with a friendly message instead of crashing.

## Testing

| Test | How | Expect |
|------|-----|--------|
| Key loads | `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key found' if os.getenv('GEMINI_API_KEY') else 'Key NOT found')"` | `Key found` |
| Gemini works | `python test_gemini.py` | A short greeting |
| Full flow | `python test_terminal.py` | 3 suggestions in the terminal |
| API endpoint | Open `http://localhost:8000/docs`, try `POST /api/suggest` | Status 200 and 3 suggestions |
| Bad input | Remove a field in `/docs` and run it | Status 422 |

## Error handling

| Problem | Likely cause | What the user sees |
|---------|--------------|--------------------|
| Key missing or rejected | `.env` missing, wrong name, or revoked key | A friendly message about the key |
| 404 from Gemini | Outdated model name | Update `GEMINI_MODEL` |
| 429 | Free-tier rate limit | Ask to wait a minute |
| Timeout or no internet | Slow or no connection | Could not reach the service |
| Unreadable JSON | Unexpected Gemini output | Try again |

## Free tier notes

- The free tier is rate limited, and limits change by model.
- Free tier access depends on your country being eligible.
- Read Google's terms for free-tier data use. Questionnaire answers are sent to Google's API.

## Security notes

- The key lives only in `.env`. It never appears in code, logs or commits.
- If a key is ever exposed, delete it in Google AI Studio and create a new one.
- Typed answers are trimmed, and the prompt treats them as data, which limits prompt injection.
- AI output is shown on the page as plain text, never as HTML.

## Baseline note

The output of this API is the **Phase 1 baseline**. In Phase 2, my own matching engine will be compared against it.