import VideoLoader from './components/VideoLoader'
import BasicSearch from './components/BasicSearch'
import RAGSearch from './components/RAGSearch'
import './App.css'

function App() {
  return (
    <div className="container">
      <div className="header">
        <h1>🎬 Semantic Video Search</h1>
        <p>AI-Powered Intent-Based Video Search Engine</p>
      </div>

      <div className="content">
        <VideoLoader />
        <BasicSearch />
        <RAGSearch />
      </div>
    </div>
  )
}

export default App

