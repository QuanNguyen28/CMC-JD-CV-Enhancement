// frontend/src/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from 'react';
import api from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  const fetchMe = async () => {
    try {
      const { data } = await api.get('/auth/me');
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setInitializing(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) fetchMe();
    else setInitializing(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (username, password) => {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);

    const { data } = await api.post('/auth/token', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    localStorage.setItem('access_token', data.access_token);
    await fetchMe();
    return data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, initializing, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);