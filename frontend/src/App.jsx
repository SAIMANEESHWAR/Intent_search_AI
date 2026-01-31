import VideoLoader from './components/VideoLoader'
import BasicSearch from './components/BasicSearch'
import RAGSearch from './components/RAGSearch'
import './App.css'

function App() {
  return (
    <div className="container">
      <header className="header">
        <h1>Semantic Video Search</h1>
        <p>Find any moment in a video with natural language — intent, emotion, and RAG-powered suggestions</p>
      </header>
      <main className="content">
        <VideoLoader />
        <BasicSearch />
        <RAGSearch />
      </main>
    </div>
  )
}

export default App
