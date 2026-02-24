import { useAuth } from '../contexts/AuthContext'

export function DashboardPage() {
  const { account, logoutAction } = useAuth()

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="space-y-6 text-center">
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        {account && (
          <p className="text-gray-600">{account.email}</p>
        )}
        <button
          type="button"
          onClick={logoutAction}
          className="rounded-md bg-gray-600 px-4 py-2 text-white hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none"
        >
          ログアウト
        </button>
      </div>
    </div>
  )
}
