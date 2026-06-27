import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Workspace from './pages/Workspace'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/analyze" element={<Workspace />} />
      </Routes>
    </Router>
  )
}
