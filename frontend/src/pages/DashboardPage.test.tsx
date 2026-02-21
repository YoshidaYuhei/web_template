import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DashboardPage } from './DashboardPage'

describe('DashboardPage', () => {
  it('プレースホルダーのダッシュボード画面が表示される', () => {
    render(<DashboardPage />)
    expect(screen.getByText('ダッシュボード')).toBeInTheDocument()
  })
})
