"use client";

import { useEffect, useState, ReactNode } from "react";
import { Account, AuthContext } from "@/lib/auth";
import { apiFetch, clearToken } from "@/lib/api";

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("staff_token");
    if (!token) {
      setLoading(false);
      return;
    }
    apiFetch<Account>("/api/v1/staff/auth/me")
      .then((acc) => {
        setAccount(acc);
      })
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ account, setAccount, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
