import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import type { SignupResponse } from '../api/api'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../api/api', () => ({
  refreshToken: vi.fn().mockResolvedValue({
    access_token: 'new-access',
    refresh_token: 'new-refresh',
    token_type: 'bearer',
  }),
  logout: vi.fn().mockResolvedValue(undefined),
}))

// Generate a token with exp = now + 1 hour (fits in 32-bit setTimeout)
function makeTestToken() {
  const header = btoa(JSON.stringify({ alg: 'HS256' }))
  const exp = Math.floor(Date.now() / 1000) + 3600
  const payload = btoa(JSON.stringify({ sub: '1', exp }))
  return `${header}.${payload}.test-signature`
}


function TestConsumer() {
  const { isAuthenticated, account, loginAction, logoutAction, isLoading } =
    useAuth()
  return (
    <div>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="authenticated">{String(isAuthenticated)}</div>
      <div data-testid="email">{account?.email ?? 'none'}</div>
      <button
        onClick={() =>
          loginAction({
            account: {
              id: 1,
              email: 'user@example.com',
              is_active: true,
              has_password: true,
              oauth_providers: [],
              passkey_count: 0,
              created_at: '2025-01-01T00:00:00',
            },
            token: {
              access_token: makeTestToken(),
              refresh_token: 'refresh-token',
              token_type: 'bearer',
            },
          } as SignupResponse)
        }
      >
        login
      </button>
      <button onClick={logoutAction}>logout</button>
    </div>
  )
}

function renderWithAuth() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
})

afterEach(() => {
  cleanup()
})

describe('AuthContext', () => {
  it('初期状態では未認証', async () => {
    renderWithAuth()
    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })
    expect(screen.getByTestId('authenticated').textContent).toBe('false')
    expect(screen.getByTestId('email').textContent).toBe('none')
  })

  it('loginActionでトークンとアカウントが保存される', async () => {
    const user = userEvent.setup()
    renderWithAuth()
    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })

    await user.click(screen.getByText('login'))

    expect(screen.getByTestId('authenticated').textContent).toBe('true')
    expect(screen.getByTestId('email').textContent).toBe('user@example.com')
    expect(localStorage.getItem('access_token')).toBeTruthy()
    expect(localStorage.getItem('refresh_token')).toBe('refresh-token')
    expect(localStorage.getItem('account')).toContain('user@example.com')
  })

  it('logoutActionでトークンとアカウントがクリアされる', async () => {
    const user = userEvent.setup()
    renderWithAuth()
    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })

    await user.click(screen.getByText('login'))
    expect(screen.getByTestId('authenticated').textContent).toBe('true')

    await user.click(screen.getByText('logout'))

    expect(screen.getByTestId('authenticated').textContent).toBe('false')
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('account')).toBeNull()
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('localStorageに保存されたトークンで初期化される', async () => {
    localStorage.setItem('access_token', makeTestToken())
    localStorage.setItem('refresh_token', 'stored-refresh')
    localStorage.setItem(
      'account',
      JSON.stringify({
        id: 1,
        email: 'stored@example.com',
        is_active: true,
        has_password: true,
        oauth_providers: [],
        passkey_count: 0,
        created_at: '2025-01-01T00:00:00',
      }),
    )

    renderWithAuth()
    await waitFor(() => {
      expect(screen.getByTestId('loading').textContent).toBe('false')
    })

    expect(screen.getByTestId('authenticated').textContent).toBe('true')
    expect(screen.getByTestId('email').textContent).toBe('stored@example.com')
  })
})
