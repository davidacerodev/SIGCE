import { LogOut, NotebookPen } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useLogout, useMe } from '@/features/auth/hooks/useAuth'

export function TopBar({ children }: { children?: ReactNode }) {
  const navigate = useNavigate()
  const { data: user } = useMe()
  const logout = useLogout()

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-line bg-surface px-4">
      <Link to="/" className="flex items-center gap-2 font-serif text-lg font-semibold text-accent">
        <NotebookPen className="size-5" aria-hidden /> Marginalia
      </Link>
      <div className="flex min-w-0 flex-1 items-center gap-3">{children}</div>
      {user && (
        <div className="flex items-center gap-2 text-sm text-ink-muted">
          <span className="hidden max-w-40 truncate sm:inline">{user.display_name}</span>
          <button
            aria-label="Cerrar sesión"
            onClick={() => logout.mutate(undefined, { onSuccess: () => navigate('/login') })}
            className="rounded p-1.5 hover:bg-accent-soft"
          >
            <LogOut className="size-4" aria-hidden />
          </button>
        </div>
      )}
    </header>
  )
}
