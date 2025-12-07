import { useState } from 'react'
import { Search as SearchIcon, Loader2, Database, ExternalLink } from 'lucide-react'
import { searchDatasets } from '../services/api'

function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    
    try {
      const data = await searchDatasets(query, 5)
      setResults(data.results || [])
    } catch (err) {
      setError('Failed to search datasets. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div id="search" className="py-16 px-4 bg-nasa-dark">
      <div className="container mx-auto max-w-5xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Search NASA Datasets</h2>
          <p className="text-gray-400">Ask questions in plain English to find relevant datasets</p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="glass-effect rounded-full p-2 flex items-center gap-2">
            <SearchIcon className="w-6 h-6 text-gray-400 ml-4" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., MODIS surface reflectance 2015, ice cores temperature data..."
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none px-4 py-3"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-nasa-red hover:bg-red-600 text-white px-8 py-3 rounded-full font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Searching...
                </>
              ) : (
                'Search'
              )}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="glass-effect border-red-500 border-2 rounded-lg p-4 mb-8">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white mb-4">
              Found {results.length} results
            </h3>
            {results.map((result, index) => (
              <div key={index} className="glass-effect rounded-lg p-6 hover:bg-white/10 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-5 h-5 text-nasa-red" />
                      <h4 className="text-xl font-semibold text-white">
                        {result.meta?.title || result.meta?.text || result.id}
                      </h4>
                    </div>
                    <p className="text-gray-400 mb-3">
                      {result.meta?.description || result.meta?.summary || 'No description available'}
                    </p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-500">
                        Relevance: <span className="text-nasa-red font-semibold">
                          {(result.score * 100).toFixed(1)}%
                        </span>
                      </span>
                      {result.meta?.url && (
                        <a
                          href={result.meta.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-nasa-red hover:text-red-400 flex items-center gap-1"
                        >
                          View Dataset
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      // Pre-fill workflow generator with this dataset
                      const workflowSection = document.getElementById('generate')
                      if (workflowSection) {
                        workflowSection.scrollIntoView({ behavior: 'smooth' })
                      }
                    }}
                    className="bg-nasa-blue hover:bg-blue-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  >
                    Generate Workflow
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && !error && query && (
          <div className="text-center text-gray-400 py-12">
            <Database className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No results found. Try a different search query.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Search
