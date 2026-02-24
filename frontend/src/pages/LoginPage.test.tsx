import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { LoginPage } from './LoginPage'
import * as api from '../api/api'

const mockNavigate = vi.fn()
const mockLoginAction = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../api/api', () => ({
  login: vi.fn(),
  ApiError: class extends Error {
    status: number
    body: unknown
    constructor(status: number, body: unknown) {
      super(`API error: ${status}`)
      this.status = status
      this.body = body
    }
  },
}))

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    loginAction: mockLoginAction,
  }),
}))

const mockLogin = vi.mocked(api.login)

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <LoginPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

const mockResponse: api.LoginResponse = {
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
    access_token: 'token',
    refresh_token: 'refresh',
    token_type: 'bearer',
  },
}

describe('LoginPage', () => {
  it('メールアドレスとパスワードの入力欄、ログインボタンが表示される', () => {
    renderLoginPage()
    expect(screen.getByLabelText('メールアドレス')).toBeInTheDocument()
    expect(screen.getByLabelText('パスワード')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'ログイン' }),
    ).toBeInTheDocument()
  })

  it('メールアドレスが空の状態で送信するとバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderLoginPage()
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(
      screen.getByText('メールアドレスを入力してください'),
    ).toBeInTheDocument()
  })

  it('メールアドレスの形式が不正な場合にバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderLoginPage()
    await user.type(screen.getByLabelText('メールアドレス'), 'invalid')
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(
      screen.getByText('有効なメールアドレスを入力してください'),
    ).toBeInTheDocument()
  })

  it('パスワードが空の状態で送信するとバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(
      screen.getByText('パスワードを入力してください'),
    ).toBeInTheDocument()
  })

  it('バリデーションエラー時にAPIリクエストが送信されない', async () => {
    const user = userEvent.setup()
    renderLoginPage()
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('正常な入力でログインボタンを押すとAPIリクエストが送信される', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValue(mockResponse)
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(mockLogin).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'mypassword1',
    })
  })

  it('API成功時にloginActionが呼ばれダッシュボードに遷移する', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValue(mockResponse)
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    await waitFor(() => {
      expect(mockLoginAction).toHaveBeenCalledWith(mockResponse)
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('API失敗時(401)に認証エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValue(
      new api.ApiError(401, {
        detail: 'メールアドレスまたはパスワードが正しくありません',
      }),
    )
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'wrongpassword')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    await waitFor(() => {
      expect(
        screen.getByText('メールアドレスまたはパスワードが正しくありません'),
      ).toBeInTheDocument()
    })
  })

  it('ネットワークエラー時にサーバー接続エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValue(
      new Error(
        'サーバーに接続できません。しばらくしてから再試行してください',
      ),
    )
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    await waitFor(() => {
      expect(
        screen.getByText(
          'サーバーに接続できません。しばらくしてから再試行してください',
        ),
      ).toBeInTheDocument()
    })
  })

  it('API呼び出し中はログインボタンがローディング状態になる', async () => {
    const user = userEvent.setup()
    let resolveLogin: (value: api.LoginResponse) => void
    mockLogin.mockReturnValue(
      new Promise((resolve) => {
        resolveLogin = resolve
      }),
    )
    renderLoginPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))
    expect(screen.getByRole('button', { name: 'ログイン中...' })).toBeDisabled()

    resolveLogin!(mockResponse)
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('サインアップへのリンクが表示される', () => {
    renderLoginPage()
    expect(screen.getByText('サインアップ')).toBeInTheDocument()
  })
})
