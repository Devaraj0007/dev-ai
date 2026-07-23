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
- At least one LLM API key (OpenAI, OpenRouter, or NVIDIA NIM)

### 1. Clone & Configure

```bash
git clone https://github.com/Devaraj0007/dev-ai.git
cd dev-ai
cp .env.example .env
# Edit .env and add your API key
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

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
