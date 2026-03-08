from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import os

load_dotenv()

# ---- DB Connection ----
def get_engine():
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return engine


# ---- Get Raw Schema ----
def get_schema_dict(engine):
    """
    Returns schema as a dictionary:
    {
        "customers": [
            {"name": "customer_id", "type": "INTEGER"},
            {"name": "customer_name", "type": "VARCHAR"},
            ...
        ],
        ...
    }
    """
    inspector = inspect(engine)
    schema_dict = {}

    for table_name in inspector.get_table_names():
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"])
            })
        schema_dict[table_name] = columns

    return schema_dict


# ---- Format Schema for LLM Prompt ----
def get_schema_for_prompt(engine):
    """
    Returns schema as a clean formatted string for LLM injection.

    Example output:
    Table: customers
      - customer_id (INTEGER)
      - customer_name (VARCHAR)
      ...
    """
    schema_dict = get_schema_dict(engine)
    schema_text = ""

    for table_name, columns in schema_dict.items():
        schema_text += f"Table: {table_name}\n"
        for col in columns:
            schema_text += f"  - {col['name']} ({col['type']})\n"
        schema_text += "\n"

    return schema_text.strip()


# ---- Get Sample Rows for each Table ----
def get_sample_rows(engine, n=3):
    """
    Returns n sample rows from each table.
    Helps LLM understand actual data format and values.
    """
    inspector = inspect(engine)
    sample_text = ""

    with engine.connect() as conn:
        for table_name in inspector.get_table_names():
            result = conn.execute(
                text(f"SELECT * FROM {table_name} LIMIT {n}")
            )
            rows = result.fetchall()
            columns = result.keys()

            sample_text += f"Sample rows from '{table_name}':\n"
            sample_text += "  " + ", ".join(columns) + "\n"
            for row in rows:
                sample_text += "  " + ", ".join(str(v) for v in row) + "\n"
            sample_text += "\n"

    return sample_text.strip()


# ---- Full Context for LLM (Schema + Samples) ----
def get_full_db_context(engine):
    """
    Combines schema + sample rows into one block.
    This is what gets injected into the LLM system prompt.
    """
    schema = get_schema_for_prompt(engine)
    samples = get_sample_rows(engine)

    full_context = f"""
=== DATABASE SCHEMA ===
{schema}

=== SAMPLE DATA ===
{samples}
""".strip()

    return full_context


# ---- Test it ----
if __name__ == "__main__":
    engine = get_engine()

    print("=" * 50)
    print("📋 SCHEMA:")
    print("=" * 50)
    print(get_schema_for_prompt(engine))

    print("\n" + "=" * 50)
    print("📊 SAMPLE ROWS:")
    print("=" * 50)
    print(get_sample_rows(engine))

    print("\n" + "=" * 50)
    print("🔗 FULL CONTEXT (what LLM sees):")
    print("=" * 50)
    print(get_full_db_context(engine))