export default function Skeleton({ width = '100%', height = 16, style = {}, className = '' }) {
  return (
    <div
      className={className}
      style={{
        width,
        height,
        borderRadius: 4,
        background: 'linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-overlay) 50%, var(--bg-elevated) 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s infinite',
        ...style,
      }}
    />
  )
}
