export default function SuggestionChip({ label, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-default)',
        borderRadius: 999,
        padding: '6px 12px',
        fontSize: 12,
        fontWeight: 500,
        color: 'var(--text-secondary)',
        cursor: 'pointer',
        transition: 'all 150ms ease',
        whiteSpace: 'nowrap',
        fontFamily: 'inherit',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--accent-primary)'
        e.currentTarget.style.color = 'var(--text-primary)'
        e.currentTarget.style.background = 'var(--accent-muted)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-default)'
        e.currentTarget.style.color = 'var(--text-secondary)'
        e.currentTarget.style.background = 'var(--bg-elevated)'
      }}
    >
      {label}
    </button>
  )
}
