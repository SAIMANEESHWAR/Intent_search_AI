# rag_generator.py
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import OpenAI, but handle gracefully if not available
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        OPENAI_AVAILABLE = True
    else:
        print("⚠️ OPENAI_API_KEY not found in .env file")
        OPENAI_AVAILABLE = False
        client = None
except ImportError:
    print("⚠️ OpenAI package not installed. Install with: pip install openai")
    OPENAI_AVAILABLE = False
    client = None
except Exception as e:
    print(f"⚠️ OpenAI client initialization failed: {e}")
    OPENAI_AVAILABLE = False
    client = None

def generate_explanation(query, search_results):
    """Generate natural language explanation of search results"""
    
    if not search_results:
        return "No matching moments found. Try rephrasing your query or using different keywords."
    
    if not OPENAI_AVAILABLE or not client:
        # Fallback explanation without LLM
        if search_results:
            return f"Found {len(search_results)} matching moments. Top result: '{search_results[0]['caption']}' at {search_results[0]['start']:.1f}s with {search_results[0]['score']:.0%} relevance."
        return "No results found."
    
    # Build context from results
    context_parts = []
    for i, result in enumerate(search_results[:5], 1):
        context_parts.append(
            f"{i}. At {result['start']:.1f}s-{result['end']:.1f}s: "
            f"'{result['caption']}' (relevance: {result['score']:.0%})"
        )
    
    context = "\n".join(context_parts)
    
    # Create prompt
    prompt = f"""You are a helpful video search assistant. A user searched for: "{query}"

Found {len(search_results)} matching video moments:
{context}

Provide a concise, friendly explanation (2-3 sentences) that:
1. Confirms what was found
2. Highlights why the top result matches the query
3. Mentions the relevance score

Be conversational and helpful."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a helpful video search assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Error generating explanation: {e}")
        # Fallback
        if search_results:
            return f"Found {len(search_results)} matching moments. Top result: '{search_results[0]['caption']}' at {search_results[0]['start']:.1f}s."
        return "No results found."

def generate_suggestions(query, search_results):
    """Generate suggestion prompts that will give the best search results.
    Returns 3 concrete search queries (not generic advice) the user can click to search."""
    
    # Fallback: actual search-query style strings (clickable prompts)
    fallback_no_results = [
        "goal celebration moment",
        "crowd cheering",
        "players celebrating after score"
    ]
    fallback_with_results = [
        f"{query}",
        "before the goal",
        "after the goal"
    ]

    if not OPENAI_AVAILABLE or not client:
        return fallback_no_results if not search_results else fallback_with_results[:3]

    if not search_results:
        prompt = f"""User searched for: "{query}" but found no video moments.

Suggest exactly 3 alternative SEARCH QUERIES that would give the best results in a video search. Each suggestion must be a short, ready-to-use search phrase (e.g. "crowd celebrating after goal", "players cheering", "fans celebrating"). Use:
- More general or more specific wording
- Synonyms and related actions
- Temporal phrases like "before the goal" or "after the score"

Return ONLY the 3 search phrases, one per line. No numbers, bullets, or explanations."""
    else:
        # Use caption context so suggestions match video vocabulary
        caption_samples = [r["caption"] for r in search_results[:5]]
        context = "\n".join(f"- {c}" for c in caption_samples)
        prompt = f"""User searched for: "{query}" and found matching video moments. Sample captions from the video:
{context}

Suggest exactly 3 SEARCH QUERIES that would give the BEST results for this video. Base them on the user query and the caption style above (same vocabulary, actions, scenes). Each suggestion must be a short, ready-to-use search phrase. Include variations like "before X", "after X" if relevant.

Return ONLY the 3 search phrases, one per line. No numbers, bullets, or explanations."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You suggest concrete video search queries that get the best results. Output only the 3 search phrases, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.7
        )
        raw = response.choices[0].message.content.strip()
        suggestions = raw.split("\n")
        cleaned = [s.strip("- ").strip().strip('"').strip("'").strip() for s in suggestions if s.strip()]
        # Remove leading numbers (e.g. "1. query" -> "query")
        cleaned = [s.lstrip("0123456789.").strip() for s in cleaned]
        return cleaned[:3] if cleaned else (fallback_no_results if not search_results else fallback_with_results[:3])
    except Exception as e:
        print(f"⚠️ Error generating suggestions: {e}")
        return fallback_no_results if not search_results else fallback_with_results[:3]

def generate_suggestions_from_vector_db(query, vector_db_results):
    """Suggest search phrases with proper intent + emotion, grounded in vector DB captions.
    vector_db_results: list of dicts with 'caption', optionally 'start', 'end', 'score'."""
    fallback = [
        "goal celebration moment",
        "crowd cheering after goal",
        "players celebrating"
    ]
    if not vector_db_results:
        return generate_suggestions(query, [])

    caption_lines = []
    for i, r in enumerate(vector_db_results[:12], 1):
        cap = r.get("caption", "")
        if cap:
            caption_lines.append(f"  {i}. {cap}")

    context = "\n".join(caption_lines) if caption_lines else "(no captions)"

    if not OPENAI_AVAILABLE or not client:
        captions = [r.get("caption", "") for r in vector_db_results[:5] if r.get("caption")]
        if captions:
            return [captions[0][:50], "before the goal", "after the goal"][:3]
        return fallback

    prompt = f"""You are a video search assistant. The user typed: "{query}"

Below are REAL captions from the video (from the vector DB). Use them to suggest 3 search queries that will get the best results.

Captions from the video:
{context}

Rules for the 3 suggestions:
1. **Intent**: Use clear temporal intent where it fits — "before the goal", "after the score", "during the celebration", "moment before X", "reaction after X".
2. **Emotion / action**: Include emotion or action (celebrating, cheering, tense, excited, running, scoring) so the query matches how moments are described.
3. **Vocabulary**: Use words and phrases that appear in the captions above so the search will match.

Return ONLY 3 short search phrases, one per line. No numbers, bullets, or explanations."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You suggest video search queries with clear intent (before/after/during) and emotion, based on real video captions. Output only 3 search phrases, one per line."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.6
        )
        raw = response.choices[0].message.content.strip()
        suggestions = raw.split("\n")
        cleaned = [s.strip("- ").strip().strip('"').strip("'").strip() for s in suggestions if s.strip()]
        cleaned = [s.lstrip("0123456789.").strip() for s in cleaned]
        return cleaned[:3] if cleaned else fallback
    except Exception as e:
        print(f"⚠️ Error generating suggestions from vector DB: {e}")
        return fallback


def generate_summary(query, search_results):
    """Generate summary of all results"""
    
    if not search_results:
        return "No results found."
    
    time_range = f"{search_results[0]['start']:.1f}s to {search_results[-1]['end']:.1f}s"
    avg_score = sum(r['score'] for r in search_results) / len(search_results)
    
    return f"Found {len(search_results)} relevant moments ({time_range}) with average relevance of {avg_score:.0%}."
