import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import {
  type AccountResponse,
  type SignupResponse,
  refreshToken as refreshTokenApi,
  logout as logoutApi,
} from '../api/api'

interface AuthContextType {
  accessToken: string | null
  refreshToken: string | null
  account: AccountResponse | null
  isAuthenticated: boolean
  isLoading: boolean
  loginAction: (response: SignupResponse) => void
  logoutAction: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

const STORAGE_KEYS = {
  accessToken: 'access_token',
  refreshToken: 'refresh_token',
  account: 'account',
} as const

function parseAccessTokenExp(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [accessToken, setAccessToken] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEYS.accessToken),
  )
  const [refreshTokenValue, setRefreshToken] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEYS.refreshToken),
  )
  const [account, setAccount] = useState<AccountResponse | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEYS.account)
    return stored ? JSON.parse(stored) : null
  })
  const [isLoading, setIsLoading] = useState(true)

  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearAuth = useCallback(() => {
    setAccessToken(null)
    setRefreshToken(null)
    setAccount(null)
    localStorage.removeItem(STORAGE_KEYS.accessToken)
    localStorage.removeItem(STORAGE_KEYS.refreshToken)
    localStorage.removeItem(STORAGE_KEYS.account)
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current)
      refreshTimerRef.current = null
    }
  }, [])

  const scheduleRefresh = useCallback(
    (token: string, currentRefreshToken: string) => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current)
      }

      const exp = parseAccessTokenExp(token)
      if (!exp) return

      const performRefresh = () => {
        refreshTokenApi(currentRefreshToken)
          .then((result) => {
            setAccessToken(result.access_token)
            setRefreshToken(result.refresh_token)
            localStorage.setItem(STORAGE_KEYS.accessToken, result.access_token)
            localStorage.setItem(STORAGE_KEYS.refreshToken, result.refresh_token)
            scheduleRefresh(result.access_token, result.refresh_token)
          })
          .catch(() => {
            clearAuth()
            navigate('/login')
          })
      }

      const delay = exp - Date.now() - 60_000
      if (delay <= 0) {
        performRefresh()
        return
      }

      refreshTimerRef.current = setTimeout(performRefresh, delay)
    },
    [clearAuth, navigate],
  )

  const loginAction = useCallback(
    (response: SignupResponse) => {
      const { account: acc, token } = response
      setAccessToken(token.access_token)
      setRefreshToken(token.refresh_token)
      setAccount(acc)
      localStorage.setItem(STORAGE_KEYS.accessToken, token.access_token)
      localStorage.setItem(STORAGE_KEYS.refreshToken, token.refresh_token)
      localStorage.setItem(STORAGE_KEYS.account, JSON.stringify(acc))
      scheduleRefresh(token.access_token, token.refresh_token)
    },
    [scheduleRefresh],
  )

  const logoutAction = useCallback(() => {
    if (accessToken && refreshTokenValue) {
      logoutApi(accessToken, refreshTokenValue).catch(() => {})
    }
    clearAuth()
    navigate('/login')
  }, [accessToken, refreshTokenValue, clearAuth, navigate])

  // Initialize: check stored tokens and set up refresh
  useEffect(() => {
    if (accessToken && refreshTokenValue) {
      scheduleRefresh(accessToken, refreshTokenValue)
    }
    setIsLoading(false)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current)
      }
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        refreshToken: refreshTokenValue,
        account,
        isAuthenticated: !!accessToken && !!account,
        isLoading,
        loginAction,
        logoutAction,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
