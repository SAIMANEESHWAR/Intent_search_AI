# rag_search.py
from vector_store import search_vector_db
from rag_generator import generate_explanation, generate_suggestions, generate_summary
from video_utils import ensure_clip, _get_source_video_for_frame
import json
import os

def get_video_config():
    try:
        with open("video_config.json", "r") as f:
            return json.load(f)
    except:
        return {}

def get_full_video_url(best_frame: str, start: float):
    """Return URL for 'full video' - YouTube link or source clip depending on mode."""
    config = get_video_config()
    mode = config.get("mode", "youtube")
    if mode == "clips":
        source_path, _ = _get_source_video_for_frame(best_frame)
        if source_path and os.path.exists(source_path):
            # Use actual filename (could be .mp4, .mov, etc.)
            basename = os.path.basename(source_path)
            return f"http://localhost:8000/source_clips/{basename}"
    # YouTube mode
    url = config.get("url", "https://www.youtube.com/watch?v=zhEWqfP6V_w")
    return f"{url}&t={int(start)}s"

def rag_search(query: str):
    """RAG-enhanced search with explanations"""
    
    # Step 1: Retrieve (using vector DB)
    search_results = search_vector_db(query, top_k=10, threshold=0.4)
    
    # Step 2: Apply temporal intent (reuse existing logic)
    intent_results = []
    if search_results:
        # Detect intent
        q_lower = query.lower()
        if "before" in q_lower:
            intent = "before"
        elif "after" in q_lower:
            intent = "after"
        else:
            intent = "during"
        
        # Clean query
        clean_query = query.lower()
        for w in ["before", "after", "during"]:
            clean_query = clean_query.replace(w, "")
        clean_query = clean_query.strip()
        
        # Apply temporal adjustments
        WINDOW = 5
        for r in search_results:
            ts = r["start"]
            end_ts = r["end"]
            
            if intent == "before":
                adj_start = max(ts - WINDOW, 0)
                adj_end = ts
            elif intent == "after":
                adj_start = end_ts
                adj_end = end_ts + WINDOW
            else:
                adj_start = ts
                adj_end = end_ts
            
            # Ensure minimum duration
            if adj_end - adj_start < 3.0:
                diff = 3.0 - (adj_end - adj_start)
                adj_start = max(0, adj_start - diff / 2)
                adj_end = adj_end + diff / 2
            
            clip_filename = ensure_clip(adj_start, adj_end, r["best_frame"])
            full_url = get_full_video_url(r["best_frame"], adj_start)
            intent_results.append({
                "best_frame": r["best_frame"],
                "caption": r["caption"],
                "intent": intent,
                "original_start": ts,
                "original_end": end_ts,
                "start": adj_start,
                "end": adj_end,
                "score": r["score"],
                "video_url": f"http://localhost:8000/clips/{clip_filename}",
                "full_video_url": full_url,
                "is_youtube": get_video_config().get("mode", "youtube") != "clips"
            })
    
    # Step 3: Generate explanations (RAG)
    explanation = generate_explanation(query, search_results)
    suggestions = generate_suggestions(query, search_results)
    summary = generate_summary(query, search_results)
    
    # Step 4: Return enhanced results
    return {
        "query": query,
        "results": intent_results,
        "explanation": explanation,
        "suggestions": suggestions,
        "summary": summary,
        "count": len(intent_results)
    }

