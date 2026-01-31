import { useState } from 'react'
import { videoAPI } from '../services/api'
import ResultCard from './ResultCard'

const BasicSearch = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('⚠️ Please enter a search query')
      return
    }

    setLoading(true)
    setResults([])

    try {
      const data = await videoAPI.basicSearch(query)
      setResults(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
      alert('❌ Error connecting to backend: ' + (error.message || 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="section">
      <h2>🔍 Basic Search</h2>
      <div className="input-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !loading && handleSearch()}
          placeholder="Enter search query (e.g., 'before crowd celebrating')"
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
          {loading ? (
            <>
              <span className="loading"></span>
              <span>Searching...</span>
            </>
          ) : (
            <>
              <span>🔎</span>
              <span>Search</span>
            </>
          )}
        </button>
      </div>
      <div className="results">
        {loading && (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading" style={{ margin: '0 auto', borderTopColor: '#667eea' }}></div>
            <p style={{ marginTop: '20px', color: '#666' }}>Searching...</p>
          </div>
        )}
        {!loading && results.length === 0 && query && (
          <div className="empty-state">
            <p>No results found. Try a different query.</p>
          </div>
        )}
        {!loading && results.map((item, index) => (
          <ResultCard key={index} item={item} index={index + 1} />
        ))}
      </div>
    </div>
  )
}

export default BasicSearch

