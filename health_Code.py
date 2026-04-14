import streamlit as st
import sqlite3
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import pandas as pd
import os

# Correct path to your SQLite DB
db_path = r"C:\Users\rajs1\Downloads\newdata.db\ansh.db"

# Initialize the LLaMA model
llm = OllamaLLM(model="llama2")

# ✅ Updated Prompt Template with single quotes for strings
prompt_template = PromptTemplate(
    input_variables=["question"],
    template="""
    You are an expert at converting English questions into SQL queries.
    The SQL database has a table named Treatment with the following columns:
    - Disease
    - treat

    Example 1 - What are the treatments for Diabetes?
    SELECT treat FROM Treatment WHERE Disease = 'Diabetes';

    Example 2 - List all diseases and their treatments.
    SELECT * FROM Treatment;

    Convert this question into an SQL query: {question}

    Note: Do not include ``` or the word "SQL" in your output.
    """
)

# Function to get SQL query using LLaMA
def get_llama_response(question, prompt_template):
    prompt = prompt_template.format(question=question)
    return llm.predict(prompt).strip()

# Function to execute SQL query
def read_sql_query(sql, db):
    # Sanitize quotes: replace curly quotes with straight quotes if any
    sql = sql.replace('“', "'").replace('”', "'")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        rows = [(f"Error: {e}",)]
    conn.commit()
    conn.close()
    return rows

# Function to test DB connection
def test_connection(db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Treatment';")
        result = cur.fetchone()
        conn.close()
        if result:
            return "✅ Connected to database and Treatment table exists."
        else:
            return "⚠️ Connected to database, but Treatment table does NOT exist."
    except Exception as e:
        return f"❌ Connection failed: {e}"

# Function to preview data
def show_table_preview(db):
    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query("SELECT * FROM Treatment LIMIT 5;", conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.set_page_config(page_title="Disease SQL Assistant")
st.header("Ask LLaMA to Query the Treatment Database")

# Sidebar: DB info
st.sidebar.header("Database Status")
st.sidebar.write(f"📁 DB Path: `{os.path.abspath(db_path)}`")

# Show DB connection status
status = test_connection(db_path)
if "Connected" in status:
    st.sidebar.success(status)
else:
    st.sidebar.error(status)

# Show preview if checkbox is selected
if st.sidebar.checkbox("Preview Treatment table"):
    preview = show_table_preview(db_path)
    if isinstance(preview, pd.DataFrame):
        st.sidebar.dataframe(preview)
    else:
        st.sidebar.warning(str(preview))  # Show error as text safely

# Main Input
question = st.text_input("Ask your question about diseases or treatments:", key="input")
submit = st.button("Submit")

if submit and question:
    with st.spinner("LLaMA is thinking..."):
        sql_query = get_llama_response(question, prompt_template)
        st.code(sql_query, language="sql")

        # Debug: show raw query with repr to detect any hidden characters
        st.write("Raw SQL query:", repr(sql_query))

        # Execute the sanitized query
        result = read_sql_query(sql_query, db_path)
        for row in result:
            st.write(row)
