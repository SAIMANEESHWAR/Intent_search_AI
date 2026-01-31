from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from semantic_search import search_frames
from intent_search import intent_search
from process_video import process_video_logic
from pydantic import BaseModel

# RAG imports
try:
    from rag_search import rag_search
    from vector_store import load_captions_to_vector_db, ensure_vector_db_loaded, search_vector_db
    from rag_generator import generate_suggestions_from_vector_db
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ RAG modules not available: {e}")
    RAG_AVAILABLE = False
    ensure_vector_db_loaded = None
    search_vector_db = None
    generate_suggestions_from_vector_db = None

class VideoRequest(BaseModel):
    url: str

app = FastAPI()


@app.on_event("startup")
def startup():
    """Keep RAG ready: if vector DB is empty but captions exist, load them."""
    if RAG_AVAILABLE and ensure_vector_db_loaded:
        ensure_vector_db_loaded()


from semantic_search import search_frames, load_data

# ... imports ...

# Global status
processing_status = {"state": "idle", "message": ""}

def update_status(msg):
    global processing_status
    if msg == "COMPLETED":
        print("🔄 processing complete. Reloading search index...")
        load_data()  # Reload embeddings (old method)
        # Also load to vector DB if RAG is available
        if RAG_AVAILABLE:
            try:
                load_captions_to_vector_db()
            except Exception as e:
                print(f"⚠️ Vector DB load failed: {e}")
        processing_status = {"state": "completed", "message": "Done! Search now."}
    elif msg.startswith("ERROR"):
        processing_status = {"state": "error", "message": msg}
    else:
        processing_status = {"state": "processing", "message": msg}

@app.post("/process-video")
def process_video_endpoint(req: VideoRequest, background_tasks: BackgroundTasks):
    global processing_status
    processing_status = {"state": "starting", "message": "Starting job..."}
    background_tasks.add_task(process_video_logic, req.url, update_status)
    return {"status": "started"}

@app.get("/process-status")
def get_status():
    return processing_status

# Mount current directory to serve video.mp4 (simple approach for dev)
app.mount("/videos", StaticFiles(directory="."), name="videos")
app.mount("/clips", StaticFiles(directory="clips"), name="clips")
app.mount("/frames", StaticFiles(directory="frames"), name="frames")

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://[::]:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Range", "Content-Range", "Accept-Ranges", "Content-Length"],
)

@app.post("/search")
def search(query: str):
    return search_frames(query)

@app.post("/intent-search")
def intent(query: str):
    return intent_search(query)

# RAG endpoints
if RAG_AVAILABLE:
    @app.post("/rag-suggestions")
    def rag_suggestions_endpoint(query: str):
        """Return suggestions with proper intent + emotion, grounded in vector DB captions."""
        vector_results = []
        if search_vector_db:
            # Lower threshold so we get related captions for suggestion context
            vector_results = search_vector_db(query, top_k=15, threshold=0.25)
        suggestions = generate_suggestions_from_vector_db(query, vector_results) if generate_suggestions_from_vector_db else []
        return {"query": query, "suggestions": suggestions}

    @app.post("/rag-search")
    def rag_search_endpoint(query: str):
        """RAG-enhanced search with explanations (run after user picks a suggestion)."""
        return rag_search(query)
