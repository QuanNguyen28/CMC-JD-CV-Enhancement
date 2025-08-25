// src/AuthContext.jsx
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import api from "./api";

const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Khôi phục token ngay lập tức -> tránh bị redirect sớm
  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (t) {
      setIsAuthenticated(true);
      api.defaults.headers.common.Authorization = `Bearer ${t}`;
      (async () => {
        try {
          const { data } = await api.get("/auth/me");
          setUser(data);
        } catch {
          localStorage.removeItem("access_token");
          delete api.defaults.headers.common.Authorization;
          setIsAuthenticated(false);
          setUser(null);
        } finally {
          setLoading(false);
        }
      })();
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (username, password) => {
    // FastAPI OAuth2 (x-www-form-urlencoded)
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    form.append("grant_type", "password");

    const { data } = await api.post("/auth/token", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const token = data.access_token;
    localStorage.setItem("access_token", token);
    api.defaults.headers.common.Authorization = `Bearer ${token}`;

    const me = await api.get("/auth/me");
    setUser(me.data);
    setIsAuthenticated(true);
    return me.data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    delete api.defaults.headers.common.Authorization;
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  return (
    <AuthCtx.Provider value={{ user, isAuthenticated, loading, login, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}