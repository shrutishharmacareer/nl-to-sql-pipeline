import pandas as pd
from sqlalchemy import text
from schema_extractor import get_engine, get_full_db_context
from llm_handler import nl_to_sql, fix_sql, summarize_results
from dotenv import load_dotenv

load_dotenv()

MAX_RETRIES = 2  # How many times to self-heal before giving up


# ---- Execute SQL ----
def execute_sql(sql: str, engine) -> dict:
    """
    Runs SQL query on PostgreSQL.
    Returns results as a pandas DataFrame.
    """
    try:
        with engine.connect() as conn:
            result = pd.read_sql(text(sql), conn)
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


# ---- Full Pipeline: Question → SQL → Results ----
def run_pipeline(user_question: str) -> dict:
    """
    Full end-to-end pipeline:
    1. Get DB schema
    2. Send to Claude → get SQL
    3. Execute SQL on PostgreSQL
    4. If fails → self heal → retry
    5. Summarize results in plain English

    Returns:
    {
        "success": True/False,
        "question": "original question",
        "sql": "SELECT ...",
        "data": DataFrame or None,
        "summary": "plain english summary",
        "error": None or "error message"
    }
    """
    print("\n" + "="*60)
    print(f"🚀 Running pipeline for: {user_question}")
    print("="*60)

    # Step 1 — Get DB context
    engine = get_engine()
    db_context = get_full_db_context(engine)

    # Step 2 — Generate SQL
    llm_result = nl_to_sql(user_question, db_context)

    if not llm_result["success"]:
        return {
            "success": False,
            "question": user_question,
            "sql": None,
            "data": None,
            "summary": None,
            "error": llm_result["error"]
        }

    sql = llm_result["sql"]

    # Step 3 — Execute SQL (with self-healing retry)
    for attempt in range(MAX_RETRIES):
        print(f"\n⚡ Executing SQL (attempt {attempt + 1})...")
        exec_result = execute_sql(sql, engine)

        if exec_result["success"]:
            print("✅ Query executed successfully!")
            df = exec_result["data"]
            print(f"📊 Returned {len(df)} rows, {len(df.columns)} columns")

            # Step 4 — Summarize results
            print("💬 Generating summary...")
            results_preview = df.head(10).to_string()
            summary = summarize_results(user_question, sql, results_preview)

            return {
                "success": True,
                "question": user_question,
                "sql": sql,
                "data": df,
                "summary": summary,
                "error": None
            }

        else:
            print(f"❌ SQL execution failed: {exec_result['error']}")

            # Self-heal — ask Claude to fix the SQL
            if attempt < MAX_RETRIES - 1:
                fix_result = fix_sql(
                    user_question,
                    sql,
                    exec_result["error"],
                    db_context
                )

                if fix_result["success"]:
                    sql = fix_result["sql"]  # Try fixed SQL next iteration
                else:
                    break

    return {
        "success": False,
        "question": user_question,
        "sql": sql,
        "data": None,
        "summary": None,
        "error": exec_result["error"]
    }


# ---- Pretty Print Results ----
def print_results(pipeline_output: dict):
    """
    Prints pipeline results in a clean readable format.
    """
    print("\n" + "="*60)

    if not pipeline_output["success"]:
        print(f"❌ Pipeline failed: {pipeline_output['error']}")
        return

    print(f"❓ Question : {pipeline_output['question']}")
    print(f"\n📝 SQL Query:\n{pipeline_output['sql']}")
    print(f"\n📊 Results ({len(pipeline_output['data'])} rows):")
    print(pipeline_output["data"].to_string(index=False))
    print(f"\n💬 Summary:\n{pipeline_output['summary']}")
    print("="*60)


# ---- Test it ----
if __name__ == "__main__":
    test_questions = [
        "Show me all customers from USA",
        "What are the top 5 products by total sales?",
        "How many orders were placed in 2004?",
        "Which country has the highest total revenue?",
        "What is the average order value by deal size?"
    ]

    for question in test_questions:
        result = run_pipeline(question)
        print_results(result)