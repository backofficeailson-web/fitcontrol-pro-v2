import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
export default function PrivateRoute({children}){ const {isAuth,loading}=useAuth(); if(loading) return <div className="center">Carregando...</div>; return isAuth?children:<Navigate to="/login" replace/>; }
