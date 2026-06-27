const VARIANTS = {
  tabular: { bg: '#1e1b4b', color: '#a5b4fc', border: '#3730a3' },
  time_series: { bg: '#052e16', color: '#86efac', border: '#166534' },
  wide_format: { bg: '#2e1065', color: '#d8b4fe', border: '#7e22ce' },
  success: { bg: 'var(--success-muted)', color: 'var(--success)', border: 'rgba(34,197,94,0.3)' },
  error: { bg: 'var(--error-muted)', color: 'var(--error)', border: 'rgba(239,68,68,0.3)' },
  warning: { bg: 'var(--warning-muted)', color: 'var(--warning)', border: 'rgba(245,158,11,0.3)' },
}

export default function Badge({ type = 'tabular', label }) {
  const v = VARIANTS[type] || VARIANTS.tabular
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '2px 8px',
      borderRadius: 999,
      fontSize: 11,
      fontWeight: 500,
      letterSpacing: '0.05em',
      textTransform: 'uppercase',
      background: v.bg,
      color: v.color,
      border: `1px solid ${v.border}`,
      whiteSpace: 'nowrap',
    }}>
      {label}
    </span>
  )
}
