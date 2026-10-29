import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import { Providers } from './providers'
import { routes } from './router'

const router = createBrowserRouter(routes)

export default function App() {
  return (
    <Providers>
      <RouterProvider router={router} />
    </Providers>
  )
}
