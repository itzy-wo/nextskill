# Career Skill-Gap Finder

Tell it what you know. It tells you what to learn next.

> **Status:** Phase 1 of 3 (in progress). Small and working beats big and unfinished.

## What it does

You answer a short skills questionnaire. The app sends your answers to an LLM API and returns **3 career suggestions**. In Phase 1 these suggestions are my **baseline**, which later phases (data + ML matching) must beat, measured honestly.

> This is a suggestion, not a verdict.

## Phase 1 scope

- [ ] Short skills questionnaire (Streamlit UI, terminal for testing)
- [ ] First API call to an LLM
- [ ] 3 career suggestions (baseline)
- [ ] API key kept safe in a `.env` file

**Done when:** it runs end to end and I can explain every single line.

## Tech stack

Python, `requests`, `python-dotenv`, JSON, Streamlit, Google Gemini API (free tier), Git + GitHub

## Setup

1. Clone the repo
   ```bash
   git clone https://github.com/itzy-wo/nextskill.git
   cd nextskill
   ```
2. Install dependencies
   ```bash
   pip install requests python-dotenv
   ```
3. Create a `.env` file in the project root and add your key (never commit this file)
   ```
   GEMINI_API_KEY=your_key_here
   ```
4. Run it
   ```bash
   python main.py
   ```

## Roadmap

| Phase | Focus | Outcome |
|-------|-------|---------|
| 1. Foundations | Questionnaire + first LLM API call | Baseline of 3 career suggestions |
| 2. Data + ML core | Job-posting dataset, skill extraction, matching engine | Measured results vs. the Phase 1 baseline |
| 3. Product + users | Streamlit app, pytest tests, feedback form | Real people used it and I logged what they said |

## Limits and privacy

- Suggestions come from an LLM and can be wrong.
- Your answers are sent to the LLM provider's API.
- Never share or commit your API key.

## License

TBD
