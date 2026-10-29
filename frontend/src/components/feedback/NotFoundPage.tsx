import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <main className="flex h-full flex-col items-center justify-center gap-3">
      <h1 className="text-2xl font-medium">Página no encontrada</h1>
      <Link to="/" className="text-accent underline focus-visible:outline-2 focus-visible:outline-accent">
        Volver al inicio
      </Link>
    </main>
  )
}
