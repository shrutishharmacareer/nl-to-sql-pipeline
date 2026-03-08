import streamlit as st
import sys
import os

# Fix import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from schema_extractor import get_engine, get_full_db_context
from llm_handler import nl_to_sql, fix_sql, summarize_results
from query_executor import run_pipeline, print_results

# ---- Page Config ----
st.set_page_config(
    page_title="NL to SQL Pipeline",
    page_icon="🤖",
    layout="wide"
)

# ---- Header ----
st.title("🤖 Natural Language to SQL Pipeline")
st.markdown("Ask your database anything in plain English!")
st.divider()

# ---- Sidebar ----
with st.sidebar:
    st.header("📊 Database Info")
    st.markdown("**Connected to:** `nl_sql_db`")
    st.markdown("**Tables:**")
    st.markdown("- 🧑 customers (92 rows)")
    st.markdown("- 📦 products (109 rows)")
    st.markdown("- 🛒 orders (2,823 rows)")

    st.divider()

    st.header("💡 Example Questions")
    example_questions = [
        "Show me all customers from USA",
        "What are the top 5 products by total sales?",
        "How many orders were placed in 2004?",
        "Which country has the highest total revenue?",
        "What is the average order value by deal size?",
        "Show me all Large deals from France",
        "Which product line has the most orders?",
        "What is the total revenue per year?"
    ]

    for q in example_questions:
        if st.button(q, use_container_width=True):
            st.session_state.question = q

    st.divider()
    st.markdown("Built with Claude AI + PostgreSQL")


# ---- Query History ----
if "history" not in st.session_state:
    st.session_state.history = []

if "question" not in st.session_state:
    st.session_state.question = ""


# ---- Main Input ----
col1, col2 = st.columns([5, 1])

with col1:
    user_question = st.text_input(
        label="Your Question",
        placeholder="e.g. What are the top 5 customers by revenue?",
        value=st.session_state.question,
        label_visibility="collapsed"
    )

with col2:
    ask_button = st.button("🔍 Ask", use_container_width=True, type="primary")


# ---- Run Pipeline ----
if ask_button and user_question:

    # Clear the prefilled question
    st.session_state.question = ""

    with st.spinner("🤔 Thinking..."):
        result = run_pipeline(user_question)

    if result["success"]:

        # ---- SQL Query ----
        st.subheader("📝 Generated SQL")
        st.code(result["sql"], language="sql")

        # ---- Results Table ----
        st.subheader(f"📊 Results — {len(result['data'])} rows returned")
        st.dataframe(
            result["data"],
            use_container_width=True,
            hide_index=True
        )

        # ---- Summary ----
        st.subheader("💬 Summary")
        st.info(result["summary"])

        # ---- Save to History ----
        st.session_state.history.append({
            "question": user_question,
            "sql": result["sql"],
            "rows": len(result["data"]),
            "summary": result["summary"]
        })

    else:
        st.error(f"❌ Error: {result['error']}")
        st.markdown("Try rephrasing your question or check the example questions in the sidebar.")


# ---- Query History ----
if st.session_state.history:
    st.divider()
    st.subheader("🕐 Query History")

    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Q: {item['question']} — {item['rows']} rows"):
            st.code(item["sql"], language="sql")
            st.write(item["summary"])


# ---- Empty State ----
if not ask_button and not st.session_state.history:
    st.markdown("")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("💡 **Tip:** Click any example question in the sidebar to try it instantly")

    with col2:
        st.info("🔍 **How it works:** Type a question → Claude writes SQL → Results appear instantly")

    with col3:
        st.info("📊 **Data:** 2,823 real sales orders across 92 customers and 109 products")