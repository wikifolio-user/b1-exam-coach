# B1 Exam Coach — Phase 2

A focused Streamlit learning app for Cambridge B1 Preliminary preparation.

The goal is not to be a generic language app. It tracks mistakes, weak topics, Writing practice and daily study recommendations so the learner can train specifically for B1 Preliminary.

## Included now

- Dashboard with current progress and today's mission
- Personal adaptive Study Plan
- Reading Trainer for Parts 1–6
- Grammar Trainer with adaptive weak-topic selection
- Vocabulary trainer with simple spaced repetition
- Writing Trainer for Email, Article and Story
- Writing feedback using Cambridge-oriented training criteria:
  - Content
  - Communicative Achievement
  - Organisation
  - Language
- Offline Writing evaluator that works without an API key
- Optional OpenAI Writing feedback when `OPENAI_API_KEY` is configured
- My Mistakes notebook with targeted Reading/Grammar practice
- Progress charts
- SQLite by default
- Optional `DATABASE_URL` support for hosted PostgreSQL
- GitHub Actions test workflow
- Original sample exercises rather than copied Cambridge exam items

Writing scores in this app are training estimates and are not official Cambridge scores.

---

# 1. Download and extract

Extract the project and open a terminal inside the `b1-exam-coach` folder.

# 2. Create a Python environment

Recommended: Python 3.12.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

# 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

# 4. Run tests

```bash
pytest -q
```

You should see all tests pass.

# 5. Start the app locally

```bash
streamlit run app.py
```

Open the local address shown by Streamlit in your browser.

The SQLite database is created automatically as `b1_exam_coach.db`.

# 6. First test inside the app

Use this order:

1. Open **Settings** and enter your name and optional exam date.
2. Complete 3–5 **Grammar** questions.
3. Complete Reading questions from at least two different parts.
4. Open **My Mistakes** and start a targeted weak-topic drill.
5. Open **Writing**, choose an Email task and write about 100 words.
6. Open **Study Plan** and check whether the recommendations now react to your results.
7. Open **Progress** and verify that your attempts and Writing scores appear.

# 7. Optional AI Writing feedback

The app works without AI. Start without an API key first.

For local development, copy `.env.example` to `.env` and add your key:

```env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-5.6-luna
```

Never commit `.env` or `.streamlit/secrets.toml` to GitHub.

The app automatically falls back to the offline evaluator if an AI request fails.

# 8. Put the project on GitHub

Create a new empty GitHub repository, for example:

`b1-exam-coach`

Do not let GitHub create another README if you want the cleanest first push.

Then run from the project folder:

```bash
git init
git add .
git commit -m "Build B1 Exam Coach Phase 2"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/b1-exam-coach.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

# 9. Deploy on Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Click **Create app**.
3. Select your repository.
4. Branch: `main`.
5. Main file / entrypoint: `app.py`.
6. In Advanced settings choose a supported Python version such as Python 3.12.
7. If you use AI feedback, add the secrets there rather than committing them to GitHub.
8. Deploy.

Example Streamlit secrets:

```toml
OPENAI_API_KEY = "your-key-here"
OPENAI_MODEL = "gpt-5.6-luna"
```

## Important: progress persistence on Streamlit Community Cloud

The default SQLite database is excellent for local development, but Community Cloud does not guarantee permanent local file storage. For serious daily use on a cloud deployment, configure a persistent PostgreSQL database and add its connection string as:

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"
```

If `DATABASE_URL` is absent, the app automatically uses SQLite.

# Project structure

```text
b1-exam-coach/
├── app.py
├── components/
├── database/
│   ├── db.py
│   ├── models.py
│   ├── repositories.py
│   └── seed.py
├── pages/
│   ├── dashboard.py
│   ├── study_plan.py
│   ├── reading.py
│   ├── writing.py
│   ├── grammar.py
│   ├── vocabulary.py
│   ├── mistakes.py
│   ├── progress.py
│   └── settings.py
├── services/
│   ├── adaptive_service.py
│   ├── ai_service.py
│   ├── mistake_service.py
│   ├── progress_service.py
│   ├── scoring_service.py
│   ├── study_plan_service.py
│   ├── vocab_service.py
│   └── writing_service.py
├── tests/
├── .github/workflows/tests.yml
├── .streamlit/secrets.toml.example
├── .env.example
├── requirements.txt
└── README.md
```

# How the adaptive logic works

Reading and Grammar topics start with a neutral mastery value. Correct answers increase mastery and wrong answers decrease it. The question selector gives weaker topics more weight, so weaknesses return more often.

`My Mistakes` groups wrong answers by skill and topic and lets the learner start targeted fresh practice for that area.

# Writing feedback

The offline evaluator checks observable signals such as approximate length, structure, linking words and B1-like language features. It cannot reliably judge semantic task completion, so its result is explicitly labelled as a heuristic.

When AI feedback is configured, the app can judge the actual prompt and response more deeply and returns concrete strengths, improvements, missing points, useful phrases, exam tips and an optional improved B1-level version.

# Run tests

```bash
pytest -q
```

# Next product phase

Phase 3 should add Listening, Speaking/audio and stronger exam simulation. Phase 4 should add full timed Mock Exams, readiness scoring and more detailed analytics.
