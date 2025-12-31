import { useEffect, useState } from 'react'
import './App.css'

interface DatabaseHealth {
  status: string
  error: string | null
}

interface HealthResponse {
  status: string
  database: DatabaseHealth
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch('/api/health')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data: HealthResponse = await response.json()
        setHealth(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
  }, [])

  if (loading) {
    return (
      <div className="health-container">
        <div className="health-card">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="health-container">
        <div className="health-card error">
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="health-container">
      <div className={`health-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
        <h1>Health Check</h1>
        <div className="status-section">
          <h2>Application Status</h2>
          <p className={`status ${health?.status}`}>{health?.status}</p>
        </div>
        <div className="status-section">
          <h2>Database Status</h2>
          <p className={`status ${health?.database.status === 'connected' ? 'healthy' : 'unhealthy'}`}>
            {health?.database.status}
          </p>
          {health?.database.error && (
            <p className="error-message">{health.database.error}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
