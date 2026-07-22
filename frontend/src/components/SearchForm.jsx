import { useState } from 'react'

export default function SearchForm({ onAnalyze, loading }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const val = input.trim()
    if (val && !loading) {
      onAnalyze(val)
    }
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        className="search-input"
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="输入仓库名，如 facebook/react"
        disabled={loading}
      />
      <button className="search-btn" type="submit" disabled={loading}>
        {loading ? '分析中...' : '分析'}
      </button>
    </form>
  )
}
