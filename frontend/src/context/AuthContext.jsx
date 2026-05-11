import { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../services/api';
const AuthContext=createContext(null);
export function AuthProvider({children}){ const [user,setUser]=useState(()=>JSON.parse(localStorage.getItem('fit_user')||'null')); const [loading,setLoading]=useState(false);
  async function login(email,password){ const data=await api('/auth/login',{method:'POST',body:{email,password}}); localStorage.setItem('fit_token',data.token); localStorage.setItem('fit_user',JSON.stringify(data.user)); setUser(data.user); }
  async function register(payload){ const data=await api('/auth/register',{method:'POST',body:payload}); localStorage.setItem('fit_token',data.token); localStorage.setItem('fit_user',JSON.stringify(data.user)); setUser(data.user); }
  function logout(){ localStorage.removeItem('fit_token'); localStorage.removeItem('fit_user'); setUser(null); }
  useEffect(()=>{ if(!localStorage.getItem('fit_token')) return; setLoading(true); api('/auth/me').then(setUser).catch(logout).finally(()=>setLoading(false)); },[]);
  return <AuthContext.Provider value={{user,loading,login,register,logout,isAuth:!!user}}>{children}</AuthContext.Provider> }
export const useAuth=()=>useContext(AuthContext);
