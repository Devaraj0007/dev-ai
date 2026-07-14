# Research Agent (with Citations)

An advanced research agent that answers questions from local source documents
with grounded citations. It also supports a general chat mode, but the
submission is optimized for the citation-checked research flow.

Built for the 24-Hour AI Agent Challenge.

## What reviewers can run

- End-to-end research Q&A with citations.
- A second general mode for open-ended questions.
- A batch run with 1,113 sample questions in `data/questions.txt`.
- A saved demo output file in `outputs/sample_qa.json`.
- A web UI at `python -m src.web`.
- MIT license in the repository root for reuse clarity.

## Install

### Windows PowerShell

```powershell
git clone https://github.com/Devaraj0007/research-agent.git
cd research-agent
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
py -3.11 -m pip install -r requirements.txt
```

### macOS / Linux

```bash
git clone https://github.com/Devaraj0007/research-agent.git
cd research-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configure API keys

Copy the example environment file and add your OpenRouter key:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:

```ini
OPENROUTER_API_KEY=your-openrouter-api-key-here
RESEARCH_AGENT_MODEL=google/gemini-2.5-flash:nitro
RESEARCH_AGENT_MODE=research
RESEARCH_AGENT_TOP_K=4
RESEARCH_AGENT_MIN_SCORE=0.05
```

`RESEARCH_AGENT_MODE=research` is the recommended default for the challenge.
Use `general` only if you want a normal chat assistant demo.

## Run end to end

Build the retrieval index once:

```bash
python -m src.cli ingest
```

Run the full sample batch and save the results:

```bash
python -m src.cli batch --mode research data/questions.txt --out outputs/sample_qa.json
```

Ask a single question:

```bash
python -m src.cli ask --mode research "How many weeks of paid parental leave do employees get once they've completed 12 months of service?"
```

Interactive mode:

```bash
python -m src.cli interactive --mode research
```

Optional validation on the saved batch:

```bash
python eval.py outputs/sample_qa.json
```

Web UI:

```bash
python -m src.web
```

Open http://127.0.0.1:8000 in your browser.

## Sample output

The checked-in file [outputs/sample_qa.json](outputs/sample_qa.json) contains a
real 1,113-question batch run. It includes grounded answers, explicit gap
notes for out-of-scope questions, and citation metadata.

## Design choices

- TF-IDF + cosine similarity for retrieval, implemented in pure Python.
- OpenRouter for model access so the model is swappable through one config.
- Research mode validates citation numbers after generation.
- General mode is kept as a fallback demo path, but research mode is the main
  showcase.
- The repo includes a web UI and batch CLI so reviewers can test different
  execution paths.

## Tradeoffs and limitations

- TF-IDF is lexical, so paraphrased questions can under-retrieve.
- The grounding check verifies citation numbers, not full semantic support.
- The agent still requires an OpenRouter key for real responses.
- The web UI and batch mode rely on the same local index, so the first `ingest`
  step is required after a fresh clone.

## Validation

These commands were run successfully in this workspace:

```bash
python -m pytest tests/test_agent.py
python -m unittest tests/test_retriever.py
python -m src.cli ingest
python -m src.cli batch --mode research data/questions.txt --out outputs/sample_qa.json
python eval.py outputs/sample_qa.json
```
