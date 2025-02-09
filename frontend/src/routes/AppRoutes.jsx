import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from '../components/auth/Login';
import Callback from '../components/auth/Callback';
import MatchList from '../components/matching/MatchList';
import MatchDetails from '../components/matching/MatchDetails';
import UserProfile from '../components/profile/UserProfile';

const AppRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/callback" element={<Callback />} />
        
        {/* Protected Routes */}
        <Route 
          path="/matches" 
          element={
            <ProtectedRoute>
              <MatchList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/matches/:id" 
          element={
            <ProtectedRoute>
              <MatchDetails />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <UserProfile />
            </ProtectedRoute>
          } 
        />
        
        {/* Redirects */}
        <Route path="/" element={<Navigate to="/matches" />} />
      </Routes>
    </BrowserRouter>
  );
}; 