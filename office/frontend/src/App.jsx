import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import { AppShell } from './components'
import { AdminPage, Dashboard, FilesPage, UploadPage } from './pages'
import { Login } from './login'

function Protected({ admin = false }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="full-loading">Loading Office Portal…</div>
  if (!user) return <Navigate to="/login" replace />
  if (admin && user.role !== 'admin') return <Navigate to="/" replace />
  return <AppShell><Outlet /></AppShell>
}

export default function App() {
  return <Routes><Route path="/login" element={<Login />} /><Route element={<Protected />}><Route path="/" element={<Dashboard />} /><Route path="/files/personal" element={<FilesPage />} /><Route path="/files/common" element={<FilesPage folder="common" />} /><Route path="/upload" element={<UploadPage />} /></Route><Route element={<Protected admin />}><Route path="/admin" element={<AdminPage />} /></Route><Route path="*" element={<Navigate to="/" replace />} /></Routes>
}
