import { Search as SearchIcon, Sparkles } from 'lucide-react'

function Hero() {
  return (
    <div className="gradient-bg py-20 px-4">
      <div className="container mx-auto text-center">
        <div className="flex justify-center mb-6">
          <div className="bg-nasa-red/20 p-4 rounded-full">
            <Sparkles className="w-12 h-12 text-nasa-red" />
          </div>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
          Discover NASA Data
          <br />
          <span className="text-nasa-red">In Plain English</span>
        </h1>
        
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Search thousands of NASA datasets using natural language and automatically generate 
          analysis-ready Jupyter notebooks in seconds.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a
            href="#search"
            className="bg-nasa-red hover:bg-red-600 text-white px-8 py-4 rounded-full font-semibold transition flex items-center gap-2"
          >
            <SearchIcon className="w-5 h-5" />
            Start Searching
          </a>
          <a
            href="#generate"
            className="glass-effect text-white px-8 py-4 rounded-full font-semibold transition hover:bg-white/10"
          >
            Generate Workflow
          </a>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-4xl mx-auto">
          <div className="glass-effect p-6 rounded-lg">
            <div className="text-4xl font-bold text-nasa-red mb-2">10K+</div>
            <div className="text-gray-300">NASA Datasets</div>
          </div>
          <div className="glass-effect p-6 rounded-lg">
            <div className="text-4xl font-bold text-nasa-red mb-2">&lt;5s</div>
            <div className="text-gray-300">Notebook Generation</div>
          </div>
          <div className="glass-effect p-6 rounded-lg">
            <div className="text-4xl font-bold text-nasa-red mb-2">100%</div>
            <div className="text-gray-300">Free & Open Source</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Hero
