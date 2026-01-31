const ResultCard = ({ item, index }) => {
  return (
    <div className="result-card">
      <div className="result-header">
        <div className="result-info">
          <h3>Match {index}</h3>
          <p className="text-muted" style={{ marginBottom: '10px' }}>{item.caption}</p>
          <div>
            <span className="badge badge-score">
              Match: {item.score.toFixed(2)}
            </span>
            <span className="badge badge-intent">
              When: {item.intent}
            </span>
            <span className="badge badge-time">
              {item.start.toFixed(1)}s - {item.end.toFixed(1)}s
            </span>
          </div>
        </div>
      </div>
      <div className="media-container">
        <div className="frame-preview">
          <img
            src={`http://localhost:8000/frames/${item.best_frame}`}
            alt="Frame preview"
            onError={(e) => (e.target.style.display = 'none')}
          />
        </div>
        <div>
          <video controls preload="metadata">
            <source src={item.video_url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      </div>
      <a
        href={item.full_video_url}
        target="_blank"
        rel="noopener noreferrer"
        className="link-btn"
      >
        {item.is_youtube === false ? '🔗 View full clip' : '🔗 Open in YouTube'}
      </a>
    </div>
  )
}

export default ResultCard

