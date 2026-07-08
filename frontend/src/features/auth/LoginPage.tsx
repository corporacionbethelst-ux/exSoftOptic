import { FormEvent, useState } from 'react';
import { Glasses } from 'lucide-react';
import { ApiError } from '../../services';
import { env } from '../../config/env';
import { useAuth } from './AuthContext';

export function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState(env.demoUsername);
  const [password, setPassword] = useState(env.demoPassword);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="brand-mark"><Glasses size={34} /></div>
        <p className="eyebrow">ExSoftOptic</p>
        <h1>Panel administrativo para ópticas</h1>
        <p className="muted">Usa las credenciales del seed base para comenzar.</p>
        <form onSubmit={onSubmit} className="form-stack">
          <label>
            Usuario
            <input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
          </label>
          <label>
            Contraseña
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
          </label>
          {error ? <div className="alert error">{error}</div> : null}
          <button className="primary-button" disabled={loading}>{loading ? 'Ingresando…' : 'Entrar'}</button>
        </form>
      </section>
    </main>
  );
}
