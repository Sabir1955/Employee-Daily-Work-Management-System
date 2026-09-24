import { useEffect, useRef, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { AlertCircle, CheckCircle2, ChevronRight, CloudUpload, File, FileText, FolderOpen, LayoutDashboard, LogOut, Menu, ShieldCheck, Users, X } from 'lucide-react'
import { useAuth } from './context/AuthContext'
import { initials } from './utils'

export function Logo() {
  return <div className="brand"><div className="brand-mark">O</div><div><strong>Office Portal</strong><span>Secure workspace</span></div></div>
}

export function AppShell({ children }) {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/files/personal', label: 'My files', icon: FolderOpen },
    { to: '/files/common', label: 'Common files', icon: Users },
    { to: '/upload', label: 'Upload files', icon: CloudUpload },
  ]
  if (user?.role === 'admin') links.push({ to: '/admin', label: 'Administration', icon: ShieldCheck })
  const signOut = async () => { await logout(); navigate('/login') }
  return <div className="app-shell">
    <aside className={open ? 'sidebar open' : 'sidebar'}>
      <div className="sidebar-top"><Logo /><button className="icon-button mobile-only" onClick={() => setOpen(false)} aria-label="Close menu"><X size={20} /></button></div>
      <nav>{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)}><Icon size={18} />{label}<ChevronRight className="nav-chevron" size={15} /></NavLink>)}</nav>
      <div className="sidebar-bottom"><div className="security-note"><ShieldCheck size={17} /><span>Your files are protected<br />by secure sessions.</span></div><button className="logout-link" onClick={signOut}><LogOut size={17} />Sign out</button></div>
    </aside>
    {open && <button className="scrim" onClick={() => setOpen(false)} aria-label="Close navigation" />}
    <main className="main"><header className="topbar"><button className="icon-button mobile-only" onClick={() => setOpen(true)} aria-label="Open menu"><Menu /></button><div className="topbar-spacer" /><div className="user-menu"><div className="avatar">{initials(user?.username)}</div><div><strong>{user?.username}</strong><small>{user?.role === 'admin' ? 'Administrator' : 'Employee'}</small></div></div></header><div className="content">{children}</div></main>
  </div>
}

export function PageHeader({ eyebrow, title, description, action }) {
  return <div className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>
}

export function StatCard({ label, value, caption, icon: Icon, accent = '' }) {
  return <div className={`stat-card ${accent}`}><div className="stat-icon"><Icon size={20} /></div><div><span>{label}</span><strong>{value}</strong>{caption && <small>{caption}</small>}</div></div>
}

export function EmptyState({ title, text, action }) {
  return <div className="empty-state"><div className="empty-icon"><File size={25} /></div><h3>{title}</h3><p>{text}</p>{action}</div>
}

export function Toast({ toast, onClose }) {
  useEffect(() => { if (toast) { const timer = setTimeout(onClose, 4500); return () => clearTimeout(timer) } }, [toast, onClose])
  if (!toast) return null
  return <div className={`toast ${toast.type === 'error' ? 'toast-error' : ''}`}><span>{toast.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}</span>{toast.message}<button onClick={onClose} aria-label="Dismiss"><X size={16} /></button></div>
}

export function UploadDropzone({ files, setFiles, uploading }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)
  const addFiles = (list) => setFiles((current) => [...current, ...Array.from(list).filter((file) => !current.some((existing) => existing.name === file.name && existing.size === file.size))])
  return <div className={`dropzone ${dragging ? 'dragging' : ''}`} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); addFiles(event.dataTransfer.files) }} onClick={() => inputRef.current?.click()}><input ref={inputRef} type="file" multiple hidden onChange={(event) => addFiles(event.target.files)} disabled={uploading} /><div className="upload-icon"><CloudUpload size={27} /></div><h3>Drop files here, or <span>browse</span></h3><p>Maximum file size is 500 MB. Executable files are not allowed.</p>{files.length > 0 && <div className="selected-files" onClick={(event) => event.stopPropagation()}>{files.map((file, index) => <div className="selected-file" key={`${file.name}-${index}`}><FileText size={17} /><span>{file.name}<small>{(file.size / 1024 / 1024).toFixed(2)} MB</small></span><button type="button" onClick={() => setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index))} disabled={uploading}><X size={15} /></button></div>)}</div>}</div>
}
