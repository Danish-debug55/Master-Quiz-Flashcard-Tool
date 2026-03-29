# Mastery Flashcards Airtable Ready

A local FastAPI flashcard app for Sigma Labs style mastery quiz revision.

## Features
- Load demo mastery quiz data
- Import quiz data from Airtable using env variables
- Convert mastery quiz questions into flashcards
- Topic and subtopic filtering
- Again, Hard, Good, Easy spaced repetition buttons
- Explanation, wrong options notes, and example block
- Dashboard and search
- Keyboard shortcuts

## Setup

Create a `.env` file in the project root using `.env.example` as a guide.

Example:

AIRTABLE_PAT=your_real_pat_here
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=Mastery Quiz Questions
AIRTABLE_VIEW_NAME=Grid view

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

## Main endpoints
- `POST /api/load-demo-data`
- `GET /api/next-card?topic=All`
- `POST /api/review`
- `GET /api/dashboard`
- `GET /api/search`
- `GET /api/airtable/status`
- `POST /api/airtable/import`

## How Airtable import works
The app reads these env vars:
- `AIRTABLE_PAT`
- `AIRTABLE_BASE_ID`
- `AIRTABLE_TABLE_NAME`
- `AIRTABLE_VIEW_NAME`

It fetches records from Airtable, converts them into quiz questions, saves them to `data/quiz_questions.json`, then rebuilds `data/flashcards.json` and resets `data/progress.json`.

## Important note
You will likely need to adjust `app/importer.py` once your team confirms the exact Airtable field names.
