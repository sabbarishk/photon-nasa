import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { DatasetProvider } from './context/DatasetContext'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Search from './components/Search'
import WorkflowGenerator from './components/WorkflowGenerator'
import Footer from './components/Footer'

function App() {
  return (
    <DatasetProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <Routes>
            <Route path="/" element={
              <>
                <Hero />
                <Search />
                <WorkflowGenerator />
              </>
            } />
            <Route path="/search" element={<Search />} />
            <Route path="/generate" element={<WorkflowGenerator />} />
          </Routes>
          <Footer />
        </div>
      </Router>
    </DatasetProvider>
  )
}

export default App
