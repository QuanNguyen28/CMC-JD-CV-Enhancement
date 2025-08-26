import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense } from "react";
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
        <Suspense
          fallback={
            <div className="min-h-screen grid place-items-center text-gray-500">
              Loading…
            </div>
          }
        >
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />

            {/* Private area */}
            <Route element={<ProtectedRoute />}> 
              <Route path="/" element={<Layout />}> 
                {/* default landing */}
                <Route index element={<Dashboard />} />
                {/* explicit alias */}
                <Route path="dashboard" element={<Dashboard />} />

                <Route path="compose" element={<ComposePage />} />
                <Route path="interview" element={<InterviewPage />} />
                <Route path="retrieve" element={<RetrievePage />} />
                <Route path="roles" element={<Roles />} />

                {/* in-layout 404 */}
                <Route path="*" element={<NotFound />} />
              </Route>
            </Route>

            {/* top-level fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}