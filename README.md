# 🤖 Natural Language to SQL Pipeline

> Ask your database anything in plain English — powered by Claude AI + PostgreSQL

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B?logo=streamlit)
![Claude AI](https://img.shields.io/badge/Claude-AI-orange?logo=anthropic)

---

## 📌 Overview

A production-grade **Natural Language to SQL** pipeline that lets business users query a PostgreSQL database using plain English — no SQL knowledge required.

Type a question → Claude AI writes the SQL → Results appear instantly as a formatted table with a plain English summary.

---

## 🏗️ Architecture

```
User (Natural Language Question)
        ↓
   Streamlit UI (Chat Interface)
        ↓
   Schema Extractor (reads DB metadata + sample rows)
        ↓
   Claude AI (converts question + schema → SQL)
        ↓
   Safety Validator (blocks dangerous queries)
        ↓
   Query Executor (runs SQL on PostgreSQL)
        ↓
   Self-Healing (if query fails → Claude fixes it → retry)
        ↓
   Result Formatter (table + plain English summary)
        ↓
   Response to User
```

---

## ✨ Features

- 💬 **Natural Language Queries** — Ask questions in plain English, no SQL needed
- 🧠 **Claude AI Powered** — Uses Anthropic's Claude to generate accurate PostgreSQL queries
- 🔧 **Self-Healing SQL** — If a query fails, automatically sends error back to Claude to fix and retry
- 🛡️ **Safety Validation** — Blocks all dangerous queries (DROP, DELETE, UPDATE, etc.)
- 📊 **Interactive Results** — Sortable, filterable data tables in the browser
- 💬 **Plain English Summaries** — Claude explains query results in simple language
- 🕐 **Query History** — Session-based history of all questions and results
- ⚡ **Schema Awareness** — Automatically reads DB schema + sample rows for accurate SQL generation

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Anthropic Claude API (claude-sonnet) |
| **Backend** | Python 3.11 |
| **Database** | PostgreSQL 15 |
| **DB Driver** | SQLAlchemy + psycopg2 |
| **Frontend** | Streamlit |
| **Data Processing** | Pandas |
| **Environment** | python-dotenv |

---

## 📁 Project Structure

```
nl-to-sql-pipeline/
│
├── src/
│   ├── schema_extractor.py   # Reads DB schema + sample rows
│   ├── llm_handler.py        # Claude API integration + prompt engineering
│   ├── query_executor.py     # SQL execution + self-healing pipeline
│   └── app.py                # Streamlit UI
│
├── data/
│   ├── setup_db.py           # Creates tables + inserts sample data
│   └── load_kaggle_data.py   # Loads Kaggle sales dataset into PostgreSQL
│
├── .env                      # API keys + DB credentials (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Anthropic API key (get one at https://console.anthropic.com)

### 1. Clone the Repository
```bash
git clone https://github.com/shrutishharmacareer/nl-to-sql-pipeline.git
cd nl-to-sql-pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nl_sql_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 5. Set Up the Database
```bash
# Create database in PostgreSQL first, then run:
python data/load_kaggle_data.py
```

### 6. Run the App
```bash
streamlit run src/app.py
```

Open your browser at **http://localhost:8501** 🎉

---

## 💡 Example Questions

```
"Show me all customers from USA"
"What are the top 5 products by total sales?"
"How many orders were placed in 2004?"
"Which country has the highest total revenue?"
"What is the average order value by deal size?"
"Which product line has the most orders?"
"Show me all Large deals from France"
"What is the total revenue per year?"
"Which month had the highest sales in 2003?"
```

---

## 📊 Dataset

Uses the [Sample Sales Data](https://www.kaggle.com/datasets/kyanyoga/sample-sales-data) dataset from Kaggle, loaded into 3 PostgreSQL tables:

| Table | Rows | Description |
|---|---|---|
| `customers` | 92 | Customer info, location, contact details |
| `products` | 109 | Product codes, lines, MSRP pricing |
| `orders` | 2,823 | Sales transactions with dates, quantities, revenue |

---

## 🔒 Security

- Only `SELECT` statements are allowed — all write operations are blocked
- API keys and DB credentials are stored in `.env` (never committed to git)
- SQL safety validator scans every query before execution

---

## 🏭 Industry Use Cases

This pipeline solves a real problem across industries:

- **Finance** — Analysts querying transaction data without SQL
- **E-Commerce** — Merchandising teams asking inventory and sales questions
- **Healthcare** — Non-technical staff querying patient or operational data
- **SaaS** — Product managers self-serving analytics without the data team

---

## 📈 Future Improvements

- [ ] Add support for multiple database connections
- [ ] Implement vector embeddings for smarter schema selection on large DBs
- [ ] Add query caching for repeated questions
- [ ] Export results to CSV/Excel
- [ ] Deploy on Streamlit Cloud for public access
- [ ] Add authentication for multi-user support

---

## 👩‍💻 Author

**Shruti Sharma**
- GitHub: [@shrutishharmacareer](https://github.com/shrutishharmacareer)

---

## 📄 License

MIT License — feel free to use and modify for your own projects.
