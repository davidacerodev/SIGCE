import { NotebookPen } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { useLogin, useMe, useRegister } from '../hooks/useAuth'

export function LoginPage() {
  const navigate = useNavigate()
  const me = useMe()
  const login = useLogin()
  const register = useRegister()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')

  if (me.data) return <Navigate to="/" replace />

  const action = mode === 'login' ? login : register
  const submit = (e: FormEvent) => {
    e.preventDefault()
    const done = { onSuccess: () => navigate('/') }
    if (mode === 'login') login.mutate({ email, password }, done)
    else register.mutate({ email, password, display_name: name }, done)
  }
  const input = 'rounded-md border border-line bg-white px-3 py-2'

  return (
    <main className="flex h-full items-center justify-center p-4">
      <form onSubmit={submit} className="flex w-full max-w-sm flex-col gap-4 rounded-card border border-line bg-surface p-6">
        <h1 className="flex items-center gap-2 text-2xl text-accent"><NotebookPen className="size-6" aria-hidden /> Marginalia</h1>
        <h2 className="text-lg">{mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</h2>
        {mode === 'register' && (
          <label className="flex flex-col gap-1 text-sm">Nombre
            <input required value={name} maxLength={120} onChange={(e) => setName(e.target.value)} className={input} />
          </label>
        )}
        <label className="flex flex-col gap-1 text-sm">Correo
          <input required type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className={input} />
        </label>
        <label className="flex flex-col gap-1 text-sm">Contraseña
          <input required type="password" minLength={8} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password} onChange={(e) => setPassword(e.target.value)} className={input} />
        </label>
        {action.error && <p role="alert" className="text-sm text-danger">{action.error.message}</p>}
        <Button type="submit" variant="primary" disabled={action.isPending}>{mode === 'login' ? 'Entrar' : 'Registrarme'}</Button>
        <button type="button" className="text-sm text-accent underline" onClick={() => { login.reset(); register.reset(); setMode(mode === 'login' ? 'register' : 'login') }}>
          {mode === 'login' ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
        </button>
      </form>
    </main>
  )
}
