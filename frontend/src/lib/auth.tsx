"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authAPI } from "@/lib/api";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_id: string;
  avatar_url?: string;
}

interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  subscription_plan: string;
}

interface AuthContextType {
  user: User | null;
  tenant: Tenant | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    company_name: string;
    company_slug: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("vf_access_token");
    if (token) {
      authAPI
        .me()
        .then(({ data }) => setUser(data))
        .catch(() => {
          localStorage.removeItem("vf_access_token");
          localStorage.removeItem("vf_refresh_token");
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await authAPI.login({ email, password });
    localStorage.setItem("vf_access_token", data.tokens.access_token);
    localStorage.setItem("vf_refresh_token", data.tokens.refresh_token);
    setUser(data.user);
    setTenant(data.tenant);
  };

  const register = async (formData: {
    email: string;
    password: string;
    full_name: string;
    company_name: string;
    company_slug: string;
  }) => {
    const { data } = await authAPI.register(formData);
    localStorage.setItem("vf_access_token", data.tokens.access_token);
    localStorage.setItem("vf_refresh_token", data.tokens.refresh_token);
    setUser(data.user);
    setTenant(data.tenant);
  };

  const logout = () => {
    localStorage.removeItem("vf_access_token");
    localStorage.removeItem("vf_refresh_token");
    setUser(null);
    setTenant(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tenant,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
