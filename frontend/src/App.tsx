import { Routes, Route } from 'react-router-dom'
import { SignupPage } from './pages/SignupPage'
import { DashboardPage } from './pages/DashboardPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/signup" element={<SignupPage />} />
    </Routes>
  )
}

export default App
