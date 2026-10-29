import type { RouteObject } from 'react-router-dom'
import { NotFoundPage } from '@/components/feedback/NotFoundPage'
import { RequireAuth } from '@/features/auth/components/RequireAuth'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { HomePage } from '@/features/notebooks/pages/HomePage'
import { WorkspacePage } from '@/features/notebooks/pages/WorkspacePage'

export const routes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/notebooks/:id', element: <WorkspacePage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]
