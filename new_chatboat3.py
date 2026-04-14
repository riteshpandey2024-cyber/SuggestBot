import streamlit as st
import sqlite3
import google.generativeai as genai
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
import pandas as pd
import os
from rapidfuzz import process, fuzz

# === API Key for Gemini ===
genai.configure(api_key="AIzaSyA8-Q1tO01v3RN3OW_#######")  # Replace with your actual Gemini API key
model = genai.GenerativeModel("gemini-2.0-flash")

# === Path to your SQLite DB ===
db_path = r"C:\\Users\\rajs1\\Downloads\\newdata.db\\ansh.db"
chat_db_path = db_path

# === Database functions ===
def test_connection(db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Treatment';")
        result = cur.fetchone()
        conn.close()
        return "✅ Connected and 'Treatment' table exists." if result else "⚠️ Connected, but 'Treatment' table does not exist."
    except Exception as e:
        return f"❌ Connection failed: {e}"

def show_table_preview(db):
    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query("SELECT * FROM Treatment LIMIT 5;", conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error: {e}"

def read_sql_query(sql, db):
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

# === Chat history table ===
def initialize_chat_history_table():
    conn = sqlite3.connect(chat_db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ChatHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def save_chat_to_db(username, msg):
    conn = sqlite3.connect(chat_db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO ChatHistory (username, role, content) VALUES (?, ?, ?)", (username, msg.type, msg.content))
    conn.commit()
    conn.close()

def load_chat_from_db(username):
    conn = sqlite3.connect(chat_db_path)
    df = pd.read_sql_query("SELECT role, content FROM ChatHistory WHERE username = ? ORDER BY timestamp", conn, params=(username,))
    conn.close()
    history = ChatMessageHistory()
    for _, row in df.iterrows():
        if row["role"] == "human":
            history.add_user_message(row["content"])
        elif row["role"] == "ai":
            history.add_ai_message(row["content"])
    return history

# === Fuzzy matching and disease extraction ===
def get_all_diseases(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Disease FROM Treatment;")
    diseases = [row[0].strip() for row in cur.fetchall()]
    conn.close()
    return diseases

def find_best_disease_match(question, disease_list, threshold=85):
    question_lower = question.lower().strip()
    disease_lower_map = {d.lower(): d for d in disease_list}
    if question_lower in disease_lower_map:
        return disease_lower_map[question_lower]
    best_match = process.extractOne(question_lower, list(disease_lower_map.keys()), scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] >= threshold:
        return disease_lower_map[best_match[0]]
    return None

def extract_disease_from_question(question, disease_list):
    question_lower = question.lower()
    for disease in disease_list:
        if disease.lower() in question_lower:
            return disease
    return None

# === Get Gemini response with history ===
def get_gemini_sql_response(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

def get_gemini_response_with_history(username, question):
    user_chat_history = st.session_state[f"chat_history_{username}"]
    diseases = get_all_diseases(db_path)
    best_match = extract_disease_from_question(question, diseases)
    if not best_match:
        best_match = find_best_disease_match(question, diseases)

    refers_to_previous = any(phrase in question.lower() for phrase in ["this disease", "this"])
    if not best_match and refers_to_previous and st.session_state.get("last_disease"):
        best_match = st.session_state["last_disease"]

    if best_match:
        st.session_state["last_disease"] = best_match
        st.info(f"🤖 Detected disease: **{best_match}**")
        sql_query = f"SELECT treat FROM Treatment WHERE Disease = '{best_match}';"

        # Save user message and SQL to chat
        user_chat_history.add_user_message(question)
        save_chat_to_db(username, HumanMessage(content=question))
        user_chat_history.add_ai_message(sql_query)
        save_chat_to_db(username, AIMessage(content=sql_query))

        # Fetch SQL result
        results = read_sql_query(sql_query, db_path)
        if results and not results[0][0].startswith("Error"):
            treatment_text = results[0][0]
            # Add some extra explanation
            friendly_text = (
                f"The recommended treatment for **{best_match}** is:\n\n"
                f"{treatment_text}\n\n"
                "Please consult your healthcare provider for personalized advice."
            )
            user_chat_history.add_ai_message(friendly_text)
            save_chat_to_db(username, AIMessage(content=friendly_text))
            return friendly_text
        else:
            return "⚠️ No result found or SQL error occurred."
    else:
        st.warning("⚠️ No close disease match found. Please check the spelling or try a different query.")
        return ""

# === New function for concise disease info ===
def generate_concise_disease_info(disease, question):
    prompt = (
        f"The user asked: {question}\n"
        f"Provide a concise and clear summary about the disease '{disease}' in 3-4 sentences."
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# === Streamlit App ===
st.set_page_config(page_title="💬 Ayushveda - Disease Assistant")
st.title("💬 Welcome to Ayushveda")
st.markdown("🙏 **Namaste!** Welcome to **Ayushveda** — your trusted assistant for disease treatments and general health queries.")
st.sidebar.header("Setup")

username = st.sidebar.text_input("Enter your username:", key="username")
if not username:
    st.warning("Please enter your username to continue.")
    st.stop()

initialize_chat_history_table()
if f"chat_history_{username}" not in st.session_state:
    st.session_state[f"chat_history_{username}"] = load_chat_from_db(username)

user_chat_history = st.session_state[f"chat_history_{username}"]

st.sidebar.write(f"📁 DB Path: `{os.path.abspath(db_path)}`")
st.sidebar.success(test_connection(db_path))

if st.sidebar.checkbox("Preview Treatment Table"):
    preview = show_table_preview(db_path)
    if isinstance(preview, pd.DataFrame):
        st.sidebar.dataframe(preview)
    else:
        st.sidebar.warning(preview)

question = st.text_input("Ask your question:")
submit = st.button("Submit")

if submit and question:
    with st.spinner("Processing your request..."):
        treatment_keywords = ["treatment", "treat", "disease", "cure", "therapy", "medicine"]
        symptom_keywords = ["symptom", "sign", "indication", "feature", "how does", "what happens", "effects"]
        subscription_keywords = ["subscription", "cost", "price", "membership", "fee"]

        lower_q = question.lower()

        if any(word in lower_q for word in treatment_keywords):
            # Treatment request: fetch from DB and show treatment as is
            response = get_gemini_response_with_history(username, question)
            if response:
                st.success(response)
            else:
                st.error("❌ No response found.")

        elif any(word in lower_q for word in symptom_keywords) or ("this disease" in lower_q or "it" in lower_q):
            # Symptoms / follow-up info request
            diseases = get_all_diseases(db_path)
            disease = extract_disease_from_question(question, diseases)
            if not disease:
                disease = st.session_state.get("last_disease")

            if disease:
                concise_info = generate_concise_disease_info(disease, question)
                user_chat_history.add_user_message(question)
                save_chat_to_db(username, HumanMessage(content=question))
                user_chat_history.add_ai_message(concise_info)
                save_chat_to_db(username, AIMessage(content=concise_info))
                st.success(concise_info)
            else:
                st.warning("⚠️ Please specify the disease for more information.")

        elif any(word in lower_q for word in subscription_keywords):
            st.success("💰 The subscription cost is ₹150.")

        else:
            # General AI response
            user_chat_history.add_user_message(question)
            save_chat_to_db(username, HumanMessage(content=question))
            response = model.generate_content(question).text.strip()
            user_chat_history.add_ai_message(response)
            save_chat_to_db(username, AIMessage(content=response))
            st.write(f"🧠 Gemini: {response}")
else:
    st.info("Ask me anything about disease treatments or health!")

st.markdown("---")
st.markdown("© 2025 Ayushveda | Powered by Gemini and SQLite")
