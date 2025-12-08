import { useState } from 'react'
import { FileCode, Loader2, Download, Eye, CheckCircle, Play, Image as ImageIcon } from 'lucide-react'
import { generateWorkflow, executeNotebook } from '../services/api'

function WorkflowGenerator() {
  const [formData, setFormData] = useState({
    datasetUrl: '',
    format: 'csv',
    variable: '',
    title: ''
  })
  const [notebook, setNotebook] = useState(null)
  const [loading, setLoading] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState(null)
  const [error, setError] = useState(null)
  const [showPreview, setShowPreview] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const data = await generateWorkflow(
        formData.datasetUrl,
        formData.format,
        formData.variable,
        formData.title
      )
      setNotebook(data)
      setShowPreview(true)
    } catch (err) {
      setError('Failed to generate workflow. Please check your inputs and try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const executeCode = async () => {
    if (!notebook || !notebook.notebook) return
    
    setExecuting(true)
    setError(null)
    setExecutionResult(null)
    
    try {
      // Parse notebook to get code
      const nb = typeof notebook.notebook === 'string' 
        ? JSON.parse(notebook.notebook) 
        : notebook.notebook
      
      // Extract code from cells
      const code = nb.cells
        .filter(cell => cell.cell_type === 'code')
        .map(cell => Array.isArray(cell.source) ? cell.source.join('') : cell.source)
        .join('\n\n')
      
      // Execute code
      const result = await executeNotebook(code, 120)  // 2 minute timeout
      setExecutionResult(result)
      
      if (result.exit_code !== 0 && result.stderr) {
        setError(`Execution completed with warnings: ${result.stderr.substring(0, 200)}`)
      }
    } catch (err) {
      setError('Failed to execute notebook. Make sure the dataset URL is accessible.')
      console.error(err)
    } finally {
      setExecuting(false)
    }
  }

  const downloadNotebook = () => {
    if (!notebook || !notebook.notebook) return
    
    // notebook.notebook is already a JSON string from the API
    const notebookContent = typeof notebook.notebook === 'string' 
      ? notebook.notebook 
      : JSON.stringify(notebook.notebook, null, 2)
    
    const blob = new Blob([notebookContent], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formData.title || 'workflow'}.ipynb`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div id="generate" className="py-16 px-4 bg-nasa-dark/50">
      <div className="container mx-auto max-w-5xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Generate Analysis Workflow</h2>
          <p className="text-gray-400">
            Automatically create a Jupyter notebook for your NASA dataset
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form */}
          <div className="glass-effect rounded-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-gray-300 mb-2 font-semibold">
                  Dataset URL <span className="text-nasa-red">*</span>
                </label>
                <input
                  type="url"
                  value={formData.datasetUrl}
                  onChange={(e) => setFormData({ ...formData, datasetUrl: e.target.value })}
                  placeholder="https://data.giss.nasa.gov/..."
                  required
                  className="w-full bg-white/5 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-nasa-red transition"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2 font-semibold">
                  Dataset Format <span className="text-nasa-red">*</span>
                </label>
                <select
                  value={formData.format}
                  onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                  className="w-full bg-white/5 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-nasa-red transition"
                >
                  <option value="csv">CSV</option>
                  <option value="netcdf">NetCDF</option>
                  <option value="hdf5">HDF5</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-300 mb-2 font-semibold">
                  Variable to Analyze <span className="text-nasa-red">*</span>
                </label>
                <input
                  type="text"
                  value={formData.variable}
                  onChange={(e) => setFormData({ ...formData, variable: e.target.value })}
                  placeholder="e.g., temperature, J-D, surface_temp"
                  required
                  className="w-full bg-white/5 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-nasa-red transition"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-2 font-semibold">
                  Workflow Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="My NASA Data Analysis"
                  className="w-full bg-white/5 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-nasa-red transition"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-nasa-red hover:bg-red-600 text-white px-8 py-4 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileCode className="w-5 h-5" />
                    Generate Notebook
                  </>
                )}
              </button>
            </form>

            {error && (
              <div className="mt-4 border-2 border-red-500 rounded-lg p-4">
                <p className="text-red-400">{error}</p>
              </div>
            )}
          </div>

          {/* Preview / Result */}
          <div className="glass-effect rounded-lg p-8">
            {!notebook ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
                <FileCode className="w-16 h-16 mb-4 opacity-50" />
                <p className="text-lg">Your generated notebook will appear here</p>
                <p className="text-sm mt-2">Fill in the form and click "Generate Notebook"</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-400 mb-4">
                  <CheckCircle className="w-6 h-6" />
                  <span className="font-semibold">Notebook generated successfully!</span>
                </div>

                <div className="bg-white/5 rounded-lg p-4 mb-4">
                  <h4 className="text-white font-semibold mb-2">Details:</h4>
                  <div className="space-y-2 text-sm text-gray-400">
                    <p><span className="text-gray-500">Format:</span> {formData.format.toUpperCase()}</p>
                    <p><span className="text-gray-500">Variable:</span> {formData.variable}</p>
                    <p><span className="text-gray-500">Cells:</span> {(() => {
                      try {
                        const nb = typeof notebook.notebook === 'string' 
                          ? JSON.parse(notebook.notebook) 
                          : notebook.notebook
                        return nb?.cells?.length || 0
                      } catch {
                        return 0
                      }
                    })()}</p>
                  </div>
                </div>

                <div className="flex gap-3 flex-wrap">
                  <button
                    onClick={downloadNotebook}
                    className="flex-1 min-w-[150px] bg-nasa-blue hover:bg-blue-800 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Download .ipynb
                  </button>
                  <button
                    onClick={executeCode}
                    disabled={executing}
                    className="flex-1 min-w-[150px] bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {executing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5" />
                        Run & Visualize
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className="flex-1 bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-lg font-semibold transition flex items-center justify-center gap-2"
                  >
                    <Eye className="w-5 h-5" />
                    {showPreview ? 'Hide' : 'Preview'}
                  </button>
                </div>

                {showPreview && notebook.notebook && (
                  <div className="mt-4">
                    <h4 className="text-white font-semibold mb-2">Code Preview:</h4>
                    <div className="bg-black/50 rounded-lg p-4 max-h-96 overflow-auto">
                      <pre className="text-xs text-gray-300 whitespace-pre-wrap">
                        {typeof notebook.notebook === 'string' 
                          ? notebook.notebook 
                          : JSON.stringify(notebook.notebook, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {executionResult && (
                  <div className="mt-4 space-y-4">
                    <div className="flex items-center gap-2 text-green-400">
                      <ImageIcon className="w-5 h-5" />
                      <h4 className="text-white font-semibold">Visualizations Generated!</h4>
                    </div>

                    {/* Display generated images */}
                    {executionResult.images && executionResult.images.length > 0 && (
                      <div className="space-y-4">
                        {executionResult.images.map((img, idx) => (
                          <div key={idx} className="bg-white/5 rounded-lg p-4">
                            <p className="text-sm text-gray-400 mb-2">{img.filename}</p>
                            <img 
                              src={img.data} 
                              alt={`Visualization ${idx + 1}`}
                              className="w-full rounded-lg border border-gray-600"
                            />
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Display console output if available */}
                    {executionResult.stdout && (
                      <div className="bg-black/50 rounded-lg p-4">
                        <h5 className="text-white font-semibold mb-2 text-sm">Output:</h5>
                        <pre className="text-xs text-green-400 whitespace-pre-wrap max-h-48 overflow-auto">
                          {executionResult.stdout}
                        </pre>
                      </div>
                    )}

                    {/* Display errors if any */}
                    {executionResult.stderr && executionResult.exit_code !== 0 && (
                      <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
                        <h5 className="text-red-400 font-semibold mb-2 text-sm">Errors:</h5>
                        <pre className="text-xs text-red-300 whitespace-pre-wrap max-h-48 overflow-auto">
                          {executionResult.stderr}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Example Section */}
        <div className="mt-16 glass-effect rounded-lg p-8">
          <h3 className="text-2xl font-bold text-white mb-4">Example Workflows</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setFormData({
                datasetUrl: 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv',
                format: 'csv',
                variable: 'J-D',
                title: 'GISS Temperature Analysis'
              })}
              className="text-left bg-white/5 hover:bg-white/10 rounded-lg p-4 transition"
            >
              <div className="text-nasa-red font-semibold mb-2">GISS Temperature</div>
              <div className="text-sm text-gray-400">Global temperature anomalies (CSV)</div>
            </button>
            <button
              onClick={() => setFormData({
                datasetUrl: 'https://example.nasa.gov/modis/data.nc',
                format: 'netcdf',
                variable: 'surface_reflectance',
                title: 'MODIS Surface Reflectance'
              })}
              className="text-left bg-white/5 hover:bg-white/10 rounded-lg p-4 transition"
            >
              <div className="text-nasa-red font-semibold mb-2">MODIS Data</div>
              <div className="text-sm text-gray-400">Surface reflectance (NetCDF)</div>
            </button>
            <button
              onClick={() => setFormData({
                datasetUrl: 'https://example.nasa.gov/ice-cores.csv',
                format: 'csv',
                variable: 'co2_ppm',
                title: 'Ice Core CO2 Analysis'
              })}
              className="text-left bg-white/5 hover:bg-white/10 rounded-lg p-4 transition"
            >
              <div className="text-nasa-red font-semibold mb-2">Ice Core Data</div>
              <div className="text-sm text-gray-400">CO2 measurements (CSV)</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowGenerator
