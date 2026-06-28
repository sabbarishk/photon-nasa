export default function KPICard({ label, value, delta, index = 0 }) {
  const deltaColor = delta?.startsWith('+')
    ? 'var(--delta-positive)'
    : delta?.startsWith('-')
    ? 'var(--delta-negative)'
    : 'var(--delta-neutral)'

  const deltaArrow = delta?.startsWith('+') ? '▲' : delta?.startsWith('-') ? '▼' : ''

  return (
    <div
      className="fade-in"
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 8,
        padding: 24,
        minWidth: 140,
        flex: '0 0 auto',
        animationDelay: `${index * 50}ms`,
        transition: 'border-color 150ms ease, background 150ms ease',
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--border-default)'
        e.currentTarget.style.background = 'var(--bg-elevated)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-subtle)'
        e.currentTarget.style.background = 'var(--bg-surface)'
      }}
    >
      <p style={{
        fontSize: 11,
        fontWeight: 500,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        color: 'var(--text-tertiary)',
        marginBottom: 8,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {label}
      </p>
      <p style={{
        fontSize: 30,
        fontWeight: 700,
        color: 'var(--text-primary)',
        lineHeight: 1.1,
        marginBottom: delta ? 6 : 0,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {value}
      </p>
      {delta && (
        <p style={{
          fontSize: 12,
          fontWeight: 500,
          color: deltaColor,
          display: 'flex',
          alignItems: 'center',
          gap: 3,
        }}>
          {deltaArrow && <span>{deltaArrow}</span>}
          {delta}
        </p>
      )}
    </div>
  )
}
