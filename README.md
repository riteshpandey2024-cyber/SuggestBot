# SuggestBot - AI-Powered Disease Treatment Assistant

SuggestBot is an intelligent chatbot system that converts user queries into SQL queries and retrieves disease treatment information from a structured database. It integrates AI models (LLaMA & Gemini) with SQLite to provide accurate, conversational, and context-aware responses.

---

##  Features

-  Natural Language to SQL Conversion using LLaMA
-  AI Chatbot powered by Google Gemini
-  Context-aware conversation with chat history
-  SQLite database integration for disease-treatment mapping
-  Fuzzy matching for better disease detection (handles typos)
-  Database preview and connection status
-  Multi-user chat history stored in database
-  Real-time query processing using Streamlit UI

---

##  Tech Stack

- **Frontend/UI**: Streamlit  
- **Backend**: Python  
- **Database**: SQLite  
- **AI Models**:  
  - LLaMA (via Ollama)  
  - Google Gemini API  
- **Libraries**:  
  - LangChain  
  - Pandas  
  - RapidFuzz  
  - SQLite3  

---

## 📁 Project Structure
 
```
SuggestBot/
|
├── Bot-3.0/
|   |
|   ├── app/
|   |   ├── main.py                # Entry point (Streamlit app - Gemini chatbot)
|   |   ├── llama_engine.py        # LLaMA-based SQL query generator
|   |   ├── db_utils.py            # Database connection & query functions
|   |   ├── chat_history.py        # Chat history management (SQLite)
|   |   ├── disease_matcher.py     # Fuzzy matching & disease extraction
|   |   └── config.py              # API keys & configuration
|   |
|   ├── database/
|   |   └── ritesh.db              # SQLite database
|   |
|   ├── models/
|   |   └── prompts.py             # Prompt templates (LangChain)
|   |
|   ├── utils/
|   |   └── helpers.py             # Common helper functions
|   |
|   ├── requirements.txt           # Dependencies
|   ├── README.md                  # Project documentation
|   ├── .gitignore
|   └── run.sh / run.bat           # Run script (optional)
|
├── health_Code.py                 # LLaMA-based SQL query generator
├── new_chatboat3.py               # Gemini-based chatbot with memory
└── README.md
```

--- 


---

## 🗄️ Database Schema

### Table: `Treatment`

| Column   | Type  | Description                  |
|----------|------|------------------------------|
| Disease  | TEXT | Name of the disease          |
| treat    | TEXT | Corresponding treatment info |

---

##  Installation & Setup

###  Clone the Repository
```bash
git clone https://github.com/riteshpandey2024-cyber/SuggestBot.git
cd SuggestBot
```

### Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
## Setup Database
 
- Update the database path in code:
 
```python
db_path = "path_to_your_database.db"
```
 
##  Setup API Keys
 
- Replace Gemini API key in:
 
```python
genai.configure(api_key="YOUR_API_KEY")
```
 
##  Run the Application
 
```bash
streamlit run new_chatboat3.py
```
 

