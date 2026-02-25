import json
import os
from groq import Groq
from core.prompts import generate_prompt
from utils.pdf_utils import extract_text_from_pdf, generate_html , clean_policy_text
from utils.formatters import validate_rules_report
from core.rag_engine import create_vector_store, retrieve_relevant_context

def generate_policy_rules(relevant_context):
    """
    This function sends the retrieved policy context to the LLM (llama-3.3)
    to extract structured insurance rules and generate corresponding SQL queries.

    Args:
        relevant_context (str): The specific policy segments retrieved from the Vector DB.
    Returns:
        dict: A structured JSON object containing extracted rules, quotes, and SQL.
    """
    try:
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("Error: api_key.txt file not found.")
        return None

    client = Groq(api_key=api_key)
    prompt = generate_prompt(policy_text=relevant_context)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(completion.choices[0].message.content)


def run_agent(pdf_path):
    """
     Orchestrates the complete RAG-based analysis pipeline.
     Workflow:
        1. Extraction: Parses and cleans PDF text.
        2. RAG Indexing: Builds a local vector store from the text.
        3. Retrieval: Fetches contextually relevant policy excerpts.
        4. Generation: Extracts structured rules and SQL via LLM.
        5. Validation: Performs post-process verification of quotes/SQL.
        6. Export: Generates a final HTML report.
    """
    try:
        filename = os.path.basename(pdf_path)
        file_base_name, _ = os.path.splitext(filename)
        print(f"[*] Task started: Analyzing {file_base_name} with RAG")

        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text:
            return

        cleaned_text = clean_policy_text(raw_text)

        print("[*] RAG: Indexing policy text into Vector Store...")
        vector_db = create_vector_store(cleaned_text)


        print("[*] RAG: Retrieving relevant policy sections...")
        relevant_context = retrieve_relevant_context(vector_db)

        print("[*] AI Analysis: Processing retrieved context with llama-3.3...")
        results = generate_policy_rules(relevant_context)

        if not results or 'rules' not in results:
            print("[!] Error: AI analysis failed.")
            return

        print("[*] Validation: Verifying quotes and SQL integrity...")
        results = validate_rules_report(results, raw_text)

        output_filename = f"output_files/{file_base_name}.html"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(generate_html(results))

        print(f"[SUCCESS] RAG Pipeline complete. Report: {output_filename}")

    except Exception as e:
        print(f"[CRITICAL ERROR] Pipeline failed: {str(e)}")
