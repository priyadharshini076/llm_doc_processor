import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def ask_llm(prompt, model="gpt-4o-mini"):  # or "gpt-3.5-turbo"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers policy-related queries from documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=700
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"
