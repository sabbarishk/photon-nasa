import { Github, Twitter, Mail, ExternalLink } from 'lucide-react'

function Footer() {
  return (
    <footer className="bg-nasa-dark border-t border-gray-800 py-12 px-4 mt-auto">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Photon</h3>
            <p className="text-gray-400 text-sm">
              Natural language query layer and automated workflow generator for NASA open data.
            </p>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="text-gray-400 hover:text-white transition">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white transition">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-white transition">
                  Examples
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">NASA Data</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="https://data.nasa.gov" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition flex items-center gap-1">
                  data.nasa.gov
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a href="https://earthdata.nasa.gov" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition flex items-center gap-1">
                  Earth Data
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a href="https://api.nasa.gov" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition flex items-center gap-1">
                  NASA APIs
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Connect</h4>
            <div className="flex gap-4">
              <a href="#" className="text-gray-400 hover:text-white transition">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
          <p>© 2025 Photon. Open source project for NASA data discovery.</p>
          <p className="mt-4 md:mt-0">
            Built for researchers, by researchers
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
