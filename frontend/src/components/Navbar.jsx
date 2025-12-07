import { Link } from 'react-router-dom'
import { Rocket, Menu, X } from 'lucide-react'
import { useState } from 'react'

function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="glass-effect sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Rocket className="w-8 h-8 text-nasa-red" />
            <span className="text-2xl font-bold text-white">Photon</span>
            <span className="text-sm text-gray-400 hidden md:inline">NASA Data Portal</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#search" className="text-gray-300 hover:text-white transition">
              Search
            </a>
            <a href="#generate" className="text-gray-300 hover:text-white transition">
              Generate
            </a>
            <a href="#docs" className="text-gray-300 hover:text-white transition">
              Documentation
            </a>
            <button className="bg-nasa-red hover:bg-red-600 text-white px-6 py-2 rounded-full transition">
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-white"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-3">
            <a href="#search" className="block text-gray-300 hover:text-white transition">
              Search
            </a>
            <a href="#generate" className="block text-gray-300 hover:text-white transition">
              Generate
            </a>
            <a href="#docs" className="block text-gray-300 hover:text-white transition">
              Documentation
            </a>
            <button className="w-full bg-nasa-red hover:bg-red-600 text-white px-6 py-2 rounded-full transition">
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
