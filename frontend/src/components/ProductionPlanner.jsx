import { useState } from 'react'
import { productionAPI } from '../services/api'
import BudgetDashboard from './BudgetDashboard'
import SceneBreakdown from './SceneBreakdown'
import RiskDashboard from './RiskDashboard'

const TABS = [
  { id: 'budget', label: 'Budget', icon: '💰' },
  { id: 'scenes', label: 'Scene Breakdown', icon: '🎬' },
  { id: 'risk', label: 'Risk Analyzer', icon: '⚠️' }
]

const ProductionPlanner = () => {
  const [script, setScript] = useState('')
  const [budget, setBudget] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('budget')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!script.trim()) {
      setError('Please enter a script')
      return
    }
    
    const budgetNum = parseFloat(budget)
    if (!budgetNum || budgetNum <= 0) {
      setError('Please enter a valid budget amount')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await productionAPI.generatePlan(script, budgetNum)
      
      if (data.error) {
        setError(data.error)
      } else {
        setResult(data)
        setActiveTab('budget')
      }
    } catch (err) {
      setError(err.message || 'Failed to generate production plan')
    } finally {
      setLoading(false)
    }
  }

  const handleNewPlan = () => {
    setResult(null)
    setError('')
    setActiveTab('budget')
  }

  // After result: show only tabs + content, no form
  if (result) {
    return (
      <section id="production-planner" className="section enhanced-planner-section">
        <div className="planner-header">
          <h2 className="planner-result-title">📋 Production Plan</h2>
          <button
            type="button"
            onClick={handleNewPlan}
            className="btn-new-plan"
          >
            ← New plan
          </button>
        </div>

        <div className="planner-tabs">
          {TABS.map(({ id, label, icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={`planner-tab ${activeTab === id ? 'active' : ''}`}
            >
              {icon} {label}
            </button>
          ))}
        </div>

        {activeTab === 'budget' && <BudgetDashboard data={result} />}
        {activeTab === 'scenes' && <SceneBreakdown data={result} />}
        {activeTab === 'risk' && <RiskDashboard data={result} />}
      </section>
    )
  }

  // No result: show form
  return (
    <section id="production-planner" className="section enhanced-planner-section">
      <form onSubmit={handleSubmit} className="enhanced-form">
        <div className="form-group">
          <label className="form-label">
            Script Text
          </label>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Paste your movie script here..."
            disabled={loading}
            className="form-textarea"
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Total Budget (₹)
          </label>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            placeholder="Enter total budget in ₹"
            disabled={loading}
            min="0"
            step="1000"
            className="form-input"
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="loading"></span>
              <span>Generating Plan...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Generate Production Plan</span>
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="status error" style={{ marginTop: '16px' }}>
          <span>❌</span>
          <span>{error}</span>
        </div>
      )}
    </section>
  )
}

export default ProductionPlanner

