"""
core/ai_engine.py — Google Gemini API integration for response generation.
Uses google.generativeai with automatic fallback.
"""

import google.generativeai as genai

_model = None
_client_type = None  # "gemini" or "openai"


def initialize_gemini(api_key):
    """Configure the Google Gemini API client."""
    global _model, _client_type
    if not api_key:
        _model = None
        _client_type = None
        return None

    clean_key = api_key.strip()

    # Try Google Gemini first
    try:
        genai.configure(api_key=clean_key)
        for model_name in ["gemini-flash-latest", "gemini-3.6-flash", "gemini-2.5-flash-lite", "gemini-pro-latest", "gemini-2.0-flash"]:
            try:
                m = genai.GenerativeModel(model_name)
                # Verify model works
                _model = m
                _client_type = "gemini"
                return _model
            except Exception:
                continue
    except Exception:
        pass

    # Fallback to OpenAI/xAI if an OpenAI key is provided
    try:
        from openai import OpenAI
        _model = OpenAI(
            api_key=clean_key,
            base_url="https://api.x.ai/v1",
        )
        _client_type = "openai"
        return _model
    except Exception:
        _model = None
        _client_type = None
        return None


def initialize_grok(api_key):
    """Backward-compatible alias for initialize_gemini."""
    return initialize_gemini(api_key)


def get_client():
    """Get the current AI model/client instance."""
    return _model


def _chat(prompt, max_tokens=500):
    """Send a prompt to Gemini (or fallback model) and return the response text."""
    global _model, _client_type
    if not _model:
        return None
    try:
        if _client_type == "gemini" or hasattr(_model, "generate_content"):
            response = _model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
        elif _client_type == "openai" or hasattr(_model, "chat"):
            response = _model.chat.completions.create(
                model="grok-3-mini-fast",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to alternative Gemini model if model generation fails
        try:
            for fallback_name in ["gemini-flash-latest", "gemini-3.6-flash", "gemini-2.5-flash-lite", "gemini-pro-latest"]:
                try:
                    fallback_m = genai.GenerativeModel(fallback_name)
                    res = fallback_m.generate_content(prompt)
                    if res and hasattr(res, "text") and res.text:
                        _model = fallback_m
                        _client_type = "gemini"
                        return res.text.strip()
                except Exception:
                    continue
        except Exception:
            pass
    return None


def generate_treatment_response(disease, treatment_text):
    """
    Generate a friendly, formatted treatment response.
    Combines DB data with Gemini AI enhancement.
    """
    prompt = f"""You are a friendly medical information assistant called Ayushveda.
The user asked about treatment for "{disease}".

Here is the treatment information from our database:
{treatment_text}

Please provide a well-formatted, friendly response that:
1. Acknowledges the disease
2. Presents the treatment information clearly with bullet points
3. Adds a brief disclaimer to consult a healthcare professional
4. Keep it concise (under 200 words)
5. Use emojis sparingly for friendliness

Do NOT add any information beyond what's in the database. Only format it nicely."""

    result = _chat(prompt)
    if result:
        return result
    return format_basic_treatment(disease, treatment_text)


def format_basic_treatment(disease, treatment_text):
    """Fallback formatting when AI API is unavailable."""
    return (
        f"### 🏥 Treatment for {disease}\n\n"
        f"{treatment_text}\n\n"
        "---\n"
        "⚠️ *Please consult your healthcare provider for personalized medical advice.*"
    )


def generate_disease_info(disease, question):
    """Generate concise disease info using Gemini AI."""
    prompt = f"""You are a friendly medical information assistant called Ayushveda.
The user asked: "{question}"
This is about the disease: {disease}

Provide a concise, accurate summary in 3-4 sentences. Include:
- Brief description of the disease
- Common symptoms
- When to seek medical help

Keep it professional but friendly. Use 1-2 emojis. Add a disclaimer to see a doctor."""

    result = _chat(prompt)
    if result:
        return result
    return f"I can provide treatment information for {disease}. Please ask about its treatment."


def generate_general_response(question, chat_context=""):
    """Generate a general health-related response using Gemini AI."""
    context_part = ""
    if chat_context:
        context_part = f"\nRecent conversation context:\n{chat_context}\n"

    prompt = f"""You are Ayushveda, a friendly and knowledgeable health assistant chatbot.
{context_part}
User's question: {question}

Guidelines:
- If the question is health-related, provide helpful, accurate information
- If it's a greeting, respond warmly and introduce yourself
- If it's unrelated to health, politely redirect to health topics
- Keep responses concise (under 150 words)
- Use friendly tone with 1-2 emojis
- Always recommend consulting a doctor for medical decisions"""

    result = _chat(prompt)
    if result:
        return result
    return "I'm sorry, the AI service is not available right now. Please check your API key."


def classify_query(question):
    """
    Classify the user's query into categories based on keywords.
    Returns: 'treatment', 'symptom', 'general'
    """
    lower_q = question.lower()

    treatment_keywords = [
        "treatment", "treat", "cure", "therapy", "medicine",
        "medication", "remedy", "drug", "prescription", "how to treat",
        "what is the treatment", "how to cure"
    ]

    symptom_keywords = [
        "symptom", "sign", "indication", "feature", "how does",
        "what happens", "effects", "causes", "cause", "what is",
        "tell me about", "explain", "describe", "information about",
        "info about", "details"
    ]

    if any(word in lower_q for word in treatment_keywords):
        return "treatment"
    elif any(word in lower_q for word in symptom_keywords):
        return "symptom"
    else:
        return "general"
