export default function Footer() {
  const stack = [
    'FastAPI',
    'yt-dlp',
    'ffmpeg',
    'Vit-GPT2',
    'SBERT',
    'ChromaDB',
    'Ollama / OpenAI',
    'React',
  ]
  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div className="footer-stack">
          <span className="footer-stack-label">Stack:</span>
          <span className="footer-stack-list">
            {stack.join(' · ')}
          </span>
        </div>
        <div className="footer-meta">
          <p className="footer-copy">
            Paste a YouTube link to add a video. Search with phrases like “before the goal” or “crowd celebrating.” Get short clips and simple explanations.
          </p>
          <p className="footer-legal">
            © {new Date().getFullYear()} — Video search by natural language.
          </p>
        </div>
      </div>
    </footer>
  )
}
