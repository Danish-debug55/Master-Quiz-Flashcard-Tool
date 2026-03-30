# C22 Mastery Quiz Flashcard Tool

A FastAPI flashcard app for Sigma Labs mastery quiz revision. Flashcard data is baked in as static JSON — no external API required at runtime. Per-user progress is tracked via a browser UUID stored in `localStorage`.

## Features

- Spaced repetition scheduling (Again / Hard / Good / Easy)
- Topic filtering and keyword search
- Dashboard with stats, weakest topics, and hard cards
- Per-user progress — each browser gets its own independent session
- Fully static data — no Airtable connection needed at runtime

## Project structure

```
app/
  main.py        # FastAPI routes
  service.py     # Business logic
  models.py      # Pydantic models
  scheduler.py   # Spaced repetition logic
data/
  flashcards.json      # Static flashcard data (baked into Docker image)
  quiz_questions.json  # Raw question data
  progress/            # Per-user progress files (runtime, gitignored)
static/
  index.html
  app.js
  styles.css
terraform/       # AWS infrastructure (ECS Fargate + ALB + ECR)
deploy.sh        # Build, push to ECR, redeploy ECS
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/next-card?topic=All` | Get next due card |
| POST | `/api/review` | Submit card rating |
| GET | `/api/dashboard` | User stats and progress |
| GET | `/api/search?q=keyword` | Search flashcards |

All progress endpoints require an `X-User-Id` header (UUID). The frontend handles this automatically via `localStorage`.

## Deploy to AWS

```bash
# 1. Fill in your VPC and subnet IDs in terraform/terraform.tfvars
# 2. Apply infrastructure
cd terraform && terraform init && terraform apply

# 3. Build, push image to ECR and redeploy ECS
cd .. && ./deploy.sh
```

See `terraform/terraform.tfvars` for all configurable values.
