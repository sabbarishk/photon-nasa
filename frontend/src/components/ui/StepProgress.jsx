import { CheckCircle2, Loader2 } from 'lucide-react'

export default function StepProgress({ steps, currentStep }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {steps.map((step, i) => {
        const isDone = i < currentStep
        const isCurrent = i === currentStep
        const isPending = i > currentStep

        return (
          <div
            key={i}
            className={!isPending ? 'fade-in' : ''}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              opacity: isPending ? 0.3 : 1,
              animationDelay: `${i * 100}ms`,
              transition: 'opacity 300ms ease',
            }}
          >
            {isDone ? (
              <CheckCircle2 size={16} color="var(--success)" style={{ flexShrink: 0 }} />
            ) : isCurrent ? (
              <Loader2 size={16} color="var(--accent-primary)" style={{ flexShrink: 0, animation: 'spin 1s linear infinite' }} />
            ) : (
              <div style={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                border: '1px solid var(--border-default)',
                flexShrink: 0,
              }} />
            )}
            <span style={{
              fontSize: 13,
              color: isDone
                ? 'var(--text-secondary)'
                : isCurrent
                ? 'var(--text-primary)'
                : 'var(--text-tertiary)',
              fontWeight: isCurrent ? 500 : 400,
            }}>
              {step}
            </span>
          </div>
        )
      })}
    </div>
  )
}
