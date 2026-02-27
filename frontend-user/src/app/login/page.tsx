"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, setToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const { setAccount } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const endpoint = isRegister ? "/api/v1/auth/register" : "/api/v1/auth/login";
      const body = isRegister
        ? { email, password, display_name: displayName }
        : { email, password };
      const data = await apiFetch<{ access_token: string }>(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      });
      setToken(data.access_token);
      const account = await apiFetch<any>("/api/v1/auth/me");
      setAccount(account);
      router.push("/search");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-teal-50 to-white px-4">
      <div className="w-full max-w-md p-6 md:p-8 bg-white rounded-xl shadow-lg">
        <h1 className="text-2xl md:text-3xl font-bold text-center text-teal-500 mb-6 md:mb-8">Friend</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <input
              type="text"
              placeholder="表示名"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
              required
            />
          )}
          <input
            type="email"
            placeholder="メールアドレス"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
            required
          />
          <input
            type="password"
            placeholder="パスワード"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
            required
          />

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full py-2.5 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium"
          >
            {isRegister ? "新規登録" : "ログイン"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          {isRegister ? "既にアカウントをお持ちの方" : "アカウントをお持ちでない方"}
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="ml-1 text-teal-500 hover:underline"
          >
            {isRegister ? "ログイン" : "新規登録"}
          </button>
        </p>
      </div>
    </div>
  );
}
