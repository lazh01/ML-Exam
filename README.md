# Ad Campaign Analytics Agent

An AI agent that answers natural-language questions about social media advertising data.
Built with the Mistral API and a set of Python tools for data querying, statistical analysis, and visualization.

## What it does

The agent can:
- Answer questions about campaign performance (ROI, CTR, CPC, CPM, conversion rate)
- Compare platforms, cities, audiences, and campaign types
- Generate interactive HTML charts and dashboards using Plotly
- Generate static PNG charts using Matplotlib and Seaborn

## Project structure

```
ad_agent/
├── agent.py              # Main agent loop and tool dispatcher
├── logger.py             # Session-based tool call logger
├── run_tests.py          # Runs all fixed test cases
├── export_use_cases.py   # Exports use cases to use_cases.md
├── requirements.txt      # Python dependencies
├── tools/
│   ├── __init__.py
│   ├── query_data.py     # inspect_dataset — returns schema and sample rows
│   ├── execute_code.py   # Executes LLM-generated pandas/numpy code
│   ├── plot_code.py      # Executes LLM-generated visualization code
│   └── plot_chart.py     # Deterministic chart tool (bar, line, scatter, pie)
├── data/
│   └── ads.csv           # Dataset (not included, see Setup)
├── sessions/             # Auto-created, one folder per session with logs and outputs
└── test_results/         # Auto-created when running run_tests.py
```

## Dependencies

- Python 3.10+
- mistralai
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- scipy
- scikit-learn
- python-dotenv

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ML-Exam.git
cd ML-Exam
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
cd ad_agent
pip install -r requirements.txt
```

### 4. Download the dataset

Download the dataset from Kaggle:
👉 https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset

Rename the file to `ads.csv` and place it in the `data/` folder.

### 5. Set up your API key

Create a `.env` file in the `ML-Exam/` folder (next to the `ad_agent/` folder):

```
MISTRAL_API_KEY=your_key_here
```

Get your free API key at https://console.mistral.ai

## How to run

### Interactive mode

```bash
python agent.py
```

Type your question when prompted. Example:

```
Which advertising channel has the highest average ROI?
```

### Run all test cases

```bash
python run_tests.py
```

Results are saved to `test_results/test_results.json` and `test_results/test_results.txt`.

### Export use cases

```bash
python export_use_cases.py
```

Generates `use_cases.md` with all session inputs and outputs.

## Architecture

```
User query
    │
    ▼
Agent loop (mistral-large-latest)
    ├── inspect_dataset  → returns schema, column types, 3 sample rows
    ├── execute_code     → runs LLM-generated pandas/numpy code on the dataset
    ├── plot_chart       → creates png visualization using deterministic tool with matplotlib.
    └── plot_code        → runs LLM-generated visualization code (Plotly/Seaborn)
    │
    ▼
Plain-English answer grounded in computed results
```

Each session is logged to `sessions/<session_id>/log.jsonl` and all generated files are saved to `sessions/<session_id>/outputs/`.

## Dataset

**Marketing Campaign Performance Dataset** — Kaggle  
200,000 rows, 16 columns including: platform, campaign type, target audience, location, clicks, impressions, acquisition cost, ROI, conversion rate, and start date.

Each row represents a single campaign summary — not daily measurements.

## Notes

- The dataset is synthetic and intentionally flat, meaning statistical trends are weak by design
- Generated code is validated for banned patterns before execution (`os.`, `subprocess`, `open()` etc.)
