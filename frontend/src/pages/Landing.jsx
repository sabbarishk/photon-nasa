import { useNavigate } from 'react-router-dom'
import { BarChart2, MessageCircle, GitBranch, Github, ChevronDown } from 'lucide-react'

function Navbar() {
  const navigate = useNavigate()
  return (
    <nav style={{
      height: 56,
      background: 'rgba(17,17,19,0.80)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontWeight: 600, fontSize: 16, color: 'var(--text-primary)' }}>Photon</span>
        <span style={{
          fontSize: 10,
          fontWeight: 500,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          background: 'var(--accent-muted)',
          border: '1px solid var(--accent-border)',
          color: '#a5b4fc',
          padding: '1px 6px',
          borderRadius: 999,
        }}>v2</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <a
          href="https://github.com/sabbarishk/photon-nasa"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            color: 'var(--text-secondary)',
            textDecoration: 'none',
            fontSize: 13,
            fontWeight: 500,
            padding: '6px 12px',
            borderRadius: 6,
            border: '1px solid var(--border-default)',
            background: 'var(--bg-elevated)',
            transition: 'all 150ms ease',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.color = 'var(--text-primary)'
            e.currentTarget.style.borderColor = 'var(--border-strong)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.color = 'var(--text-secondary)'
            e.currentTarget.style.borderColor = 'var(--border-default)'
          }}
        >
          <Github size={14} />
          Star on GitHub
        </a>
        <button
          onClick={() => navigate('/analyze')}
          style={{
            background: 'var(--accent-primary)',
            color: 'white',
            border: 'none',
            padding: '7px 16px',
            borderRadius: 6,
            fontSize: 13,
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 150ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--accent-hover)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'var(--accent-primary)' }}
        >
          Try Demo
        </button>
      </div>
    </nav>
  )
}

function Feature({ icon: Icon, title, body, badge }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{
        width: 40,
        height: 40,
        borderRadius: 8,
        background: 'var(--accent-muted)',
        border: '1px solid var(--accent-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <Icon size={20} color="var(--accent-primary)" />
      </div>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h3>
          {badge && (
            <span style={{
              fontSize: 10,
              fontWeight: 500,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              background: 'var(--warning-muted)',
              border: '1px solid rgba(245,158,11,0.3)',
              color: 'var(--warning)',
              padding: '1px 6px',
              borderRadius: 999,
            }}>{badge}</span>
          )}
        </div>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7 }}>{body}</p>
      </div>
    </div>
  )
}

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <Navbar />

      {/* Hero */}
      <section style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 24px',
        background: 'radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.08) 0%, transparent 60%), var(--bg-base)',
        textAlign: 'center',
        position: 'relative',
      }}>
        {/* Badge pill */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          background: 'var(--accent-muted)',
          border: '1px solid var(--accent-border)',
          borderRadius: 999,
          padding: '4px 14px',
          marginBottom: 32,
          fontSize: 11,
          fontWeight: 500,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#a5b4fc',
        }}>
          ✦ Open Source · Self-Hostable
        </div>

        <h1 style={{
          fontSize: 48,
          fontWeight: 700,
          letterSpacing: '-0.02em',
          lineHeight: 1.1,
          color: 'var(--text-primary)',
          marginBottom: 20,
          maxWidth: 600,
        }}>
          Your data, analyzed.
        </h1>

        <p style={{
          fontSize: 18,
          fontWeight: 400,
          color: 'var(--text-secondary)',
          maxWidth: 480,
          lineHeight: 1.6,
          marginBottom: 36,
        }}>
          Upload any CSV or Excel file. Ask questions in plain English. Get a complete KPI dashboard with real executed results — not AI guesses.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginBottom: 20 }}>
          <button
            onClick={() => navigate('/analyze')}
            style={{
              background: 'var(--accent-primary)',
              color: 'white',
              border: 'none',
              padding: '10px 24px',
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 150ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--accent-hover)'; e.currentTarget.style.transform = 'scale(1.01)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--accent-primary)'; e.currentTarget.style.transform = 'scale(1)' }}
          >
            Start Analyzing
          </button>
          <a
            href="https://github.com/sabbarishk/photon-nasa"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--bg-elevated)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-default)',
              padding: '10px 24px',
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 500,
              textDecoration: 'none',
              transition: 'all 150ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-overlay)'; e.currentTarget.style.borderColor = 'var(--border-strong)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.borderColor = 'var(--border-default)' }}
          >
            <Github size={16} />
            View on GitHub
          </a>
        </div>

        <div style={{
          height: 1,
          background: 'var(--border-subtle)',
          width: 240,
          margin: '4px auto 16px',
        }} />

        <p style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
          No signup required · Self-hostable · Open source MIT
        </p>

        {/* Scroll indicator */}
        <div style={{
          position: 'absolute',
          bottom: 32,
          left: '50%',
          transform: 'translateX(-50%)',
          color: 'var(--text-tertiary)',
          animation: 'scrollBounce 2s ease-in-out infinite',
        }}>
          <ChevronDown size={24} />
        </div>
      </section>

      {/* Features */}
      <section style={{
        background: 'var(--bg-base)',
        padding: '80px 24px',
        borderTop: '1px solid var(--border-subtle)',
      }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <p style={{
            fontSize: 11,
            fontWeight: 500,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: 'var(--text-tertiary)',
            textAlign: 'center',
            marginBottom: 48,
          }}>How it works</p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 48,
          }}>
            <Feature
              icon={BarChart2}
              title="Real execution, not guesses"
              body="Your analysis code runs on AWS Lambda. Every number in your dashboard comes from actual computation against your real data."
            />
            <Feature
              icon={MessageCircle}
              title="Conversational refinement"
              body="Ask follow-up questions. Drill into specific segments. Each turn builds on the previous analysis — like working with a senior analyst."
            />
            <Feature
              icon={GitBranch}
              title="Promote to pipeline"
              body="Turn a working analysis into a scheduled AWS pipeline with one click. From exploration to production without leaving Photon."
              badge="Coming soon"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        background: 'var(--bg-surface)',
        borderTop: '1px solid var(--border-subtle)',
        padding: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
          © 2026 Photon. Open source MIT license.
        </span>
        <a
          href="https://github.com/sabbarishk/photon-nasa"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12,
            color: 'var(--text-tertiary)',
            textDecoration: 'none',
            transition: 'color 150ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-tertiary)' }}
        >
          <Github size={14} />
          GitHub
        </a>
      </footer>
    </div>
  )
}
