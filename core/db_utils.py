"""
core/db_utils.py — Database connection, queries, and chat history management.
"""

import sqlite3
import pandas as pd


def get_connection(db_path):
    """Get a SQLite database connection."""
    return sqlite3.connect(db_path)


def test_connection(db_path):
    """Test database connection and check if Treatment table exists."""
    try:
        conn = get_connection(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Treatment';")
        result = cur.fetchone()
        conn.close()
        if result:
            return True, "Connected — Treatment table found"
        else:
            return False, "Connected — but Treatment table is missing"
    except Exception as e:
        return False, f"Connection failed: {e}"


def get_table_preview(db_path, limit=5):
    """Get a preview of the Treatment table."""
    try:
        conn = get_connection(db_path)
        df = pd.read_sql_query(f"SELECT * FROM Treatment LIMIT {limit};", conn)
        conn.close()
        return df
    except Exception as e:
        return None


def get_all_diseases(db_path):
    """Get all unique disease names from the database."""
    try:
        conn = get_connection(db_path)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT Disease FROM Treatment ORDER BY Disease;")
        diseases = [row[0].strip() for row in cur.fetchall()]
        conn.close()
        return diseases
    except Exception:
        return []


def get_disease_count(db_path):
    """Get total number of diseases in the database."""
    try:
        conn = get_connection(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Treatment;")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def query_treatment(db_path, disease):
    """Query treatment for a specific disease."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT treat FROM Treatment WHERE Disease = ?;", (disease,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception:
        conn.close()
        return None


def execute_sql(db_path, sql):
    """Execute a raw SQL query and return results."""
    sql = sql.replace('\u201c', "'").replace('\u201d', "'")
    conn = get_connection(db_path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        conn.close()
        return [(f"Error: {e}",)]


# === Chat History ===

def initialize_chat_history_table(db_path):
    """Create the ChatHistory table if it doesn't exist."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ChatHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_chat_message(db_path, username, role, content):
    """Save a single chat message to the database."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ChatHistory (username, role, content) VALUES (?, ?, ?)",
        (username, role, content)
    )
    conn.commit()
    conn.close()


def load_chat_history(db_path, username):
    """Load chat history for a user from the database."""
    try:
        conn = get_connection(db_path)
        df = pd.read_sql_query(
            "SELECT role, content FROM ChatHistory WHERE username = ? ORDER BY timestamp",
            conn, params=(username,)
        )
        conn.close()

        messages = []
        for _, row in df.iterrows():
            messages.append({"role": row["role"], "content": row["content"]})
        return messages
    except Exception:
        return []


def clear_chat_history(db_path, username):
    """Clear all chat history for a specific user."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM ChatHistory WHERE username = ?;", (username,))
    conn.commit()
    conn.close()


def get_user_chat_dataframe(db_path, username):
    """Fetch complete chat history dataframe with timestamps for export."""
    try:
        conn = get_connection(db_path)
        df = pd.read_sql_query(
            "SELECT timestamp as Timestamp, username as User, role as Role, content as Message FROM ChatHistory WHERE username = ? ORDER BY timestamp ASC",
            conn, params=(username,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()
