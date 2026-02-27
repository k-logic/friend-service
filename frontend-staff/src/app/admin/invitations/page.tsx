"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Invitation = {
  id: number;
  token: string;
  invite_url: string;
  email: string;
  expires_at: string;
  used_at: string | null;
  created_at: string;
};

export default function InvitationsPage() {
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [copiedId, setCopiedId] = useState<number | null>(null);

  useEffect(() => {
    apiFetch<Invitation[]>("/api/v1/invitations").then(setInvitations).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!email) return;
    setError("");
    try {
      const inv = await apiFetch<Invitation>("/api/v1/invitations", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setInvitations((prev) => [inv, ...prev]);
      setEmail("");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const copyUrl = (inv: Invitation) => {
    navigator.clipboard.writeText(inv.invite_url);
    setCopiedId(inv.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatDate = (s: string) => new Date(s).toLocaleString("ja-JP");

  const getStatus = (inv: Invitation) => {
    if (inv.used_at) return "使用済み";
    if (new Date(inv.expires_at) < new Date()) return "期限切れ";
    return "有効";
  };

  const getStatusColor = (inv: Invitation) => {
    if (inv.used_at) return "text-gray-500";
    if (new Date(inv.expires_at) < new Date()) return "text-red-500";
    return "text-green-600";
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">招待管理</h2>

        <div className="bg-white rounded shadow p-4 mb-6">
          <h3 className="text-sm font-bold mb-3">新規招待トークン発行</h3>
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="text-xs text-gray-500">メールアドレス</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
                className="block border rounded px-2 py-1 text-sm w-full max-w-md"
              />
            </div>
            <button
              onClick={handleCreate}
              disabled={!email}
              className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 disabled:opacity-50"
            >
              発行
            </button>
          </div>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </div>

        <table className="w-full bg-white rounded shadow text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">メール</th>
              <th className="p-2">状態</th>
              <th className="p-2 text-left">有効期限</th>
              <th className="p-2 text-left">発行日時</th>
              <th className="p-2">URL</th>
            </tr>
          </thead>
          <tbody>
            {invitations.map((inv) => (
              <tr key={inv.id} className="border-t">
                <td className="p-2">{inv.id}</td>
                <td className="p-2">{inv.email}</td>
                <td className={`p-2 text-center font-bold ${getStatusColor(inv)}`}>
                  {getStatus(inv)}
                </td>
                <td className="p-2 text-xs text-gray-500">
                  {formatDate(inv.expires_at)}
                </td>
                <td className="p-2 text-xs text-gray-500">
                  {formatDate(inv.created_at)}
                </td>
                <td className="p-2 text-center">
                  <button
                    onClick={() => copyUrl(inv)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {copiedId === inv.id ? "コピー済み" : "URLコピー"}
                  </button>
                </td>
              </tr>
            ))}
            {invitations.length === 0 && (
              <tr>
                <td colSpan={6} className="p-4 text-center text-gray-400">
                  招待トークンがありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
