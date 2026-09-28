# Review Intelligence: FMCG Consumer Sentiment Agent

A brand manager asks natural-language questions about product reviews and gets
answers grounded in real data: sentiment trends, safety/quality flags with a
severity score, summary reports, and cited example reviews.

## Architecture

```
Streamlit dashboard (src/frontend)
        |  HTTP
FastAPI backend (src/main.py)
  routers -> services -> tools / agent
        |
  AgentRuntime (LangGraph agent)  --MCP over stdio-->  MCP server (src/mcp)
                                                         |-- sentiment_trend
                                                         |-- flagged_reviews
                                                         |-- generate_summary_report
                                                         `-- search_reviews  -> ChromaDB
Data: CSV (aggregations) + ChromaDB (semantic search over review text)
```

| Folder | Purpose |
|---|---|
| `src/config` | constants, settings (paths, env), logging setup |
| `src/routers`, `services`, `schemas`, `exceptions` | FastAPI layers; domain errors are mapped to HTTP codes in `main.py` |
| `src/agents` | LangGraph agent, roles, prompts, grounding checks, audit log |
| `src/mcp` | MCP server, tool registry, the three core tools |
| `src/rag` | retriever (ChromaDB), guardrails, answer generator |
| `src/repositories` | review data loading and filtering |
| `src/data_prep` | labeling rules, safety flags, PII scrubbing (batch scripts) |
| `src/evaluation` | evaluation question set and runner |
| `src/frontend` | Streamlit app, API client, chat history store |
| `tests` | pytest suite |
| `archive` | experiments run before the final design (embedding benchmarks, gold-set labeling evaluation, earlier prototypes). Not part of the live app. |

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then fill in GROQ_API_KEY
```

Data files are not in the repo (see `.gitignore`). Place them as:
`data/raw/raw_reviews.csv`, `data/labeled/reviews_scrubbed.csv`,
`data/vectorstore/chroma_db/`.

## Run

Terminal 1 (backend; the agent warms up on startup, about a minute):
```powershell
uvicorn src.main:app --reload
```
Terminal 2 (dashboard):
```powershell
streamlit run src/frontend/app.py
```
API docs: http://127.0.0.1:8000/docs

## Tests and evaluation

```powershell
pytest tests/ -v
python -m src.evaluation.run_evaluation --frameworks langgraph --models groq:openai/gpt-oss-120b
```
Evaluation writes `data/evaluation/results.csv` and `summary.csv`.

## Sample report

```powershell
python -m src.mcp.tools.summary_report --days 30 --save
```
Saved to `reports/`. The dataset ends on 2023-03-21, so "last week" means the
7 days before that date; the 7-day sample report has only 8 reviews.

## Guardrails

- Input checks before any model call: too broad (asks to clarify), out of scope
  (policies/returns), prompt-injection attempts (blocked), identity questions (refused).
- Review text is treated as data, never as instructions.
- After each answer: citations, quoted text and numbers are checked against tool output.

## Audit trail

Every question and answer is appended to `logs/audit_log.jsonl` (session, role,
question, answer, tools called, tokens, latency, cost). Brand managers see the
full log; the support team sees its own records. Data-prep runs are logged in
`logs/run_log.csv`. Reviewer identity handling: see `docs/PII_HANDLING.md`.

## Regenerating data (only if needed)

1. Labeled CSV with rule-based labels: `python -m src.data_prep.apply_label_rules`
2. PII masking: `python -m src.data_prep.scrub_pii`
3. Vector store: `archive/experiments/build_production_vectorstore.py`
   (historical script, may need path adjustments)
4. Sync flags into the vector store: `python -m src.data_prep.recompute_safety_flags`

## Known limits

- The free-tier Groq limit (tokens per minute) can cause slow answers or 429/413
  errors. The agent starts a fresh context window every 4 questions to limit prompt growth.
- Sentiment follows the star rating; aspects and safety flags are keyword rules.
- Chat history for the dashboard is stored in a local JSON file.


