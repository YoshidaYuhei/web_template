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

export async function signup(request: SignupRequest): Promise<SignupResponse> {
  let response: Response
  try {
    response = await fetch('/api/auth/signup/password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
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
