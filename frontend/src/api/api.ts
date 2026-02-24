export interface SignupRequest {
  email: string
  password: string
}

export interface AccountResponse {
  id: number
  email: string
  is_active: boolean
  has_password: boolean
  oauth_providers: string[]
  passkey_count: number
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface SignupResponse {
  account: AccountResponse
  token: TokenResponse
}

export interface ErrorResponse {
  detail: string
}

export interface ValidationErrorResponse {
  detail: Array<{
    loc: (string | number)[]
    msg: string
    type: string
  }>
}

export class ApiError extends Error {
  status: number
  body: ErrorResponse | ValidationErrorResponse

  constructor(status: number, body: ErrorResponse | ValidationErrorResponse) {
    super(`API error: ${status}`)
    this.status = status
    this.body = body
  }
}

export type LoginRequest = SignupRequest
export type LoginResponse = SignupResponse

async function apiRequest<T>(url: string, options: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(url, options)
  } catch {
    throw new Error('サーバーに接続できません。しばらくしてから再試行してください')
  }

  if (!response.ok) {
    let body: ErrorResponse | ValidationErrorResponse
    try {
      body = await response.json()
    } catch {
      throw new Error('サーバーに接続できません。しばらくしてから再試行してください')
    }
    throw new ApiError(response.status, body)
  }

  return response.json()
}

export async function signup(request: SignupRequest): Promise<SignupResponse> {
  return apiRequest<SignupResponse>('/api/auth/signup/password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
}

export async function login(request: LoginRequest): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/api/auth/login/password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: token }),
  })
}

export async function logout(accessToken: string, refreshTokenValue: string): Promise<void> {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    })
  } catch {
    // ログアウトはベストエフォート：失敗してもクライアント側の認証状態はクリアされる
  }
}
