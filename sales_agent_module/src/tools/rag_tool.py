import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

def get_vector_store():
    """Get or create the vector store."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    database_path = os.path.join(base_dir, "database")
    case_studies_dir = os.path.join(base_dir, "data", "case_studies")
    embed_model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    embeddings = GoogleGenerativeAIEmbeddings(model=embed_model)
    
    if os.path.exists(database_path) and os.listdir(database_path):
        # Use the existing vector store
        vectorstore = Chroma(persist_directory=database_path, embedding_function=embeddings)
    else:
        # Load documents and create a new vector store
        loader = DirectoryLoader(case_studies_dir)
        docs = loader.load()
        vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=database_path)
    
    return vectorstore

def fetch_similar_case_study(description):
    """Fetch the most similar case study to the given description."""
    try:
        vectorstore = get_vector_store()
        vectorstore_retreiver = vectorstore.as_retriever(search_kwargs={"k": 1})
        docs = vectorstore_retreiver.invoke(description)
        if docs:
            return docs[0].page_content
    except Exception as e:
        pass

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    case_dir = os.path.join(base_dir, "data", "case_studies")
    try:
        files = [f for f in os.listdir(case_dir) if f.endswith(".md")]
        if files:
            with open(os.path.join(case_dir, files[0]), "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return "SmartOps AI empowers businesses to excel in digital presence and automated outreach."