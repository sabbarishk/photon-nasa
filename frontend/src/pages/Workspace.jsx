import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Upload, BarChart2, Lightbulb, AlertTriangle, Code2,
  MessageCircle, Github, CheckCircle2, Loader2, X,
  FileText, Link, ChevronDown
} from 'lucide-react'
import KPICard from '../components/ui/KPICard'
import Badge from '../components/ui/Badge'
import Skeleton from '../components/ui/Skeleton'
import SuggestionChip from '../components/ui/SuggestionChip'
import StepProgress from '../components/ui/StepProgress'
import { analyzeData, uploadFile, pingBackend } from '../services/api'

const EXAMPLE_CHIPS = [
  'What are the key trends?',
  'Show me the top performers',
  'Are there any anomalies?',
]

const ANALYSIS_STEPS = [
  'Loading and profiling your data...',
  'Retrieving analysis methodology...',
  'Generating analysis code...',
  'Executing on AWS Lambda...',
  'Building your dashboard...',
]

const SESSION_KEY = 'photon_session'
const MAX_SAVED_TURNS = 10

function WorkspaceNavbar() {
  const navigate = useNavigate()
  return (
    <div style={{
      height: 56,
      background: 'rgba(17,17,19,0.80)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      flexShrink: 0,
    }}>
      <button
        onClick={() => navigate('/')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: 0,
        }}
      >
        <span style={{ fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>Photon</span>
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
      </button>
      <a
        href="https://github.com/sabbarishk/photon-nasa"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          color: 'var(--text-tertiary)',
          textDecoration: 'none',
          fontSize: 12,
          transition: 'color 150ms ease',
        }}
        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-tertiary)' }}
      >
        <Github size={14} />
        GitHub
      </a>
    </div>
  )
}

function DataSourceSection({ currentSource, onSourceSet, onClear, onLoadDemo }) {
  const [dragging, setDragging] = useState(false)
  const [urlValue, setUrlValue] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const fileInputRef = useRef(null)

  const handleDrop = useCallback(async (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer?.files?.[0]
    if (!file) return
    await handleFileUpload(file)
  }, [])

  const handleFileUpload = async (file) => {
    setUploadError('')
    setUploading(true)
    try {
      const result = await uploadFile(file)
      onSourceSet(result.path, file.name)
    } catch (err) {
      setUploadError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleUrlSubmit = () => {
    const v = urlValue.trim()
    if (v) {
      onSourceSet(v, v)
      setUrlValue('')
    }
  }

  if (currentSource) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '10px 12px',
        background: 'var(--success-muted)',
        border: '1px solid rgba(34,197,94,0.25)',
        borderRadius: 6,
      }}>
        <div style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: 'var(--success)',
          flexShrink: 0,
        }} />
        <FileText size={14} color="var(--success)" style={{ flexShrink: 0 }} />
        <span style={{
          fontSize: 12,
          color: 'var(--text-secondary)',
          flex: 1,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>{currentSource.label}</span>
        <button
          onClick={onClear}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-tertiary)',
            cursor: 'pointer',
            padding: 2,
            display: 'flex',
            alignItems: 'center',
            borderRadius: 4,
            transition: 'color 150ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-tertiary)' }}
        >
          <X size={14} />
        </button>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragging ? 'var(--accent-primary)' : 'var(--border-default)'}`,
          borderRadius: 8,
          padding: 20,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 6,
          cursor: 'pointer',
          background: dragging ? 'var(--accent-muted)' : 'transparent',
          transition: 'all 150ms ease',
        }}
      >
        {uploading ? (
          <Loader2 size={20} color="var(--accent-primary)" style={{ animation: 'spin 1s linear infinite' }} />
        ) : (
          <Upload size={20} color="var(--text-tertiary)" />
        )}
        <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          {uploading ? 'Uploading...' : 'Drop CSV or Excel file'}
        </span>
        <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>or paste a URL below</span>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          style={{ display: 'none' }}
          onChange={e => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
        />
      </div>

      {uploadError && (
        <p style={{ fontSize: 11, color: 'var(--error)', margin: 0 }}>{uploadError}</p>
      )}

      {/* Demo separator + button */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '12px 0' }}>
        <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
        <span style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>or try the demo</span>
        <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
      </div>
      <button
        onClick={onLoadDemo}
        style={{
          width: '100%',
          padding: '10px',
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-default)',
          borderRadius: 6,
          color: 'var(--text-secondary)',
          fontSize: 13,
          fontWeight: 500,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          transition: 'all 150ms ease',
          fontFamily: 'inherit',
          marginBottom: 8,
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'var(--bg-overlay)'
          e.currentTarget.style.borderColor = 'var(--border-strong)'
          e.currentTarget.style.color = 'var(--text-primary)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'var(--bg-elevated)'
          e.currentTarget.style.borderColor = 'var(--border-default)'
          e.currentTarget.style.color = 'var(--text-secondary)'
        }}
      >
        <BarChart2 size={14} />
        Manufacturing Quality Dataset
        <span style={{
          fontSize: 10,
          background: 'var(--accent-muted)',
          color: '#a5b4fc',
          padding: '1px 6px',
          borderRadius: 999,
          border: '1px solid var(--accent-border)',
        }}>DEMO</span>
      </button>

      <div style={{ display: 'flex', gap: 6 }}>
        <input
          type="text"
          value={urlValue}
          onChange={e => setUrlValue(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleUrlSubmit()}
          placeholder="https://example.com/data.csv"
          style={{
            flex: 1,
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)',
            padding: '8px 10px',
            borderRadius: 6,
            fontSize: 12,
            outline: 'none',
            transition: 'border-color 150ms ease, box-shadow 150ms ease',
          }}
          onFocus={e => {
            e.target.style.borderColor = 'var(--accent-primary)'
            e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.15)'
          }}
          onBlur={e => {
            e.target.style.borderColor = 'var(--border-default)'
            e.target.style.boxShadow = 'none'
          }}
        />
        <button
          onClick={handleUrlSubmit}
          disabled={!urlValue.trim()}
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-secondary)',
            padding: '8px 10px',
            borderRadius: 6,
            cursor: urlValue.trim() ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            opacity: urlValue.trim() ? 1 : 0.4,
            transition: 'all 150ms ease',
          }}
        >
          <Link size={14} />
        </button>
      </div>
    </div>
  )
}

function stripMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#{1,6}\s/g, '')
    .replace(/`(.*?)`/g, '$1')
    .trim()
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'flex-start' }}>
      <span style={{ fontSize: 10, color: 'var(--text-tertiary)', letterSpacing: '0.05em', textTransform: 'uppercase', fontWeight: 500 }}>Photon</span>
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px 12px 12px 2px',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 4,
      }}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: 'var(--text-tertiary)',
              animation: `typingDot 1.2s ${i * 0.2}s ease-in-out infinite`,
            }}
          />
        ))}
      </div>
    </div>
  )
}

function MessageBubble({ role, content, suggestions, onSuggestionClick }) {
  if (role === 'user') {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <div style={{
          background: 'var(--accent-muted)',
          border: '1px solid var(--accent-border)',
          borderRadius: '12px 12px 2px 12px',
          padding: '12px 16px',
          maxWidth: '75%',
          fontSize: 14,
          color: 'var(--text-primary)',
          lineHeight: 1.5,
        }}>
          {content}
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-start' }}>
      <span style={{ fontSize: 10, color: 'var(--text-tertiary)', letterSpacing: '0.05em', textTransform: 'uppercase', fontWeight: 500 }}>Photon</span>
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px 12px 12px 2px',
        padding: '14px 16px',
        maxWidth: '85%',
        fontSize: 14,
        color: 'var(--text-primary)',
        lineHeight: 1.7,
      }}>
        {content}
      </div>
      {suggestions && suggestions.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, paddingLeft: 2 }}>
          {suggestions.map((s, i) => (
            <SuggestionChip key={i} label={s} onClick={() => onSuggestionClick(s)} />
          ))}
        </div>
      )}
    </div>
  )
}

function EmptyConversation({ onChipClick }) {
  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 16,
      padding: 24,
    }}>
      <Lightbulb size={24} color="var(--text-tertiary)" />
      <p style={{ fontSize: 14, color: 'var(--text-secondary)', textAlign: 'center' }}>
        Ask anything about your data
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, width: '100%' }}>
        {EXAMPLE_CHIPS.map((chip, i) => (
          <SuggestionChip key={i} label={chip} onClick={() => onChipClick(chip)} />
        ))}
      </div>
    </div>
  )
}

function EmptyDashboard() {
  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 12,
      padding: 48,
    }}>
      <BarChart2 size={48} color="var(--text-tertiary)" style={{ opacity: 0.3 }} />
      <p style={{ fontSize: 16, color: 'var(--text-secondary)' }}>Your analysis will appear here</p>
      <p style={{ fontSize: 13, color: 'var(--text-tertiary)' }}>Load a dataset and ask a question to get started</p>
    </div>
  )
}

function LoadingDashboard({ currentStep }) {
  return (
    <div style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 32 }}>
      <StepProgress steps={ANALYSIS_STEPS} currentStep={currentStep} />
      <div>
        <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>KEY METRICS</p>
        <div style={{ display: 'flex', gap: 12 }}>
          {[1, 2, 3].map(i => (
            <div key={i} style={{ flex: 1, background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 24 }}>
              <Skeleton height={10} width="60%" style={{ marginBottom: 12 }} />
              <Skeleton height={30} width="80%" style={{ marginBottom: 8 }} />
              <Skeleton height={10} width="40%" />
            </div>
          ))}
        </div>
      </div>
      <div>
        <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>ANALYSIS</p>
        <Skeleton height={300} style={{ borderRadius: 8, width: '100%' }} />
      </div>
    </div>
  )
}

function TurnHistoryBar({ turns, activeTurnIndex, onSelect }) {
  if (turns.length <= 1) return null
  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
      padding: '12px 32px',
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      overflowX: 'auto',
      flexShrink: 0,
    }}>
      <span style={{
        fontSize: 11,
        fontWeight: 500,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        color: 'var(--text-tertiary)',
        marginRight: 4,
        whiteSpace: 'nowrap',
        flexShrink: 0,
      }}>
        Analysis History
      </span>
      {turns.map((turn, i) => {
        const isActive = i === activeTurnIndex
        return (
          <button
            key={turn.id}
            onClick={() => onSelect(i)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              gap: 2,
              padding: '6px 12px',
              borderRadius: 6,
              border: `1px solid ${isActive ? 'var(--accent-primary)' : 'var(--border-default)'}`,
              background: isActive ? 'var(--accent-muted)' : 'var(--bg-elevated)',
              color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 150ms ease',
              flexShrink: 0,
              textAlign: 'left',
              fontFamily: 'inherit',
            }}
            onMouseEnter={e => {
              if (!isActive) {
                e.currentTarget.style.borderColor = 'var(--border-strong)'
                e.currentTarget.style.color = 'var(--text-primary)'
              }
            }}
            onMouseLeave={e => {
              if (!isActive) {
                e.currentTarget.style.borderColor = 'var(--border-default)'
                e.currentTarget.style.color = 'var(--text-secondary)'
              }
            }}
          >
            <span style={{ fontSize: 12, fontWeight: 500, whiteSpace: 'nowrap', maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', display: 'block' }}>
              Q{i + 1}: {turn.question.length > 30 ? turn.question.slice(0, 30) + '…' : turn.question}
            </span>
            <span style={{ fontSize: 10, color: 'var(--text-tertiary)', whiteSpace: 'nowrap' }}>
              {turn.timestamp}
            </span>
          </button>
        )
      })}
    </div>
  )
}

function AnalysisResults({ result, methodologyUsed, codeVisible, onToggleCode, onRerun }) {
  const hasImage = Boolean(result.execution?.output_image)

  return (
    <div className="fade-in" style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* KPI Cards */}
      {result.kpi_cards && result.kpi_cards.length > 0 && (
        <div>
          <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>KEY METRICS</p>
          <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4 }}>
            {result.kpi_cards.map((kpi, i) => (
              <KPICard key={i} label={kpi.label} value={kpi.value} delta={kpi.delta} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Chart */}
      {hasImage ? (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)' }}>ANALYSIS</p>
            {methodologyUsed && <Badge type={methodologyUsed} label={methodologyUsed.replace('_', ' ')} />}
          </div>
          <img
            src={`data:image/png;base64,${result.execution.output_image}`}
            alt="Analysis dashboard"
            style={{ width: '100%', borderRadius: 8, border: '1px solid var(--border-subtle)', display: 'block' }}
          />
        </div>
      ) : (
        <div style={{
          border: '1px dashed var(--border-default)',
          borderRadius: 8,
          padding: 32,
          textAlign: 'center',
        }}>
          <BarChart2 size={24} style={{ color: 'var(--text-tertiary)', margin: '0 auto 12px', display: 'block' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 16 }}>
            Chart not available for this turn
          </p>
          <button
            onClick={onRerun}
            style={{
              background: 'var(--accent-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              padding: '8px 16px',
              fontSize: 13,
              fontWeight: 500,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontFamily: 'inherit',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--accent-hover)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--accent-primary)' }}
          >
            ↺ Re-run this analysis
          </button>
        </div>
      )}

      {/* Anomalies */}
      {result.anomalies && result.anomalies.length > 0 && (
        <div>
          <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>ANOMALIES DETECTED</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {result.anomalies.map((a, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                background: 'var(--warning-muted)',
                border: '1px solid rgba(245,158,11,0.3)',
                borderRadius: 6,
                padding: 12,
              }}>
                <AlertTriangle size={16} color="var(--warning)" style={{ flexShrink: 0, marginTop: 1 }} />
                <div>
                  <span style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: 13 }}>{a.column}</span>
                  {' '}
                  <span style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{a.finding}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insight Narrative */}
      {result.insight_narrative && (
        <div>
          <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>ANALYSIS SUMMARY</p>
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
              <Lightbulb size={16} color="var(--accent-primary)" />
              <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--accent-primary)' }}>AI Insight</span>
            </div>
            <p style={{ fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.7, margin: 0 }}>
              {stripMarkdown(result.insight_narrative)}
            </p>
          </div>
        </div>
      )}

      {/* Data Profile */}
      {result.profile?.columns?.length > 0 && (
        <div>
          <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>DATA PROFILE</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: result.profile.columns.some(c => c.null_pct > 0) ? 10 : 0 }}>
            {result.profile.columns.map((col, i) => (
              <span key={i} style={{
                fontSize: 11,
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 4,
                padding: '3px 8px',
                color: 'var(--text-secondary)',
                whiteSpace: 'nowrap',
              }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{col.name}</span>
                <span style={{ color: 'var(--text-tertiary)', marginLeft: 4 }}>{col.dtype}</span>
              </span>
            ))}
          </div>
          {result.profile.columns.some(c => c.null_pct > 0) && (
            <p style={{ fontSize: 12, color: 'var(--warning)', marginTop: 4 }}>
              ⚠ {result.profile.columns.filter(c => c.null_pct > 0).length} column{result.profile.columns.filter(c => c.null_pct > 0).length > 1 ? 's' : ''} contain null values. Consider cleaning your data before analysis for best results.
            </p>
          )}
        </div>
      )}

      {/* Generated Code (collapsible, per-turn visibility) */}
      {result.code && (
        <div>
          <button
            onClick={onToggleCode}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              width: '100%',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-default)',
              color: 'var(--text-primary)',
              padding: '8px 16px',
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 150ms ease',
              justifyContent: 'center',
              fontFamily: 'inherit',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-overlay)'; e.currentTarget.style.borderColor = 'var(--border-strong)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.borderColor = 'var(--border-default)' }}
          >
            <Code2 size={14} />
            {codeVisible ? 'Hide generated code' : 'Show generated code'}
          </button>
          {codeVisible && (
            <div style={{ marginTop: 8 }}>
              <p style={{ fontSize: 11, color: 'var(--text-tertiary)', marginBottom: 8 }}>Code generated and executed by Photon</p>
              <pre style={{
                background: '#0d0d0f',
                border: '1px solid var(--border-subtle)',
                borderRadius: 6,
                padding: 16,
                fontSize: 13,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                color: '#e4e4e7',
                overflowX: 'auto',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}>
                {result.code}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function RestoreBanner({ savedAt, onRestore, onDismiss }) {
  return (
    <div style={{
      margin: '0 0 0 0',
      padding: '10px 16px',
      background: 'var(--accent-muted)',
      border: '1px solid var(--accent-border)',
      borderRadius: 6,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 8,
      flexShrink: 0,
    }}>
      <span style={{ fontSize: 12, color: '#a5b4fc', flex: 1 }}>
        ↩ Restore session from {savedAt}?
      </span>
      <div style={{ display: 'flex', gap: 6 }}>
        <button
          onClick={onRestore}
          style={{
            background: 'var(--accent-primary)',
            color: 'white',
            border: 'none',
            padding: '4px 10px',
            borderRadius: 4,
            fontSize: 11,
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: 'inherit',
          }}
        >
          Restore
        </button>
        <button
          onClick={onDismiss}
          style={{
            background: 'transparent',
            color: '#a5b4fc',
            border: '1px solid var(--accent-border)',
            padding: '4px 10px',
            borderRadius: 4,
            fontSize: 11,
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: 'inherit',
          }}
        >
          Start fresh
        </button>
      </div>
    </div>
  )
}

function saveSession(source, turns) {
  try {
    const toSave = turns.slice(-MAX_SAVED_TURNS).map(t => ({
      ...t,
      result: {
        ...t.result,
        execution: {
          ...t.result.execution,
          output_image: null, // too large for localStorage
        },
      },
    }))
    localStorage.setItem(SESSION_KEY, JSON.stringify({
      sessionId: crypto.randomUUID?.() || String(Date.now()),
      source,
      createdAt: new Date().toISOString(),
      turns: toSave,
    }))
  } catch {}
}

function loadSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

const DEMO_SOURCE = {
  path: 'https://raw.githubusercontent.com/sabbarishk/photon-nasa/main/photon/data/demo/manufacturing_quality.csv',
  label: 'Manufacturing Quality Dataset',
}

export default function Workspace() {
  const location = useLocation()
  const [currentSource, setCurrentSource] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [turns, setTurns] = useState([])
  const [activeTurnIndex, setActiveTurnIndex] = useState(null)
  const [codeVisible, setCodeVisible] = useState({})
  const [error, setError] = useState('')
  const [savedSession, setSavedSession] = useState(null)
  const threadRef = useRef(null)
  const stepTimerRef = useRef(null)

  const loadDemo = () => {
    setCurrentSource(DEMO_SOURCE)
  }

  // On mount: warm up backend, check for saved session, auto-load demo if routed from landing
  useEffect(() => {
    pingBackend()
    if (location.state?.loadDemo) {
      setCurrentSource(DEMO_SOURCE)
      return // skip session restore when demo-loading
    }
    const session = loadSession()
    if (session && session.turns?.length > 0) {
      setSavedSession(session)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight
    }
  }, [messages, loading])

  const startStepTimer = () => {
    setLoadingStep(0)
    let step = 0
    stepTimerRef.current = setInterval(() => {
      step = Math.min(step + 1, ANALYSIS_STEPS.length - 1)
      setLoadingStep(step)
    }, 2000)
  }

  const stopStepTimer = () => {
    if (stepTimerRef.current) {
      clearInterval(stepTimerRef.current)
      stepTimerRef.current = null
    }
  }

  const handleRestoreSession = () => {
    if (!savedSession) return
    const restoredMessages = savedSession.turns.flatMap(t => [
      { role: 'user', content: t.question },
      {
        role: 'assistant',
        content: t.result.insight_narrative || 'Analysis complete.',
        suggestions: t.result.follow_up_suggestions || [],
      },
    ])
    setMessages(restoredMessages)
    setTurns(savedSession.turns)
    setActiveTurnIndex(savedSession.turns.length - 1)
    setCurrentSource({ path: savedSession.source, label: savedSession.source })
    setSavedSession(null)
  }

  const handleDismissSession = () => {
    localStorage.removeItem(SESSION_KEY)
    setSavedSession(null)
  }

  const handleSubmit = async (question) => {
    const q = question || inputValue.trim()
    if (!q || !currentSource || loading) return

    setInputValue('')
    setError('')

    const userMsg = { role: 'user', content: q }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)

    setLoading(true)
    startStepTimer()

    const apiHistory = updatedMessages.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const result = await analyzeData(q, currentSource.path, apiHistory)
      stopStepTimer()
      setLoadingStep(ANALYSIS_STEPS.length - 1)

      const newTurn = {
        id: Date.now(),
        question: q,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        result,
      }
      const newTurns = [...turns, newTurn]
      setTurns(newTurns)
      setActiveTurnIndex(newTurns.length - 1)

      // Save to localStorage
      saveSession(currentSource.path, newTurns)

      const assistantMsg = {
        role: 'assistant',
        content: stripMarkdown(result.insight_narrative) || 'Analysis complete.',
        suggestions: result.follow_up_suggestions || [],
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      stopStepTimer()
      setError(err.message || 'Analysis failed. Check the server is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion)
  }

  const handleChipClick = (chip) => {
    if (!currentSource) return
    handleSubmit(chip)
  }

  const handleClear = () => {
    if (window.confirm('Clear all session history?')) {
      localStorage.removeItem(SESSION_KEY)
      setCurrentSource(null)
      setMessages([])
      setTurns([])
      setActiveTurnIndex(null)
      setCodeVisible({})
      setError('')
    }
  }

  const activeResult = activeTurnIndex !== null ? turns[activeTurnIndex] : null

  return (
    <>
      <style>{`
        @keyframes typingDot {
          0%, 60%, 100% { opacity: 0.2; transform: scale(0.8); }
          30% { opacity: 1; transform: scale(1); }
        }
      `}</style>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        <WorkspaceNavbar />

        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Left panel */}
          <div style={{
            width: 420,
            flexShrink: 0,
            background: 'var(--bg-surface)',
            borderRight: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            overflow: 'hidden',
          }}>
            {/* Data source */}
            <div style={{ padding: '16px 16px 20px', borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}>
              <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>DATA SOURCE</p>
              {savedSession && (
                <div style={{ marginBottom: 12 }}>
                  <RestoreBanner
                    savedAt={new Date(savedSession.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    onRestore={handleRestoreSession}
                    onDismiss={handleDismissSession}
                  />
                </div>
              )}
              <DataSourceSection
                currentSource={currentSource}
                onSourceSet={(path, label) => setCurrentSource({ path, label })}
                onClear={handleClear}
                onLoadDemo={loadDemo}
              />
            </div>

            {/* Conversation thread */}
            <div
              ref={threadRef}
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: 20,
                display: 'flex',
                flexDirection: 'column',
                gap: 16,
              }}
            >
              {messages.length === 0 ? (
                <EmptyConversation onChipClick={handleChipClick} />
              ) : (
                <>
                  {messages.map((msg, i) => (
                    <MessageBubble
                      key={i}
                      role={msg.role}
                      content={msg.content}
                      suggestions={msg.suggestions}
                      onSuggestionClick={handleSuggestionClick}
                    />
                  ))}
                  {loading && <TypingIndicator />}
                </>
              )}
            </div>

            {/* Input */}
            <div style={{ padding: 12, borderTop: '1px solid var(--border-subtle)', flexShrink: 0 }}>
              <textarea
                rows={2}
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit()
                  }
                }}
                disabled={!currentSource || loading}
                placeholder={currentSource ? 'Ask a question about your data...' : 'Load a data source above to start analyzing'}
                style={{
                  width: '100%',
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-default)',
                  color: 'var(--text-primary)',
                  padding: '12px 14px',
                  borderRadius: 6,
                  fontSize: 14,
                  resize: 'none',
                  outline: 'none',
                  fontFamily: 'inherit',
                  transition: 'border-color 150ms ease, box-shadow 150ms ease',
                  opacity: (!currentSource || loading) ? 0.5 : 1,
                  cursor: (!currentSource || loading) ? 'not-allowed' : 'text',
                }}
                onFocus={e => {
                  e.target.style.borderColor = 'var(--accent-primary)'
                  e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.15)'
                }}
                onBlur={e => {
                  e.target.style.borderColor = 'var(--border-default)'
                  e.target.style.boxShadow = 'none'
                }}
              />
              {error && (
                <p style={{ fontSize: 11, color: 'var(--error)', marginTop: 6 }}>{error}</p>
              )}
              {turns.length > 0 && (
                <button
                  onClick={handleClear}
                  style={{
                    marginTop: 8,
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-tertiary)',
                    fontSize: 11,
                    cursor: 'pointer',
                    padding: 0,
                    fontFamily: 'inherit',
                    transition: 'color 150ms ease',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
                  onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-tertiary)' }}
                >
                  Clear session history
                </button>
              )}
            </div>
          </div>

          {/* Right panel */}
          <div style={{
            flex: 1,
            background: 'var(--bg-base)',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
          }}>
            {turns.length > 1 && (
              <TurnHistoryBar
                turns={turns}
                activeTurnIndex={activeTurnIndex}
                onSelect={setActiveTurnIndex}
              />
            )}
            {loading ? (
              <LoadingDashboard currentStep={loadingStep} />
            ) : activeResult ? (
              <AnalysisResults
                result={activeResult.result}
                methodologyUsed={activeResult.result.methodology_used}
                codeVisible={codeVisible[activeTurnIndex] || false}
                onToggleCode={() => setCodeVisible(prev => ({
                  ...prev,
                  [activeTurnIndex]: !prev[activeTurnIndex],
                }))}
                onRerun={() => handleSubmit(activeResult.question)}
              />
            ) : (
              <EmptyDashboard />
            )}
          </div>
        </div>
      </div>
    </>
  )
}
