# 🧠 Dev AI

**Dev AI** is a production-ready RAG-based Q&A command-line interface with automated citation grounding verification, TF-IDF retrieval, and evaluation reporting.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **TF-IDF Retrieval** | High-precision chunking and scoring over local document collections |
| **Grounding Verification** | Automatically verifies that every claim carries grounded inline citations (`[1]`, `[2]`) |
| **Gap Detection** | Identifies missing information and flags when retrieved context is insufficient |
| **Batch & Eval Pipeline** | Run batch evaluation suites and score citation accuracy with `eval.py` |
| **Interactive CLI & Web UI** | Command-line interface with interactive mode and local web server options |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Dev AI CLI / Web UI                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                       Dev AI Engine                         │
│                                                             │
│  1. Retrieve Chunks (TF-IDF Vector Store)                   │
│  2. Build Context & Grounding Prompt                        │
│  3. LLM Answer Synthesis (OpenAI / OpenRouter / NVIDIA NIM) │
│  4. Post-Process & Verify Citation Grounding                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- At least one LLM API key (`GEMINI_API_KEY` or `NVIDIA_API_KEY`)

> **Automatic 3-Tier Provider Fallback**:
> 1. **`gemini-3.6-flash`**: Primary model tried first when `GEMINI_API_KEY` is present.
> 2. **`gemini-3-flash`**: Automatic fallback if `gemini-3.6-flash` encounters quota, billing, or 402/403/429 rate-limit errors.
> 3. **NVIDIA NIM**: Final fallback if `GEMINI_API_KEY` is missing or all Gemini attempts fail (uses `NVIDIA_API_KEY`).

### 1. Clone & Configure

```bash
git clone https://github.com/Devaraj0007/dev-ai.git
cd dev-ai
cp .env.example .env
# Edit .env and set GEMINI_API_KEY or NVIDIA_API_KEY
```

### 2. Install Dependencies & Build Index

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m src.cli ingest
```

### 3. Usage

#### Ask a Question
```bash
python -m src.cli ask "What is the parental leave policy?"
```

#### Run Interactive Mode
```bash
python -m src.cli interactive
```

#### Run Batch Evaluation
```bash
python -m src.cli batch questions.txt --out outputs/sample_qa.json
python eval.py outputs/sample_qa.json
```

#### Run Unit Tests
```bash
python -m unittest discover tests
```

---

## 🌐 Web UI (Optional Demo)

Dev AI includes an optional web interface demo built with **FastAPI** (`backend_api/`) and **Next.js** (`frontend/`) featuring Vengeance UI animated components.

> **Note**: The CLI (`python -m src.cli`) remains the primary entry point. The Web UI is a thin, optional API layer built on top of `src/`.

### 1. Start the FastAPI Backend

```bash
pip install -r backend_api/requirements.txt
uvicorn backend_api.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/health`
- Interactive API Docs: `http://localhost:8000/docs`

### 2. Start the Next.js Frontend

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to submit research questions and view grounded answer cards with live citation verification badges.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

