import { useState } from 'react'
import { productionAPI } from '../services/api'
import BudgetDashboard from './BudgetDashboard'
import SceneBreakdown from './SceneBreakdown'
import RiskDashboard from './RiskDashboard'
import ShootingSchedule from './ShootingSchedule'

const TABS = [
  { id: 'budget', label: 'Budget', icon: '💰' },
  { id: 'scenes', label: 'Scene Breakdown', icon: '🎬' },
  { id: 'schedule', label: 'Shooting Schedule', icon: '📅' },
  { id: 'risk', label: 'Risk Analyzer', icon: '⚠️' }
]

const newActor = (name = '', fromScript = false) => ({
  id: crypto.randomUUID?.() ?? Date.now(),
  name: (typeof name === 'string' ? name : '').trim(),
  daily_rate: '',
  available_days: '',
  fromScript: !!fromScript
})

const ProductionPlanner = () => {
  const [script, setScript] = useState('')
  const [budget, setBudget] = useState('')
  const [actors, setActors] = useState([])
  const [fetching, setFetching] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('budget')

  const handleFetchCharacters = async () => {
    if (!script.trim()) {
      setError('Enter a script first')
      return
    }
    setFetching(true)
    setError('')
    try {
      const data = await productionAPI.extractActors(script)
      if (data.error) {
        setError(data.error)
      } else {
        const names = data.actor_names || []
        setActors(names.length ? names.map(name => newActor(name, true)) : [])
      }
    } catch (err) {
      const msg = err.response?.data?.detail
        ? (Array.isArray(err.response.data.detail) ? err.response.data.detail.map(d => d.msg || JSON.stringify(d)).join(', ') : String(err.response.data.detail))
        : err.response?.data?.error || err.message || 'Failed to fetch characters. Check backend is running and GROQ_API_KEY is set.'
      setError(msg)
    } finally {
      setFetching(false)
    }
  }

  const addCustomActor = () => {
    setActors(prev => [...prev, newActor('', false)])
  }

  const removeActor = (id) => {
    setActors(prev => prev.filter(a => a.id !== id))
  }

  const updateActor = (id, field, value) => {
    setActors(prev => prev.map(a => (a.id === id ? { ...a, [field]: value } : a)))
  }

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

    const actorsPayload = actors
      .map(a => ({
        name: (a.name || '').trim(),
        daily_rate: parseFloat(a.daily_rate),
        available_days: parseInt(a.available_days, 10)
      }))
      .filter(
        a =>
          a.name &&
          !Number.isNaN(a.daily_rate) &&
          a.daily_rate >= 0 &&
          !Number.isNaN(a.available_days) &&
          a.available_days > 0
      )

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await productionAPI.generatePlan(script, budgetNum, actorsPayload)

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

  if (result) {
    return (
      <section id="production-planner" className="section enhanced-planner-section">
        <div className="planner-header">
          <h2 className="planner-result-title">📋 Production Plan</h2>
          <button type="button" onClick={handleNewPlan} className="btn-new-plan">
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
        {activeTab === 'schedule' && <ShootingSchedule data={result} />}
        {activeTab === 'risk' && <RiskDashboard data={result} />}
      </section>
    )
  }

  return (
    <section id="production-planner" className="section enhanced-planner-section">
      <form onSubmit={handleSubmit} className="enhanced-form">
        <div className="form-group">
          <label className="form-label">Script Text</label>
          <textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            placeholder="Paste your movie script here..."
            disabled={loading}
            className="form-textarea"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Total Budget (₹)</label>
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

        <div className="form-group">
          <label className="form-label">Characters (Groq API)</label>
          <p className="form-hint" style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Script is sent to Groq API to extract character names. Then enter remuneration (₹/day) and available days for each character.
          </p>
          <button
            type="button"
            onClick={handleFetchCharacters}
            disabled={loading || fetching || !script.trim()}
            className="btn btn-secondary"
            style={{ marginBottom: '8px' }}
          >
            {fetching ? (
              <>
                <span className="loading" style={{ marginRight: '8px' }} />
                Fetching characters… (10–20 sec)
              </>
            ) : (
              '📜 Fetch characters from script'
            )}
          </button>

          {actors.length > 0 && (
            <>
              <p style={{ fontSize: '14px', color: 'var(--primary)', fontWeight: 600, marginBottom: '12px' }}>
                Found {actors.length} character{actors.length !== 1 ? 's' : ''} from script. Enter remuneration (₹) and available days for each.
              </p>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 140px 90px auto',
                  gap: '8px',
                  alignItems: 'center',
                  marginBottom: '6px',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                  fontWeight: 600
                }}
              >
                <span>Character</span>
                <span>Remuneration (₹/day)</span>
                <span>Days</span>
                <span />
              </div>
              {actors.map((actor) => (
                <div
                  key={actor.id}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 140px 90px auto',
                    gap: '8px',
                    alignItems: 'center',
                    marginBottom: '8px'
                  }}
                >
                  {actor.fromScript ? (
                    <span
                      style={{
                        padding: '10px 12px',
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 'var(--radius)',
                        color: 'var(--text)',
                        fontWeight: 500
                      }}
                      title="Character from script (Groq API)"
                    >
                      {actor.name}
                    </span>
                  ) : (
                    <input
                      type="text"
                      value={actor.name}
                      onChange={(e) => updateActor(actor.id, 'name', e.target.value)}
                      placeholder="Custom character name"
                      disabled={loading}
                      className="form-input"
                    />
                  )}
                  <input
                    type="number"
                    value={actor.daily_rate}
                    onChange={(e) => updateActor(actor.id, 'daily_rate', e.target.value)}
                    placeholder="₹ per day"
                    disabled={loading}
                    min="0"
                    step="1000"
                    className="form-input"
                  />
                  <input
                    type="number"
                    value={actor.available_days}
                    onChange={(e) => updateActor(actor.id, 'available_days', e.target.value)}
                    placeholder="Days"
                    disabled={loading}
                    min="1"
                    step="1"
                    className="form-input"
                  />
                  <button
                    type="button"
                    onClick={() => removeActor(actor.id)}
                    disabled={loading}
                    className="btn btn-secondary"
                    style={{ padding: '8px 12px' }}
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button type="button" onClick={addCustomActor} disabled={loading} className="btn btn-secondary" style={{ marginTop: '4px' }}>
                + Add custom character
              </button>
            </>
          )}
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading || actors.length === 0}>
          {loading ? (
            <>
              <span className="loading" />
              <span>Generating Plan… (30–90 sec)</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Generate Production Plan</span>
            </>
          )}
        </button>
        <p className="form-hint" style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
          Fetch characters first, fill remuneration and days, then generate. Full plan uses AI and can take 30–90 seconds.
        </p>
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
