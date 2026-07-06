# AP Socratic

A Socratic-method study guide for AP exam prep, powered by the Claude API.
Instead of giving answers, it asks guiding questions grounded in College
Board's official course content, pushing the student to construct and
defend their own interpretation rather than being told one.

Currently covers AP English Literature and Composition; the content schema
is subject-agnostic, so more AP courses can be added as new
`content/<subject_id>/units.json` files.

## How it works

- Each unit's essential questions, skills, and example texts come from the
  AP Course and Exam Description (CED), paraphrased into the app's own
  words rather than copied verbatim (see `content/README.md` for sourcing).
- The tutor opens each unit with a concrete question tied to that unit's
  actual skills — not a generic "what do you know" prompt.
- It never asserts an exact quote or line from memory. When a claim depends
  on specific wording, it asks the student to paste the passage instead —
  which is itself the AP skill being practiced (citing textual evidence).
- Conversations persist per subject/unit in SQLite and resume where you
  left off, independent of cookies or device.

## Setup

```
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
python3 app.py
```

Visit `http://127.0.0.1:5000`.

## Adding content

Content lives in `content/<subject_id>/units.json`. See `content/README.md`
for the schema and for guidance on sourcing from College Board's publicly
released materials without scraping their site.

## Architecture

- `app.py` — Flask routes
- `llm_client.py` — Claude API integration and the Socratic system prompt
- `db.py` — SQLite-backed conversation persistence
- `content_loader.py` — loads subject/unit content from JSON

## Deployment

Pushes to `main` auto-deploy via GitHub Actions
(`.github/workflows/deploy.yml`). The deploy key on the target server is
restricted via a forced command to only run the redeploy script — it can't
be used for anything else even if the secret were ever exposed.
