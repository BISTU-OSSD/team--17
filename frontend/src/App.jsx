import { useState } from 'react'
import SearchForm from './components/SearchForm'
import ResultCard from './components/ResultCard'
import RadarChart from './components/RadarChart'
import LanguagePie from './components/LanguagePie'
import Recommendations from './components/Recommendations'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const LOADING_STEPS = [
  'Connecting to GitHub API...',
  'Fetching repository data...',
  'Analyzing health metrics...',
  'Finding similar repositories...',
  'Generating report...',
]

export default function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState(null)

  const handleAnalyze = async (repoName) => {
    setQuery(repoName)
    setError(null)
    setResult(null)
    setLoading(true)
    setLoadingStep(0)

    // Animate loading steps
    const stepTimer = setInterval(() => {
      setLoadingStep((prev) => Math.min(prev + 1, LOADING_STEPS.length - 1))
    }, 1200)

    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_full_name: repoName }),
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error: ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      clearInterval(stepTimer)
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>DevSkillMapper</h1>
        <p className="subtitle">给开源仓库做体检，帮你找到值得参与的好项目</p>
      </header>

      <SearchForm onAnalyze={handleAnalyze} loading={loading} />

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-step">{LOADING_STEPS[loadingStep]}</p>
        </div>
      )}

      {error && (
        <div className="error-card">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="results-container">
          <ResultCard data={result} />

          {result.health_scores && (
            <RadarChart scores={result.health_scores} grade={result.overall_grade} />
          )}

          {result.languages && Object.keys(result.languages).length > 0 && (
            <LanguagePie languages={result.languages} />
          )}

          {result.recommendations && result.recommendations.length > 0 && (
            <Recommendations items={result.recommendations} onSelect={handleAnalyze} />
          )}
        </div>
      )}

      <footer className="app-footer">
        <p>BISTU-OSSD team-17 &middot; MIT License</p>
      </footer>
    </div>
  )
}
