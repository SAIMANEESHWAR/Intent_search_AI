import { useState } from 'react'
import { videoAPI } from '../services/api'
import ResultCard from './ResultCard'

const RAGSearch = () => {
  const [query, setQuery] = useState('')
  const [ragData, setRagData] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRAGSearch = async () => {
    if (!query.trim()) {
      alert('⚠️ Please enter a search query')
      return
    }

    setLoading(true)
    setRagData(null)

    try {
      const data = await videoAPI.ragSearch(query)
      setRagData(data)
    } catch (error) {
      console.error('RAG search error:', error)
      setRagData(null)
      alert('❌ Error: ' + (error.message || 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="section" style={{ background: 'linear-gradient(135deg, #e8f4f8 0%, #d1e7dd 100%)', borderColor: '#4a90e2' }}>
      <h2>🤖 RAG-Enhanced Search</h2>
      <p style={{ color: '#555', marginBottom: '15px' }}>
        Get AI-powered explanations, intelligent suggestions, and detailed summaries
      </p>
      <div className="input-group">
        <input
          id="rag-query-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !loading && handleRAGSearch()}
          placeholder="Enter query (e.g., 'hesitant reaction before answering')"
          disabled={loading}
        />
        <button className="btn btn-secondary" onClick={handleRAGSearch} disabled={loading}>
          {loading ? (
            <>
              <span className="loading"></span>
              <span>Searching with AI...</span>
            </>
          ) : (
            <>
              <span>✨</span>
              <span>RAG Search</span>
            </>
          )}
        </button>
      </div>
      <div className="results">
        {loading && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading" style={{ margin: '0 auto', borderTopColor: '#28a745' }}></div>
            <p style={{ marginTop: '20px', color: '#666' }}>Generating AI explanations...</p>
          </div>
        )}
        {ragData && (
          <>
            <div className="ai-explanation">
              <h4>💡 AI Explanation</h4>
              <p style={{ lineHeight: '1.6', marginBottom: '15px' }}>
                {ragData.explanation || 'No explanation available.'}
              </p>
              <h4>📊 Summary</h4>
              <p style={{ lineHeight: '1.6', marginBottom: '15px' }}>
                {ragData.summary || 'No summary available.'}
              </p>
              {ragData.suggestions && ragData.suggestions.length > 0 && (
                <>
                  <h4>💡 Suggested Queries</h4>
                  <div className="suggestions">
                    {ragData.suggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        className="suggestion-chip"
                        onClick={() => {
                          setQuery(suggestion)
                          // Auto-search when suggestion is clicked
                          setTimeout(() => {
                            handleRAGSearch()
                          }, 100)
                        }}
                      >
                        {suggestion}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
            {ragData.results && ragData.results.length > 0 ? (
              <>
                <h3 style={{ color: '#4a90e2', marginBottom: '15px' }}>
                  🎬 Found {ragData.count} matching video clips:
                </h3>
                {ragData.results.map((item, index) => (
                  <ResultCard key={index} item={item} index={index + 1} />
                ))}
              </>
            ) : (
              <div className="empty-state">
                <p>No matching video clips found. Try the suggested queries above or rephrase your search.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default RAGSearch

