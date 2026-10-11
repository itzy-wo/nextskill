# UI Guide

How the Career Skill-Gap Finder looks and behaves for the user.

> **Plan:** the web UI starts in Phase 1, built with Streamlit.
> **Terminal:** used only for testing the logic while building.

## Why both

The core logic (questionnaire, prompt, API call, parsing) lives in plain Python functions. The terminal and the web UI both call the same functions, so nothing is written twice.

```
questionnaire answers -> build_prompt() -> call_gemini() -> parse_suggestions()
        ^                                                          |
   terminal (testing) or Streamlit UI (real use)  <----------------+
```

## User flow

1. Open the app.
2. Answer the skills questionnaire.
3. Click a submit button.
4. Wait while the app calls the Gemini API.
5. Read your 3 career suggestions.

## Questionnaire

Short and simple. Each question asks about a skill area (for example: Python, SQL, Git, statistics, communication).

| # | Question | Input type |
|---|----------|------------|
| 1 | TBD: e.g. "How comfortable are you with Python?" | Slider 1-5 |
| 2 | TBD | TBD |
| 3 | TBD | TBD |

Real questions would be filled later on.

## Screens

| Screen | What it shows |
|--------|---------------|
| Questionnaire | The questions and a submit button |
| Loading | A short "Thinking..." message |
| Results | 3 career suggestions with a short reason each |

Screenshots would be added here when the UI is completer.

## Terminal testing

Used to check the logic before the UI exists.

```
Q1. How comfortable are you with Python? (1-5): 3
...
Your top 3 career suggestions:
1. <role>: <short reason>
2. <role>: <short reason>
3. <role>: <short reason>
```

Real output would be displayed instead of "<role>:<short reason>".

## Input rules

- Answers must be in the allowed range.
- Empty answers are not accepted.

## Messages the user may see

| Situation | Message shown |
|-----------|---------------|
| Missing API key | "API key not found. Check your .env file." |
| No internet / API down | "Could not reach the API. Try again later." |
| Rate limit hit | "Too many requests. Please wait a minute and try again." |
| Unexpected API response | "Got a response I could not read. Try again." |

Every results screen also shows: **"This is a suggestion, not a verdict."**

## Planned for later phases

- Phase 2: show matched skills vs. missing skills
- Phase 3: feedback form, deployment, tests for the UI flow
