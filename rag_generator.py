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
    """Generate query suggestions"""
    
    if not OPENAI_AVAILABLE or not client:
        # Fallback suggestions
        if not search_results:
            return [
                "Try a more general query",
                "Use different keywords",
                "Search for related concepts"
            ]
        else:
            return [
                f"Similar to '{query}' but more specific",
                f"Related emotional states",
                "Temporal variations (before/after)"
            ]
    
    if not search_results:
        # No results - suggest alternatives
        prompt = f"""User searched for: "{query}" but found no results.

Suggest 3 alternative search queries that might work better. Consider:
- More general terms
- Different emotional descriptors
- Synonyms

Return only the 3 suggestions, one per line."""
    else:
        # Has results - suggest related searches
        prompt = f"""User searched for: "{query}" and found relevant results.

Suggest 3 related queries that might also be interesting:
- Similar emotional states
- Related actions
- Temporal variations (before/after)

Return only the 3 suggestions, one per line."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a helpful search assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.8
        )
        suggestions = response.choices[0].message.content.strip().split("\n")
        # Clean up suggestions
        cleaned = [s.strip("- ").strip().strip('"').strip("'") for s in suggestions if s.strip()]
        return cleaned[:3] if cleaned else [
            "Try a more general query",
            "Use different keywords",
            "Search for related concepts"
        ]
    except Exception as e:
        print(f"⚠️ Error generating suggestions: {e}")
        return [
            "Try a more general query",
            "Use different keywords",
            "Search for related concepts"
        ]

def generate_summary(query, search_results):
    """Generate summary of all results"""
    
    if not search_results:
        return "No results found."
    
    time_range = f"{search_results[0]['start']:.1f}s to {search_results[-1]['end']:.1f}s"
    avg_score = sum(r['score'] for r in search_results) / len(search_results)
    
    return f"Found {len(search_results)} relevant moments ({time_range}) with average relevance of {avg_score:.0%}."
