import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from './DashboardPage'

const mockLogoutAction = vi.fn()

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    account: {
      id: 1,
      email: 'user@example.com',
      is_active: true,
      has_password: true,
      oauth_providers: [],
      passkey_count: 0,
      created_at: '2025-01-01T00:00:00',
    },
    logoutAction: mockLogoutAction,
  }),
}))

describe('DashboardPage', () => {
  it('ダッシュボード画面が表示される', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    )
    expect(screen.getByText('ダッシュボード')).toBeInTheDocument()
  })

  it('ログイン中のメールアドレスが表示される', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    )
    expect(screen.getByText('user@example.com')).toBeInTheDocument()
  })

  it('ログアウトボタンが表示される', () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    )
    expect(
      screen.getByRole('button', { name: 'ログアウト' }),
    ).toBeInTheDocument()
  })

  it('ログアウトボタンをクリックするとlogoutActionが呼ばれる', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    )
    await user.click(screen.getByRole('button', { name: 'ログアウト' }))
    expect(mockLogoutAction).toHaveBeenCalled()
  })
})
