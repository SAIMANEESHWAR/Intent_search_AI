import { useState } from 'react'
import { videoAPI } from '../services/api'
import ResultCard from './ResultCard'

const RAGSearch = () => {
  const [query, setQuery] = useState('')
  const [preSuggestions, setPreSuggestions] = useState(null)
  const [ragData, setRagData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)

  // Step 1: Get better-sentence suggestions (before searching)
  const handleGetSuggestions = async () => {
    const q = query.trim()
    if (!q) {
      alert('⚠️ Please enter a search query')
      return
    }
    setLoadingSuggestions(true)
    setPreSuggestions(null)
    setRagData(null)
    try {
      const data = await videoAPI.getRAGSuggestions(q)
      setPreSuggestions(data.suggestions || [])
    } catch (error) {
      console.error('RAG suggestions error:', error)
      setPreSuggestions(null)
      alert('❌ Error: ' + (error.message || 'Unknown error'))
    } finally {
      setLoadingSuggestions(false)
    }
  }

  // Step 2: Run RAG search (after user picks a suggestion)
  const handleRAGSearch = async (chosenPrompt) => {
    const searchQuery = (chosenPrompt != null ? chosenPrompt : query).trim()
    if (!searchQuery) {
      alert('⚠️ Please enter or choose a search query')
      return
    }
    if (chosenPrompt != null) setQuery(chosenPrompt)
    setPreSuggestions(null)
    setLoading(true)
    setRagData(null)
    try {
      const data = await videoAPI.ragSearch(searchQuery)
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
    <div className="section">
      <h2>🤖 RAG-Enhanced Search</h2>
      <p className="text-muted">
        Step 1: Enter a query and get better prompts. Step 2: Choose a prompt to search for more accurate results.
      </p>
      <div className="input-group">
        <input
          id="rag-query-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !loadingSuggestions && !loading && handleGetSuggestions()}
          placeholder="Enter query (e.g., 'crowd celebrating after goal')"
          disabled={loadingSuggestions || loading}
        />
        <button className="btn btn-secondary" onClick={handleGetSuggestions} disabled={loadingSuggestions || loading}>
          {loadingSuggestions ? (
            <>
              <span className="loading"></span>
              <span>Getting better prompts...</span>
            </>
          ) : loading ? (
            <>
              <span className="loading"></span>
              <span>Searching...</span>
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
        {loadingSuggestions && (
          <div className="loading-block">
            <div className="loading"></div>
            <p>Getting better prompts for more accurate results...</p>
          </div>
        )}
        {preSuggestions && preSuggestions.length > 0 && !loading && (
          <div className="ai-explanation" style={{ marginBottom: '20px' }}>
            <h4>💡 Better prompts for more accurate results</h4>
            <p className="text-muted">
              Choose a prompt below — then we&apos;ll search the RAG model with it.
            </p>
            <div className="suggestions">
              {preSuggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="suggestion-chip"
                  onClick={() => handleRAGSearch(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
        )}
        {loading && (
          <div className="loading-block">
            <div className="loading"></div>
            <p>Searching with AI...</p>
          </div>
        )}
        {ragData && (
          <>
            <div className="ai-explanation">
              <h4>💡 AI Explanation</h4>
              <p className="text-muted" style={{ lineHeight: 1.6 }}>
                {ragData.explanation || 'No explanation available.'}
              </p>
              <h4>📊 Summary</h4>
              <p className="text-muted" style={{ lineHeight: 1.6 }}>
                {ragData.summary || 'No summary available.'}
              </p>
              {ragData.suggestions && ragData.suggestions.length > 0 && (
                <>
                  <h4>💡 Suggested prompts for best results</h4>
                  <p className="text-muted">
                    Click a prompt to search with it and get the best results.
                  </p>
                  <div className="suggestions">
                    {ragData.suggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        className="suggestion-chip"
                        onClick={() => handleRAGSearch(suggestion)}
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
                <h3>
                  🎬 Found {ragData.count} matching video clips:
                </h3>
                {ragData.results.map((item, index) => (
                  <ResultCard key={index} item={item} index={index + 1} />
                ))}
              </>
            ) : (
              <div className="empty-state">
                <p>No matching video clips found. Try one of the suggested prompts above for better results, or rephrase your search.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default RAGSearch

