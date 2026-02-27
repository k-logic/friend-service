"use client";

import { useEffect, useState, ReactNode } from "react";
import { Account, AuthContext } from "@/lib/auth";
import { apiFetch, clearToken } from "@/lib/api";

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    apiFetch<Account>("/api/v1/auth/me")
      .then(setAccount)
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ account, setAccount, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
