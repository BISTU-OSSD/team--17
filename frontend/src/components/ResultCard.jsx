export default function ResultCard({ data }) {
  const {
    full_name,
    description,
    stars,
    forks,
    watchers,
    open_issues,
    language,
    topics,
    overall_grade,
    license_name,
    has_readme,
    has_contributing,
    community_metrics,
  } = data

  return (
    <div className="card">
      <h2>{full_name}</h2>
      {description && <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>{description}</p>}

      <div className="grade-section">
        <div className="grade-badge">{overall_grade}</div>
        <div>
          <div className="grade-label">综合健康等级</div>
          <div style={{ color: '#64748b', fontSize: '0.85rem' }}>
            {overall_grade === 'A' ? '优秀' : overall_grade === 'B' ? '良好' : overall_grade === 'C' ? '一般' : '待改善'}
          </div>
        </div>
      </div>

      <div className="info-grid">
        <div className="info-item">
          <span className="label">Stars</span>
          <span className="value">{stars.toLocaleString()}</span>
        </div>
        <div className="info-item">
          <span className="label">Forks</span>
          <span className="value">{forks.toLocaleString()}</span>
        </div>
        <div className="info-item">
          <span className="label">Watchers</span>
          <span className="value">{watchers.toLocaleString()}</span>
        </div>
        <div className="info-item">
          <span className="label">Open Issues</span>
          <span className="value">{open_issues.toLocaleString()}</span>
        </div>
        <div className="info-item">
          <span className="label">主语言</span>
          <span className="value">{language || '-'}</span>
        </div>
        <div className="info-item">
          <span className="label">许可证</span>
          <span className="value">{license_name || '-'}</span>
        </div>
        <div className="info-item">
          <span className="label">贡献者</span>
          <span className="value">{community_metrics?.contributors_count ?? '-'}</span>
        </div>
        <div className="info-item">
          <span className="label">Tags</span>
          <span className="value">{community_metrics?.tags_count ?? 0}</span>
        </div>
      </div>

      <div style={{ marginTop: '0.75rem', display: 'flex', gap: '1rem', fontSize: '0.85rem', color: '#64748b' }}>
        <span>README: {has_readme ? '✅' : '❌'}</span>
        <span>CONTRIBUTING: {has_contributing ? '✅' : '❌'}</span>
        <span>Release: {community_metrics?.has_releases ? '✅' : '❌'}</span>
      </div>

      {topics && topics.length > 0 && (
        <div className="topics">
          {topics.map((t) => (
            <span key={t} className="topic-tag">{t}</span>
          ))}
        </div>
      )}
    </div>
  )
}
