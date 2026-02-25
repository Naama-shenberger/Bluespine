from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_vector_store(text):
    """
        Builds a local RAG search index from text.
        Operations:
        1. Chunking: Splits text into overlapping segments via RecursiveCharacterTextSplitter.
        2. Embedding: Generates vectors locally using HuggingFace ('all-MiniLM-L6-v2').
        3. Indexing: Stores data in a FAISS vector DB for semantic retrieval.

        Args:
            text (str): Input text from policy documents.
        Returns:
            FAISS: Searchable vector database.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_text(text)
    print("[*] Loading local HuggingFace embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_texts(chunks, embeddings)
    print("[+] Vector store created successfully!")
    return vector_db


def retrieve_relevant_context(vector_db, query="billing rules and medical policy restrictions"):
    """
        Retrieves and aggregates top-k relevant segments from the vector DB.

        1. Search: Finds the most semantically similar chunks based on the query.
        2. Join: Concatenates retrieved segments into a single context string for the LLM.

        Args:
            vector_db (FAISS): Indexed policy database.
            query (str): The specific topic or rule to search for.
        Returns:
            str: Combined context for model reasoning.
    """
    docs = vector_db.similarity_search(query, k=5)
    return "\n---\n".join([doc.page_content for doc in docs])