import anthropic
import os
import re
from dotenv import load_dotenv

load_dotenv()

# ---- Initialize Claude Client ----
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---- System Prompt ----
def build_system_prompt(db_context: str) -> str:
    """
    Builds the system prompt with DB schema injected.
    This tells Claude exactly what database it's working with.
    """
    return f"""
You are an expert PostgreSQL data analyst assistant.
Your job is to convert natural language questions into accurate PostgreSQL queries.

You have access to the following database:

{db_context}

STRICT RULES:
1. ONLY generate SELECT statements — never INSERT, UPDATE, DELETE, DROP, or ALTER
2. ALWAYS return valid PostgreSQL syntax
3. Use exact table and column names from the schema above
4. Return ONLY the SQL query — no explanation, no markdown, no backticks
5. If a question is ambiguous, make the most reasonable assumption
6. Always use table aliases for clarity when joining tables
7. For date filters, use PostgreSQL date functions
8. End every query with a semicolon

EXAMPLES:
User: "Show me all customers from USA"
Response: SELECT * FROM customers WHERE country = 'USA';

User: "What are the top 5 products by total sales?"
Response: SELECT p.product_line, SUM(o.sales) as total_sales FROM orders o JOIN products p ON o.product_id = p.product_id GROUP BY p.product_line ORDER BY total_sales DESC LIMIT 5;
""".strip()


# ---- Extract SQL from Response ----
def extract_sql(response_text: str) -> str:
    """
    Cleans LLM response to extract pure SQL.
    Handles cases where LLM adds markdown or explanation.
    """
    # Remove markdown code blocks if present
    response_text = re.sub(r"```sql", "", response_text)
    response_text = re.sub(r"```", "", response_text)

    # Strip whitespace
    response_text = response_text.strip()

    # Make sure it ends with semicolon
    if not response_text.endswith(";"):
        response_text += ";"

    return response_text


# ---- Validate SQL Safety ----
def is_safe_sql(sql: str) -> bool:
    """
    Checks SQL for dangerous keywords.
    Returns False if unsafe.
    """
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP",
        "ALTER", "TRUNCATE", "CREATE", "REPLACE",
        "EXEC", "EXECUTE", "GRANT", "REVOKE"
    ]
    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    return True


# ---- Main: Natural Language to SQL ----
def nl_to_sql(user_question: str, db_context: str) -> dict:
    """
    Main function — converts natural language to SQL using Claude.

    Returns:
    {
        "success": True/False,
        "sql": "SELECT ...",
        "error": None or "error message"
    }
    """
    try:
        print(f"\n🤔 User Question: {user_question}")
        print("📤 Sending to Claude...")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=build_system_prompt(db_context),
            messages=[
                {"role": "user", "content": user_question}
            ]
        )

        raw_response = response.content[0].text
        print(f"📥 Claude raw response: {raw_response}")

        # Extract and clean SQL
        sql = extract_sql(raw_response)
        print(f"🔍 Extracted SQL: {sql}")

        # Safety check
        if not is_safe_sql(sql):
            return {
                "success": False,
                "sql": None,
                "error": "⚠️ Unsafe SQL detected. Only SELECT queries are allowed."
            }

        return {
            "success": True,
            "sql": sql,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "sql": None,
            "error": str(e)
        }


# ---- Self Healing: Fix Bad SQL ----
def fix_sql(original_question: str, bad_sql: str,
            error_message: str, db_context: str) -> dict:
    """
    If SQL execution fails, send the error back to Claude to fix it.
    This is the self-healing feature.
    """
    try:
        print(f"\n🔧 Attempting self-heal...")
        print(f"❌ Failed SQL: {bad_sql}")
        print(f"💥 Error: {error_message}")

        fix_prompt = f"""
The following SQL query failed with an error.

Original question: {original_question}

Failed SQL:
{bad_sql}

Error message:
{error_message}

Please fix the SQL query. Return ONLY the corrected SQL, nothing else.
""".strip()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=build_system_prompt(db_context),
            messages=[
                {"role": "user", "content": fix_prompt}
            ]
        )

        raw_response = response.content[0].text
        fixed_sql = extract_sql(raw_response)

        print(f"✅ Fixed SQL: {fixed_sql}")

        if not is_safe_sql(fixed_sql):
            return {
                "success": False,
                "sql": None,
                "error": "Unsafe SQL detected in fix attempt."
            }

        return {
            "success": True,
            "sql": fixed_sql,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "sql": None,
            "error": str(e)
        }


# ---- Summarize Results ----
def summarize_results(user_question: str, sql: str, results: str) -> str:
    """
    After query runs, ask Claude to explain results
    in plain English to the user.
    """
    try:
        prompt = f"""
A user asked: "{user_question}"

We ran this SQL query:
{sql}

The results were:
{results}

Write a short 2-3 sentence plain English summary of these results.
Be specific with numbers. Be concise and friendly.
""".strip()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text.strip()

    except Exception as e:
        return f"Could not generate summary: {str(e)}"


# ---- Test it ----
if __name__ == "__main__":
    from schema_extractor import get_engine, get_full_db_context

    engine = get_engine()
    db_context = get_full_db_context(engine)

    # Test questions
    test_questions = [
        "Show me all customers from USA",
        "What are the top 5 products by total sales?",
        "How many orders were placed in 2004?",
        "Which country has the highest total revenue?"
    ]

    for question in test_questions:
        print("\n" + "="*60)
        result = nl_to_sql(question, db_context)

        if result["success"]:
            print(f"✅ SQL Generated Successfully!")
            print(f"📝 SQL: {result['sql']}")
        else:
            print(f"❌ Failed: {result['error']}")