import { Navigate, Outlet } from 'react-router-dom'
import { ApiError } from '@/services/api/client'
import { useMe } from '../hooks/useAuth'

export function RequireAuth() {
  const { data, error, isPending } = useMe()
  if (isPending) return <p role="status" className="p-8 text-center text-ink-muted">Cargando…</p>
  if (data) return <Outlet />
  if (error instanceof ApiError && error.status === 401) return <Navigate to="/login" replace />
  return <p role="alert" className="p-8 text-center text-danger">{error?.message ?? 'No se pudo comprobar la sesión.'}</p>
}
