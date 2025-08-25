// frontend/src/pages/LoginPage.jsx
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErr('');
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (error) {
      setErr(error?.response?.data?.detail || 'Login failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-gray-50">
      <form onSubmit={onSubmit} className="w-full max-w-sm bg-white shadow p-6 rounded-xl">
        <h1 className="text-xl font-semibold mb-4">Sign in</h1>
        {err && <div className="mb-3 text-sm text-red-600">{err}</div>}
        <label className="block text-sm mb-1">Username</label>
        <input
          className="w-full border rounded-md px-3 py-2 mb-3"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />
        <label className="block text-sm mb-1">Password</label>
        <input
          type="password"
          className="w-full border rounded-md px-3 py-2 mb-4"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          disabled={submitting}
          className="w-full rounded-md bg-blue-600 text-white py-2 hover:bg-blue-700 disabled:opacity-60"
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}