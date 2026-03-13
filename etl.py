import os
from database import SessionLocal
from models import SystemMetric, SOCAlert, ERPReport
from vector_db import get_collection
from langchain_openai import OpenAIEmbeddings

# Since the user hasn't provided an OpenAI Key yet, 
# we'll build the ingestion code but use a try-catch for the embeddings to prevent crashing.
try:
    embeddings = OpenAIEmbeddings()
except Exception as e:
    print(f"Warning: OpenAI API Key might not be set. {e}")
    embeddings = None

def run_etl_pipeline():
    """Extracts data from MySQL, transforms into text, and loads into ChromaDB."""
    db = SessionLocal()
    collection = get_collection("cio_knowledge_base")
    
    docs = []
    metadatas = []
    ids = []
    
    # Extract System Metrics
    metrics = db.query(SystemMetric).all()
    for m in metrics:
        text = f"System Metric: The component '{m.component}' showed a '{m.metric_name}' of {m.metric_value} at {m.timestamp}."
        docs.append(text)
        metadatas.append({"source": "metrics", "component": m.component})
        ids.append(f"metric_{m.id}")

    # Extract SOC Alerts
    alerts = db.query(SOCAlert).all()
    for a in alerts:
        text = f"SOC Alert ({a.severity} Severity): The system '{a.affected_system}' experienced an alert '{a.alert_type}' at {a.timestamp}. Description: {a.description}"
        docs.append(text)
        metadatas.append({"source": "soc", "severity": a.severity, "system": a.affected_system})
        ids.append(f"soc_alert_{a.id}")

    # Extract ERP Reports
    reports = db.query(ERPReport).all()
    for r in reports:
        text = f"ERP Report for module '{r.module}' (Status: {r.status}) recorded at {r.timestamp}. Impact: {r.impact_description}"
        docs.append(text)
        metadatas.append({"source": "erp", "module": r.module, "status": r.status})
        ids.append(f"erp_report_{r.id}")

    # Load into Vector DB
    if docs and embeddings is not None:
        try:
            # Note: in a production setting we'd batch this.
            # Using langhchain embeddings directly might require some extraction or we just let ChromaDB use its default sentence transformer
            # Actually, ChromaDB will automatically use its baked-in sentence transformer if we don't supply an embedding function to the collection.
            # Let's just pass the documents to the collection.
            collection.upsert(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully loaded {len(docs)} documents into the vector database.")
        except Exception as e:
            print(f"Error saving to Vector DB: {e}")
    else:
        # Fallback if OpenAI embeddings fail or aren't used: let ChromaDB use built-in mini-LM (happens by default)
        try:
            collection.upsert(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully loaded {len(docs)} documents into the vector database using default ChromaDB embeddings.")
        except Exception as e:
            print(f"Error saving to Vector DB with default embeddings: {e}")
            
    db.close()

if __name__ == "__main__":
    print("Running ETL Pipeline...")
    run_etl_pipeline()
