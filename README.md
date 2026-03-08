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


