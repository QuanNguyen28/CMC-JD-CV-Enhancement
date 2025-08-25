import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Dashboard from "./components/Dashboard";
import ComposePage from "./pages/ComposePage";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";
import Roles from "./components/Roles";

export default function App(){
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage/>} />
          <Route element={<ProtectedRoute/>}>
            <Route path="/" element={<Dashboard/>} />
            <Route path="/compose" element={<ComposePage/>} />
            <Route path="/roles" element={<Roles/>} />
          </Route>
          <Route path="*" element={<NotFound/>}/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}