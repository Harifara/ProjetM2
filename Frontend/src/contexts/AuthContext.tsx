import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface AuthContextType {
  user: any | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<any>; // 🔹 retourne l'utilisateur
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { toast } = useToast();

  // 🔹 Rafraîchir l'utilisateur avec le token existant
  const refreshUser = async () => {
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const me = await authApi.getMe();
      setUser(me);
    } catch (err: any) {
      console.warn('Token expiré ou invalide:', err);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 🔹 Login corrigé pour retourner l'utilisateur immédiatement
  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authApi.login(username, password);
      const accessToken = data.access || data.token;
      if (!accessToken) throw new Error('Token manquant dans la réponse');

      localStorage.setItem('token', accessToken);
      setToken(accessToken);

      const me = await authApi.getMe();
      setUser(me);

      return me; // 🔹 retourne l'utilisateur pour utilisation immédiate
    } catch (err: any) {
      throw new Error(err?.detail || err?.message || 'Erreur lors de la connexion');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    try {
      authApi.logout();
    } catch {}
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth doit être utilisé à l\'intérieur de AuthProvider');
  return context;
};
