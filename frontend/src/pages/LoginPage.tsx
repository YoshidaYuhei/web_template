import { type FormEvent, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login, ApiError } from '../api/api'
import { useAuth } from '../contexts/AuthContext'

function validateEmail(email: string): string | null {
  if (!email) return 'メールアドレスを入力してください'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return '有効なメールアドレスを入力してください'
  return null
}

function validatePassword(password: string): string | null {
  if (!password) return 'パスワードを入力してください'
  return null
}

export function LoginPage() {
  const navigate = useNavigate()
  const { loginAction } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setApiError(null)

    const emailErr = validateEmail(email)
    const passwordErr = validatePassword(password)
    setEmailError(emailErr)
    setPasswordError(passwordErr)

    if (emailErr || passwordErr) return

    setLoading(true)
    try {
      const response = await login({ email, password })
      loginAction(response)
      navigate('/')
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setApiError('メールアドレスまたはパスワードが正しくありません')
        } else {
          setApiError('エラーが発生しました')
        }
      } else if (err instanceof Error) {
        setApiError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-8">
        <h1 className="text-center text-3xl font-bold text-gray-900">
          ログイン
        </h1>

        {apiError && (
          <div
            role="alert"
            className="rounded-md bg-red-50 p-4 text-sm text-red-700"
          >
            {apiError}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-6">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              メールアドレス
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setEmailError(null)
              }}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none"
            />
            {emailError && (
              <p className="mt-1 text-sm text-red-600">{emailError}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              パスワード
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setPasswordError(null)
              }}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none"
            />
            {passwordError && (
              <p className="mt-1 text-sm text-red-600">{passwordError}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none disabled:opacity-50"
          >
            {loading ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600">
          アカウントをお持ちでない方は
          <Link to="/signup" className="text-indigo-600 hover:text-indigo-500">
            サインアップ
          </Link>
        </p>
      </div>
    </div>
  )
}
