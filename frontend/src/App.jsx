import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Dashboard from "./components/Dashboard";
import ComposePage from "./pages/ComposePage";
import InterviewPage from "./pages/InterviewPage";
import RetrievePage from "./pages/RetrievePage";
import Roles from "./components/Roles";

import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />

          {/* Private + Layout có Outlet */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="compose" element={<ComposePage />} />
              <Route path="interview" element={<InterviewPage />} />
              <Route path="retrieve" element={<RetrievePage />} />
              <Route path="roles" element={<Roles />} />
            </Route>
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}