"""Groq-powered grounded answer generation."""

from __future__ import annotations

import re

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, MAX_ANSWER_TOKENS

SYSTEM_PROMPT = """You are a precise, citation-driven knowledge assistant.

Rules you must ALWAYS follow:
1. Answer ONLY using the numbered source snippets provided in the context.
2. Every factual claim must end with its citation in brackets, e.g., [1] or [2].
3. If the answer is not present in the provided sources, respond EXACTLY with:
"I could not find relevant information in the indexed data."
4. Do NOT use any external knowledge, assumptions, or general world knowledge.
5. If sources contradict each other, present both perspectives and note the conflict.
6. Be concise and clear. Use bullet points for lists.
"""


def generate_answer(context: dict) -> dict:
    """Send grounded context to Groq and return the answer with sources."""

    if not GROQ_API_KEY:
        return {
            "answer": "Error generating answer: GROQ_API_KEY is not set.",
            "sources": context.get("sources", []),
            "query": context.get("query", ""),
        }

    try:
        # Create the Groq client once per call using the API key loaded from the environment.
        client = Groq(api_key=GROQ_API_KEY)

        # Put the user's question and formatted source snippets into a single grounded user message.
        user_message = f"Question: {context['query']}\n\nSources:\n{context['context_text']}"

        # Ask the Groq chat completion model to answer using only the supplied sources and system prompt.
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=MAX_ANSWER_TOKENS,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        # Pull the generated text from the first returned choice.
        response_text = (response.choices[0].message.content or "").strip()

        # If the model returns an uncited answer, fall back to the required safe response instead of guessing.
        if response_text and not re.search(r"\[\d+\]", response_text):
            response_text = "I could not find relevant information in the indexed data."

        return {
            "answer": response_text or "I could not find relevant information in the indexed data.",
            "sources": context["sources"],
            "query": context["query"],
        }
    except Exception as exc:
        # Return the error inside the response payload so the frontend can display it cleanly.
        return {
            "answer": f"Error generating answer: {exc}",
            "sources": context.get("sources", []),
            "query": context.get("query", ""),
        }
