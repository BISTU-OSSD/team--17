export default function Recommendations({ items, onSelect }) {
  return (
    <div className="card">
      <h2>相似仓库推荐</h2>
      <div className="recommendation-list">
        {items.map((repo) => (
          <div
            key={repo.full_name}
            className="recommendation-item"
            onClick={() => onSelect(repo.full_name)}
            title="点击分析此仓库"
          >
            <div className="repo-name">{repo.full_name}</div>
            {repo.description && (
              <div className="repo-desc">{repo.description}</div>
            )}
            <div className="repo-meta">
              {repo.language && <span>{repo.language} · </span>}
              <span>{repo.stars?.toLocaleString()} stars</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
