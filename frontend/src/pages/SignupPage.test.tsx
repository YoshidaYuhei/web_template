import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { SignupPage } from './SignupPage'
import * as api from '../api/api'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../api/api', () => ({
  signup: vi.fn(),
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

const mockSignup = vi.mocked(api.signup)

function renderSignupPage() {
  return render(
    <MemoryRouter initialEntries={['/signup']}>
      <SignupPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('SignupPage', () => {
  it('メールアドレスとパスワードの入力欄、サインアップボタンが表示される', () => {
    renderSignupPage()
    expect(screen.getByLabelText('メールアドレス')).toBeInTheDocument()
    expect(screen.getByLabelText('パスワード')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'サインアップ' }),
    ).toBeInTheDocument()
  })

  it('メールアドレスが空の状態で送信するとバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderSignupPage()
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(
      screen.getByText('メールアドレスを入力してください'),
    ).toBeInTheDocument()
  })

  it('メールアドレスの形式が不正な場合にバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderSignupPage()
    await user.type(screen.getByLabelText('メールアドレス'), 'invalid')
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(
      screen.getByText('有効なメールアドレスを入力してください'),
    ).toBeInTheDocument()
  })

  it('パスワードが空の状態で送信するとバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(
      screen.getByText('パスワードを入力してください'),
    ).toBeInTheDocument()
  })

  it('パスワードが8文字未満の場合にバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'short')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(
      screen.getByText('パスワードは8文字以上で入力してください'),
    ).toBeInTheDocument()
  })

  it('バリデーションエラー時にAPIリクエストが送信されない', async () => {
    const user = userEvent.setup()
    renderSignupPage()
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(mockSignup).not.toHaveBeenCalled()
  })

  it('正常な入力でサインアップボタンを押すとAPIリクエストが送信される', async () => {
    const user = userEvent.setup()
    mockSignup.mockResolvedValue({
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
    })
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(mockSignup).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'mypassword1',
    })
  })

  it('API成功時にダッシュボード画面に遷移する', async () => {
    const user = userEvent.setup()
    mockSignup.mockResolvedValue({
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
    })
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })

  it('API失敗時(409)に重複メールのエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    mockSignup.mockRejectedValue(
      new api.ApiError(409, {
        detail: 'このメールアドレスは既に登録されています',
      }),
    )
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'existing@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    await waitFor(() => {
      expect(
        screen.getByText('このメールアドレスは既に登録されています'),
      ).toBeInTheDocument()
    })
  })

  it('API失敗時(422)にバリデーションエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    mockSignup.mockRejectedValue(
      new api.ApiError(422, {
        detail: [
          {
            loc: ['body', 'password'],
            msg: 'min_length',
            type: 'value_error',
          },
        ],
      }),
    )
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    await waitFor(() => {
      expect(screen.getByText('入力内容に誤りがあります')).toBeInTheDocument()
    })
  })

  it('ネットワークエラー時にサーバー接続エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    mockSignup.mockRejectedValue(
      new Error(
        'サーバーに接続できません。しばらくしてから再試行してください',
      ),
    )
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    await waitFor(() => {
      expect(
        screen.getByText(
          'サーバーに接続できません。しばらくしてから再試行してください',
        ),
      ).toBeInTheDocument()
    })
  })

  it('API呼び出し中はサインアップボタンがローディング状態になる', async () => {
    const user = userEvent.setup()
    let resolveSignup: (value: api.SignupResponse) => void
    mockSignup.mockReturnValue(
      new Promise((resolve) => {
        resolveSignup = resolve
      }),
    )
    renderSignupPage()
    await user.type(
      screen.getByLabelText('メールアドレス'),
      'user@example.com',
    )
    await user.type(screen.getByLabelText('パスワード'), 'mypassword1')
    await user.click(screen.getByRole('button', { name: 'サインアップ' }))
    expect(screen.getByRole('button', { name: '登録中...' })).toBeDisabled()

    resolveSignup!({
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
    })
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/')
    })
  })
})
