# Using ChatGroq below instead of ChatOpenAI
# Force reload to pick up the new .env file
from langchain_core.prompts import PromptTemplate
from vector_db import get_collection
from database import SessionLocal
from risk_scoring import get_current_business_health
import os

from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

# Load all environment variables explicitly overriding any stale shell vars
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

# Setup the free Google Gemini LLM
try:
    # Requires GOOGLE_API_KEY environment variable. 
    # Get a free one at: https://aistudio.google.com/app/apikey
    # We load it directly from os.environ now to ensure it works even if shell vars drop.
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.2,
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )
except Exception as e:
    print(f"Warning: Gemini configured incorrectly or missing key. Error: {e}")
    llm = None

collection = get_collection("cio_knowledge_base")

def get_rag_context(query: str, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    if "documents" in results and results["documents"]:
        return " ".join(results["documents"][0])
    return "No relevant context found in Vector DB."

def generate_ai_response(query: str):
    # 1. Retrieve specific context from Vector DB
    rag_context = get_rag_context(query)
    
    # 2. Extract Business Health Context
    db = SessionLocal()
    health = get_current_business_health(db)
    db.close()
    
    current_health_context = (
        f"Overall System Risk Score: {health['risk_score']}/100 ({health['risk_level']}). "
        f"Recent Anomalies Detected: {', '.join(health['anomalies_detected']) if health['anomalies_detected'] else 'None'}."
    )

    # 3. Build the prompt
    prompt_template = """
You are the "Conversational CIO", an AI executive assistant that helps the CIO, CTO, and business executives understand the technical health of the enterprise and its impact on business operations.

CURRENT SYSTEM HEALTH:
{health_context}

RETRIEVED TECHNICAL DATA (RAG Context):
{rag_context}

USER QUERY: {query}

Instructions:
1. Provide a concise, executive-level summary answering the user query.
2. Translate any technical failures directly to their business impact (e.g., how a database lag affects shipments or revenue).
3. If applicable, recommend specific technical or strategic actions to mitigate risks.
4. Keep the tone professional, authoritative, and direct.

Response:
"""
    
    prompt = PromptTemplate(
        input_variables=["health_context", "rag_context", "query"],
        template=prompt_template
    )

    if llm:
        chain = prompt | llm
        try:
            response = chain.invoke({
                "health_context": current_health_context,
                "rag_context": rag_context,
                "query": query
            })
            return response.content
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return (
                    f"**[API Quota Exceeded]**\n\n"
                    f"I've retrieved the context for your query: '{query}', but my AI capability is currently rate-limited (Google Gemini Free Tier).\n\n"
                    f"**System Status:** Risk is {health['risk_level']} ({health['risk_score']}%).\n"
                    f"**Recent Anomalies:** {health['anomalies_detected']}\n\n"
                    f"**Technical Context:**\n{rag_context}"
                )
            return f"Error connecting to AI Provider. Did you set GOOGLE_API_KEY? Error: {e}"
    else:
        # Fallback for hackathon testing if NO API KEY
        return (
            f"[FALLBACK LOGIC - NO GOOGLE_API_KEY FOUND]\n"
            f"I see you asked about: '{query}'.\n"
            f"Current Risk is {health['risk_level']} ({health['risk_score']}%).\n"
            f"Found Context: {rag_context}\n"
            f"Anomalies: {health['anomalies_detected']}\n"
            f"Recommendation: Please provide a GOOGLE_API_KEY to generate deep strategic insights."
        )
