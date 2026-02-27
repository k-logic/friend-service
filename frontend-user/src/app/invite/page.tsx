"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch, setToken } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type VerifyResponse = {
  email: string;
};

export default function InvitePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAccount } = useAuth();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [info, setInfo] = useState<VerifyResponse | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("招待リンクが無効です");
      setStatus("error");
      return;
    }

    apiFetch<VerifyResponse>(`/api/v1/invitations/${token}/verify`)
      .then((data) => {
        setInfo(data);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.message);
        setStatus("error");
      });
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!displayName.trim() || !token) return;

    setSubmitting(true);
    setError("");

    try {
      const data = await apiFetch<{ access_token: string }>(
        `/api/v1/invitations/${token}/register`,
        {
          method: "POST",
          body: JSON.stringify({ display_name: displayName.trim() }),
        }
      );

      setToken(data.access_token);

      const account = await apiFetch<any>("/api/v1/auth/me");
      setAccount(account);

      router.push("/search");
    } catch (err: any) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50">
        <p className="text-gray-500">読み込み中...</p>
      </div>
    );
  }

  if (status === "error" && !info) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <h1 className="text-xl font-bold text-red-600 mb-4">エラー</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <a
            href="/login"
            className="text-purple-600 hover:underline text-sm"
          >
            ログインページへ
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-xl font-bold text-center mb-2">ようこそ!</h1>
        <p className="text-sm text-gray-500 text-center mb-6">
          ニックネームを決めてサービスをはじめましょう
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">
              メールアドレス
            </label>
            <input
              type="email"
              value={info?.email || ""}
              disabled
              className="w-full border rounded px-3 py-2 text-sm bg-gray-50 text-gray-500"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">
              ニックネーム
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="あなたのニックネームを入力"
              className="w-full border rounded px-3 py-2 text-sm"
              required
              autoFocus
            />
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={submitting || !displayName.trim()}
            className="w-full py-2.5 bg-purple-600 text-white rounded font-bold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? "設定中..." : "サービスをはじめる"}
          </button>
        </form>
      </div>
    </div>
  );
}
