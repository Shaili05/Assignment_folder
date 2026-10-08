Review Intelligence: FMCG Consumer Sentiment Agent
A brand manager asks natural-language questions about product reviews and gets answers grounded in real data: sentiment trends, safety and quality flags with a severity score, brand-health summary reports, and cited example reviews.
Every answer is checked against the data it was built from. Review text is treated as data to reason about, never as instructions to follow.
What it does
Capability
Where
Labeled review corpus (sentiment, aspect, safety flags with severity score)
src/data_prep
Retrieval over review text with citations (ChromaDB)
src/rag/retriever.py
Four tools exposed over MCP: sentiment trend, flagged reviews, summary report, review search
src/mcp
One agent (LangGraph) that answers ad-hoc questions with those tools
src/agents/review_agent.py
Dashboard with Overview, Trends, Flagged reviews, Assistant chat and Audit log
src/frontend
Guardrails: clarification, prompt-injection, privacy, role gate, grounding checks
src/guardrails
Audit trail of every question and answer, with latency, tokens and cost
src/utils/audit_logger.py
Mocked role-based access (brand manager and support team)
src/agents/roles.py
Conversation memory so follow-up questions work in the same chat
src/agents/review_agent.py
Automated tests (pytest)
tests

Architecture
Streamlit dashboard (src/frontend)
        |  HTTP
FastAPI backend (src/main.py)
  routers -> services -> tools / agent
        |
  ReviewAgent (LangGraph)  --MCP over stdio-->  MCP server (src/mcp/server.py)
                                                 |-- sentiment_trend
                                                 |-- flagged_reviews
                                                 |-- generate_summary_report
                                                 `-- search_reviews  -> ChromaDB
Data: CSV (aggregations) + ChromaDB (semantic search over review text)

Folder
Purpose
src/config
constants, settings (paths, environment), prompts, logging setup
src/routers, src/services, src/schemas
FastAPI layers
src/exceptions
custom errors and the handlers that map them to HTTP responses
src/agents
the agent, role definitions, role gate and per-role tool access
src/guardrails
input checks (before the model) and grounding checks (after it)
src/mcp
MCP server, tool registry and the tool implementations
src/rag
ChromaDB retriever and a small LLM client with retries
src/repositories
review data loading and filtering
src/data_prep
labeling rules, safety flags, PII scrubbing, vector store build (batch scripts)
src/evaluation
evaluation question set and runner
src/frontend
Streamlit app, API client, chat history store, question suggestions
src/utils
audit log, progress log, run log
tests
pytest suite
docs
PII handling note, sample audit log, evaluation summary
reports
sample brand-health report

Setup
Requires Python 3.10 or newer.
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
Open .env and fill in the keys for the models you want to use:
GROQ_API_KEY=
OPENROUTER_API_KEY=
Data files are not in the repository (see .gitignore). Place them as:
data/raw/raw_reviews.csv
data/labeled/reviews_scrubbed.csv
data/vectorstore/chroma_db/
Run
Terminal 1, backend (the agent warms up on startup, about a minute):
uvicorn src.main:app --reload
Terminal 2, dashboard:
streamlit run src/frontend/app.py
API docs: http://127.0.0.1:8000/docs
Roles
The role is chosen with a URL parameter, so each role has its own page.
Role
URL
Tabs
Tools the agent may use
Brand manager
http://localhost:8501/?role=brand_manager
Overview, Trends, Flagged reviews, Assistant, Audit log
all four
Support team
http://localhost:8501/?role=support_team
Flagged reviews, Assistant, Audit log
flagged reviews and review search

Each role gets its own agent with only its tools.
If the support team asks for a sentiment trend or a summary report, the question is stopped before any model call with a clear message that names what the role can do.
The brand manager sees the full audit log. The support team sees only its own session, with time, question, status, latency, tokens and cost, and without answers or tool arguments.
This is a mocked access layer for the capstone. There is no login.
Using the dashboard
Overview: totals, sentiment by aspect and flagged reviews by severity.
Trends: pick a product and a date range (only dates that have reviews can be selected), and group by week, month or year.
Flagged reviews: the most severe safety and quality reviews first.
Assistant: ask in plain language. A panel on the left lists saved conversations, with New chat and delete buttons, and it can be hidden. "Try a question" suggests questions that fit the role. A status line shows what the agent is doing while it works.
Audit log: see the role rules above.
Theme: use the menu at the top right, then Settings, to choose light, dark or the system theme.
Command line
All tools and batch jobs can also be run from the command line:
python -m src.cli sentiment-trend --aspect packaging --granularity month --periods 6
python -m src.cli flagged-reviews --level high --days 365 --limit 5
python -m src.cli summary-report --days 30 --save
python -m src.cli audit-summary
summary-report --save writes the report to reports/. The dataset ends on 2023-03-21, so "last week" means the 7 days before that date.
Tests and coverage
python -m pytest tests/ -q
python -m pytest tests/ -q --cov=src --cov-report=term-missing
.coveragerc measures the backend. The Streamlit app is excluded because pytest does not run it. The tests use fake objects for the model, the MCP server and ChromaDB, so they need no API key and no data files.
Evaluation
python -m src.cli evaluate --models groq:openai/gpt-oss-120b
The runner asks the agent a fixed set of questions, including adversarial ones, and checks the tool used, the facts, the citations and the grounding of each answer. It writes data/evaluation/results.csv and summary.csv. A copy of the summary is in docs/evaluation_summary.csv.
Sample outputs
reports/brand_health_report_2023-03-21_30d.md: generated brand-health report.
docs/sample_audit_log.jsonl: audit log from a demo session.
docs/evaluation_summary.csv: evaluation summary.
docs/PII_HANDLING.md: how reviewer identity data is handled.
Guardrails
Before the model: questions that are too broad get a clarifying reply, out-of-scope questions (policies, returns) are declined, prompt-injection attempts are blocked, and questions about reviewer identity are refused.
Role gate: a role is stopped before any model call when the question needs a tool it may not use.
Review text is data: retrieved reviews that look like instructions are flagged and never followed.
After the model: citations, quoted text and numbers in the answer are checked against the tool output, and the results are stored with the answer.
Audit trail
Every question and answer is appended to logs/audit_log.jsonl: session, role, question, answer, tools called, grounding checks, tokens, latency and cost. The dashboard's live status comes from logs/progress_log.jsonl. Data-prep runs are logged in logs/run_log.csv. Reviewer identity handling is described in docs/PII_HANDLING.md.
Errors
Failures use custom exceptions with a fixed status code, error code and message, defined in one place (ERROR_DEFINITIONS in src/config/constants.py). The API returns the same error shape for every failure. Rate limits and oversized prompts from the model provider are reported as friendly messages.
Regenerating data (only if needed)
python -m src.cli apply-label-rules
python -m src.cli scrub-pii
python -m src.cli build-vectorstore
python -m src.cli recompute-safety-flags
apply-label-rules replaces sentiment and aspect labels with the rule-based versions.
scrub-pii masks reviewer identity columns and redacts PII typed inside review text.
build-vectorstore rebuilds the ChromaDB collection and replaces the existing one (about an hour on a CPU).
recompute-safety-flags recomputes safety and quality flags and syncs them into ChromaDB.
Known limits
The free tier of the model provider limits tokens per minute, which can cause slow answers or 429 and 413 errors. The agent starts a fresh context window every 4 questions to keep prompts short, so it remembers only the most recent questions.
Sentiment follows the star rating. Aspects and safety flags come from keyword rules.
Chat history for the dashboard is stored in a local JSON file.
Access control is mocked with a URL parameter. There is no login.


