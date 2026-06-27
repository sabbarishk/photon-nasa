import { useState, useEffect, useRef } from 'react'
import { generateAnalysis } from '../services/api'

const LOADING_STEPS = [
  'Loading your data...',
  'Profiling dataset...',
  'Retrieving analysis methodology...',
  'Generating analysis code...',
  'Executing on AWS Lambda...',
]

const TYPE_BADGE = {
  tabular:     'bg-blue-600',
  time_series: 'bg-green-600',
  wide_format:  'bg-purple-600',
}

const METHOD_BANNER = {
  tabular:     'bg-blue-900/40 border-blue-500/30 text-blue-300',
  time_series: 'bg-green-900/40 border-green-500/30 text-green-300',
  wide_format:  'bg-purple-900/40 border-purple-500/30 text-purple-300',
}

function WorkflowGenerator() {
  const [state, setState]       = useState('input') // 'input' | 'loading' | 'results'
  const [source, setSource]     = useState('')
  const [question, setQuestion] = useState('')
  const [stepIndex, setStepIndex] = useState(0)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState(null)
  const [showCode, setShowCode] = useState(false)
  const intervalRef             = useRef(null)

  useEffect(() => {
    if (state === 'loading') {
      setStepIndex(0)
      intervalRef.current = setInterval(
        () => setStepIndex(i => Math.min(i + 1, LOADING_STEPS.length - 1)),
        8000
      )
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [state])

  const handleAnalyze = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setShowCode(false)
    setState('loading')
    try {
      const data = await generateAnalysis(question, source)
      setResult(data)
      setState('results')
    } catch (err) {
      setError(err.message)
      setState('input')
    }
  }

  const handleReset = () => {
    setState('input')
    setResult(null)
    setError(null)
    setShowCode(false)
  }

  // ── STATE 1: Input ──────────────────────────────────────────────────────────
  if (state === 'input') {
    return (
      <main className="flex-1 py-16 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="glass-effect rounded-xl p-8">
            <h1 className="text-3xl font-bold text-white mb-2">Analyze your data</h1>
            <p className="text-gray-400 mb-8 text-sm leading-relaxed">
              Paste a public CSV URL or describe your data source. Ask any question about it.
            </p>
            <form onSubmit={handleAnalyze} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Data source URL
                </label>
                <input
                  type="text"
                  value={source}
                  onChange={e => setSource(e.target.value)}
                  placeholder="https://example.com/data.csv"
                  required
                  className="w-full bg-white/5 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Your question
                </label>
                <textarea
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  placeholder="What is the trend over time? Which category has the highest values?"
                  required
                  rows={3}
                  className="w-full bg-white/5 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition resize-none"
                />
              </div>
              {error && (
                <div className="border border-red-500/50 bg-red-900/20 rounded-lg px-4 py-3 text-red-400 text-sm">
                  {error}
                </div>
              )}
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-lg transition"
              >
                Analyze
              </button>
            </form>
          </div>
        </div>
      </main>
    )
  }

  // ── STATE 2: Loading ────────────────────────────────────────────────────────
  if (state === 'loading') {
    return (
      <main className="flex-1 py-16 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="glass-effect rounded-xl p-12 flex flex-col items-center text-center">
            <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-10" />
            <div className="space-y-3 w-full max-w-xs text-left">
              {LOADING_STEPS.map((step, i) => (
                <div
                  key={step}
                  className={`flex items-center gap-3 text-sm transition-all duration-300 ${
                    i < stepIndex  ? 'text-green-400' :
                    i === stepIndex ? 'text-white font-medium' :
                                     'text-gray-600'
                  }`}
                >
                  <span className="w-4 text-center flex-shrink-0">
                    {i < stepIndex ? '✓' : i === stepIndex ? '›' : '·'}
                  </span>
                  {step}
                </div>
              ))}
            </div>
            <p className="text-gray-600 text-xs mt-10">This takes 20–60 seconds.</p>
          </div>
        </div>
      </main>
    )
  }

  // ── STATE 3: Results ────────────────────────────────────────────────────────
  const { profile, methodology_used, execution, code } = result
  const badgeColor   = TYPE_BADGE[profile.data_type]   || 'bg-gray-600'
  const bannerColor  = METHOD_BANNER[methodology_used]  || 'bg-gray-900/40 border-gray-500/30 text-gray-300'

  return (
    <main className="flex-1 py-12 px-4">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* A) Data profile card */}
        <div className="glass-effect rounded-xl p-6">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            What Photon found in your data
          </p>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-bold text-white">
              {profile.row_count} rows × {profile.column_count} columns
            </span>
            <span className={`px-2 py-0.5 rounded text-xs font-semibold text-white ${badgeColor}`}>
              {profile.data_type}
            </span>
          </div>
          <p className="text-gray-400 text-sm mb-5">{profile.summary}</p>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500 uppercase">
                <th className="pb-2 pr-6 font-medium">Column</th>
                <th className="pb-2 pr-6 font-medium">Type</th>
                <th className="pb-2 font-medium">Nulls %</th>
              </tr>
            </thead>
            <tbody>
              {profile.columns.map(col => (
                <tr key={col.name} className="border-t border-white/5">
                  <td className="py-1.5 pr-6 font-mono text-xs text-white">{col.name}</td>
                  <td className="py-1.5 pr-6 text-gray-400">{col.dtype}</td>
                  <td className="py-1.5 text-gray-400">{col.null_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* B) Methodology banner */}
        <div className={`rounded-lg px-4 py-2.5 border text-sm font-medium ${bannerColor}`}>
          Applied <span className="font-bold">{methodology_used.replace('_', ' ')}</span> analysis methodology
        </div>

        {/* C) Results */}
        <div className="glass-effect rounded-xl p-6">
          {execution.exit_code === 0 ? (
            <div className="space-y-4">
              {execution.output_image && (
                <img
                  src={`data:image/png;base64,${execution.output_image}`}
                  alt="Analysis chart"
                  className="w-full rounded-lg border border-white/10"
                />
              )}
              {execution.stdout && (
                <pre className="bg-black/50 rounded-lg p-4 text-xs text-green-400 whitespace-pre-wrap overflow-auto max-h-48">
                  {execution.stdout}
                </pre>
              )}
              {!execution.output_image && !execution.stdout && (
                <p className="text-gray-400 text-sm">Execution completed with no output.</p>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border border-red-500/50 bg-red-900/20 rounded-lg p-4">
                <p className="text-red-400 text-xs font-semibold mb-2 uppercase tracking-wide">
                  Execution error
                </p>
                <pre className="text-red-300 text-xs whitespace-pre-wrap overflow-auto max-h-64">
                  {execution.stderr}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* D) Generated code (collapsible) */}
        <div className="glass-effect rounded-xl overflow-hidden">
          <button
            onClick={() => setShowCode(!showCode)}
            className="w-full flex items-center justify-between px-6 py-4 text-sm text-gray-400 hover:text-white transition"
          >
            <span className="font-medium">Code generated by Photon</span>
            <span className="text-xs">{showCode ? '▲ Hide' : '▼ Show generated code'}</span>
          </button>
          {showCode && (
            <pre className="bg-black/50 px-6 pb-6 pt-2 text-xs text-gray-300 whitespace-pre-wrap overflow-auto max-h-[32rem] border-t border-white/10">
              {code}
            </pre>
          )}
        </div>

        <button
          onClick={handleReset}
          className="w-full text-sm text-gray-500 hover:text-gray-300 py-2 transition"
        >
          ← Analyze another dataset
        </button>

      </div>
    </main>
  )
}

export default WorkflowGenerator
