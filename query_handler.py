import requests

def format_prompt(query, relevant_chunks, max_chunks=3):
    # Combine only top N chunks to avoid long prompt
    context = "\n".join(relevant_chunks[:max_chunks])
    return f"""
You are a policy assistant. Based on the following document:

{context}

Evaluate the following query:
"{query}"

Return your decision in JSON with:
- decision: "Approved" or "Rejected"
- amount: estimated coverage if any
- justification: explanation with clause references
"""

def ask_llm(prompt, model="gemma:2b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False  # set True if streaming is needed
            },
            timeout=60  # Optional timeout to prevent hanging
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"LLM Error: {e}"