import { useState } from 'react'
import { ArrowRight, Eye, EyeOff, LockKeyhole, ShieldCheck } from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { getErrorMessage } from './api'

export function Login() {
  const { user, login, loading } = useAuth(); const navigate = useNavigate(); const [form, setForm] = useState({ username: '', password: '' }); const [show, setShow] = useState(false); const [error, setError] = useState(''); const [submitting, setSubmitting] = useState(false)
  if (loading) return <div className="full-loading">Loading Office Portal…</div>
  if (user) return <Navigate to="/" replace />
  const submit = async (event) => { event.preventDefault(); setError(''); setSubmitting(true); try { await login(form); navigate('/') } catch (requestError) { setError(getErrorMessage(requestError)) } finally { setSubmitting(false) } }
  return <div className="login-page"><div className="login-brand"><div className="brand-mark">O</div><div><strong>Office Portal</strong><span>Secure workspace</span></div></div><div className="login-card"><div className="login-icon"><LockKeyhole size={23} /></div><h1>Welcome back</h1><p>Sign in to access your workspace.</p><form onSubmit={submit}><label className="field"><span>Username</span><input autoFocus required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} placeholder="Enter your username" /></label><label className="field"><span>Password</span><div className="password-input"><input required type={show ? 'text' : 'password'} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Enter your password" /><button type="button" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></label>{error && <div className="form-error">{error}</div>}<button className="button button-primary login-button" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'}<ArrowRight size={17} /></button></form></div><div className="login-footer"><ShieldCheck size={16} />Your connection is protected with secure session authentication.</div></div>
}
