import { describe, it, expect, vi, beforeEach } from 'vitest'
import { signup, ApiError } from './api'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

beforeEach(() => {
  mockFetch.mockReset()
})

describe('signup', () => {
  it('正常なリクエストでSignupResponseが返却される', async () => {
    const mockResponse = {
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
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 'bearer',
      },
    }
    mockFetch.mockResolvedValue({
      ok: true,
      status: 201,
      json: () => Promise.resolve(mockResponse),
    })

    const result = await signup({
      email: 'user@example.com',
      password: 'mypassword1',
    })

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith('/api/auth/signup/password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'user@example.com',
        password: 'mypassword1',
      }),
    })
  })

  it('409エラー時にApiErrorがスローされる', async () => {
    const errorBody = { detail: 'このメールアドレスは既に登録されています' }
    mockFetch.mockResolvedValue({
      ok: false,
      status: 409,
      json: () => Promise.resolve(errorBody),
    })

    try {
      await signup({ email: 'existing@example.com', password: 'mypassword1' })
      expect.fail('should have thrown')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError)
      const apiErr = err as ApiError
      expect(apiErr.status).toBe(409)
      expect(apiErr.body).toEqual(errorBody)
    }
  })

  it('422エラー時にApiErrorがスローされる', async () => {
    const errorBody = {
      detail: [
        { loc: ['body', 'password'], msg: 'min_length', type: 'value_error' },
      ],
    }
    mockFetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: () => Promise.resolve(errorBody),
    })

    try {
      await signup({ email: 'user@example.com', password: 'short' })
      expect.fail('should have thrown')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError)
      const apiErr = err as ApiError
      expect(apiErr.status).toBe(422)
      expect(apiErr.body).toEqual(errorBody)
    }
  })

  it('ネットワークエラー時に適切な例外がスローされる', async () => {
    mockFetch.mockRejectedValue(new TypeError('Failed to fetch'))

    try {
      await signup({ email: 'user@example.com', password: 'mypassword1' })
      expect.fail('should have thrown')
    } catch (err) {
      expect(err).not.toBeInstanceOf(ApiError)
      expect(err).toBeInstanceOf(Error)
      expect((err as Error).message).toBe(
        'サーバーに接続できません。しばらくしてから再試行してください',
      )
    }
  })
})
