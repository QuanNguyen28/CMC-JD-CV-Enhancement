// src/pages/LoginPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import LoginForm from "../components/LoginForm"; // form của bạn nhận onSubmit(username, password)

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate("/", { replace: true });
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (username, password) => {
    try {
      setErr("");
      await login(username, password);
      navigate("/", { replace: true });
    } catch (e) {
      setErr("Đăng nhập thất bại. Kiểm tra tài khoản/mật khẩu hoặc server.");
    }
  };

  return <LoginForm onSubmit={handleSubmit} error={err} />;
}