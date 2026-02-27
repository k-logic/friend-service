"use client";

import { createContext, useContext } from "react";

export type Account = {
  id: number;
  email: string;
  display_name: string;
  credit_balance: number;
  status: string;
  avatar_url: string | null;
};

export type AuthContextType = {
  account: Account | null;
  setAccount: (account: Account | null) => void;
  loading: boolean;
};

export const AuthContext = createContext<AuthContextType>({
  account: null,
  setAccount: () => {},
  loading: true,
});

export function useAuth() {
  return useContext(AuthContext);
}
