// frontend/src/components/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function ProtectedRoute({ children }) {
  const { user, initializing } = useAuth();
  const location = useLocation();

  if (initializing) return null; // hoặc spinner

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}