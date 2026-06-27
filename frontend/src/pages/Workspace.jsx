import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, BarChart2, Lightbulb, AlertTriangle, Code2,
  MessageCircle, Github, CheckCircle2, Loader2, X,
  FileText, Link
} from 'lucide-react'
import KPICard from '../components/ui/KPICard'
import Badge from '../components/ui/Badge'
import Skeleton from '../components/ui/Skeleton'
import SuggestionChip from '../components/ui/SuggestionChip'
import StepProgress from '../components/ui/StepProgress'
import { analyzeData, uploadFile } from '../services/api'

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

function DataSourceSection({ currentSource, onSourceSet, onClear }) {
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

function MessageBubble({ role, content, suggestions, onSuggestionClick }) {
  if (role === 'user') {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <div style={{
          background: 'var(--accent-muted)',
          border: '1px solid var(--accent-border)',
          borderRadius: '12px 12px 2px 12px',
          padding: '10px 14px',
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
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 32 }}>
      <StepProgress steps={ANALYSIS_STEPS} currentStep={currentStep} />
      <div>
        <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 12 }}>KEY METRICS</p>
        <div style={{ display: 'flex', gap: 12 }}>
          {[1, 2, 3].map(i => (
            <div key={i} style={{ flex: 1, background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 20 }}>
              <Skeleton height={10} width="60%" style={{ marginBottom: 12 }} />
              <Skeleton height={28} width="80%" style={{ marginBottom: 8 }} />
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

function AnalysisResults({ result, methodologyUsed }) {
  const [codeOpen, setCodeOpen] = useState(false)

  return (
    <div className="fade-in" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 28 }}>

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
      {result.execution?.output_image && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)' }}>ANALYSIS</p>
            {methodologyUsed && <Badge type={methodologyUsed} label={methodologyUsed.replace('_', ' ')} />}
          </div>
          <img
            src={`data:image/png;base64,${result.execution.output_image}`}
            alt="Analysis dashboard"
            style={{
              width: '100%',
              borderRadius: 8,
              border: '1px solid var(--border-subtle)',
              display: 'block',
            }}
          />
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
          <div style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 8,
            padding: 20,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
              <Lightbulb size={16} color="var(--accent-primary)" />
              <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--accent-primary)' }}>AI Insight</span>
            </div>
            <p style={{ fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.7, margin: 0 }}>
              {result.insight_narrative}
            </p>
          </div>
        </div>
      )}

      {/* Generated Code (collapsible) */}
      {result.code && (
        <div>
          <button
            onClick={() => setCodeOpen(o => !o)}
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
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-overlay)'; e.currentTarget.style.borderColor = 'var(--border-strong)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-elevated)'; e.currentTarget.style.borderColor = 'var(--border-default)' }}
          >
            <Code2 size={14} />
            {codeOpen ? 'Hide generated code' : 'Show generated code'}
          </button>
          {codeOpen && (
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

export default function Workspace() {
  const [currentSource, setCurrentSource] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState(0)
  const [latestResult, setLatestResult] = useState(null)
  const [error, setError] = useState('')
  const threadRef = useRef(null)
  const stepTimerRef = useRef(null)

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight
    }
  }, [messages])

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
      setLatestResult(result)

      const assistantMsg = {
        role: 'assistant',
        content: result.insight_narrative || 'Analysis complete.',
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
    setCurrentSource(null)
    setMessages([])
    setLatestResult(null)
    setError('')
  }

  const conversationHistory = messages.map(m => ({ role: m.role, content: m.content }))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <WorkspaceNavbar />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left panel */}
        <div style={{
          width: 380,
          flexShrink: 0,
          background: 'var(--bg-surface)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          overflow: 'hidden',
        }}>
          {/* Data source */}
          <div style={{ padding: 16, borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}>
            <p style={{ fontSize: 11, fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: 10 }}>DATA SOURCE</p>
            <DataSourceSection
              currentSource={currentSource}
              onSourceSet={(path, label) => setCurrentSource({ path, label })}
              onClear={handleClear}
            />
          </div>

          {/* Conversation thread */}
          <div
            ref={threadRef}
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: 16,
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}
          >
            {messages.length === 0 ? (
              <EmptyConversation onChipClick={handleChipClick} />
            ) : (
              messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  role={msg.role}
                  content={msg.content}
                  suggestions={msg.suggestions}
                  onSuggestionClick={handleSuggestionClick}
                />
              ))
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
                padding: '10px 12px',
                borderRadius: 6,
                fontSize: 13,
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
            {!currentSource && (
              <p style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 6 }}>
                Load a data source above to start analyzing
              </p>
            )}
            {error && (
              <p style={{ fontSize: 11, color: 'var(--error)', marginTop: 6 }}>{error}</p>
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
          {loading ? (
            <LoadingDashboard currentStep={loadingStep} />
          ) : latestResult ? (
            <AnalysisResults result={latestResult} methodologyUsed={latestResult.methodology_used} />
          ) : (
            <EmptyDashboard />
          )}
        </div>
      </div>
    </div>
  )
}
