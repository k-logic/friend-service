"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import StaffLayout from "@/components/StaffLayout";

type User = { id: number; email: string; display_name: string; credit_balance: number; status: string; created_at: string };

export default function AdminUsersPage() {
  const { account } = useAuth();
  const isAdmin = account?.role === "admin";
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");

  const load = (email?: string) => {
    const q = email ? `?email=${encodeURIComponent(email)}` : "";
    apiFetch<User[]>(`/api/v1/admin/users${q}`).then(setUsers).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const toggleStatus = async (u: User) => {
    const newStatus = u.status === "active" ? "suspended" : "active";
    await apiFetch(`/api/v1/admin/users/${u.id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: newStatus }),
    });
    load(search);
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">ユーザ管理</h2>

        <div className="flex gap-2 mb-4">
          <input
            placeholder="メールアドレスで検索"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm w-80"
          />
          <button onClick={() => load(search)} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">検索</button>
        </div>

        <table className="w-full bg-white rounded shadow text-xs">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">メール</th>
              <th className="p-2 text-left">名前</th>
              <th className="p-2">残高</th>
              <th className="p-2">ステータス</th>
              {isAdmin && <th className="p-2">操作</th>}
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t">
                <td className="p-2">{u.id}</td>
                <td className="p-2">{u.email}</td>
                <td className="p-2">{u.display_name}</td>
                <td className="p-2 text-center">{u.credit_balance}</td>
                <td className="p-2 text-center">
                  <span className={u.status === "active" ? "text-green-600" : "text-red-600"}>{u.status}</span>
                </td>
                {isAdmin && (
                  <td className="p-2 text-center">
                    <button onClick={() => toggleStatus(u)} className="text-blue-600 hover:underline">
                      {u.status === "active" ? "停止" : "有効化"}
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
