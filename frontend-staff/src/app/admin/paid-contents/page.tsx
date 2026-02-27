"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type PaidContent = { id: number; title: string; description: string | null; price: number; is_active: boolean };

export default function PaidContentsPage() {
  const [contents, setContents] = useState<PaidContent[]>([]);
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");

  useEffect(() => {
    apiFetch<PaidContent[]>("/api/v1/admin/paid-contents").then(setContents).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!title || !price) return;
    const c = await apiFetch<PaidContent>("/api/v1/admin/paid-contents", {
      method: "POST",
      body: JSON.stringify({ title, price: Number(price) }),
    });
    setContents((prev) => [c, ...prev]);
    setTitle(""); setPrice("");
  };

  const toggle = async (id: number) => {
    const updated = await apiFetch<PaidContent>(`/api/v1/admin/paid-contents/${id}/toggle`, { method: "PATCH" });
    setContents((prev) => prev.map((c) => (c.id === id ? updated : c)));
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">有料情報管理</h2>
        <div className="bg-white rounded shadow p-4 mb-4 flex gap-3 items-end">
          <div><label className="text-xs text-gray-500">タイトル</label><input value={title} onChange={(e) => setTitle(e.target.value)} className="block border rounded px-2 py-1 text-sm" /></div>
          <div><label className="text-xs text-gray-500">価格</label><input type="number" value={price} onChange={(e) => setPrice(e.target.value)} className="block border rounded px-2 py-1 text-sm w-24" /></div>
          <button onClick={handleCreate} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">追加</button>
        </div>
        <table className="w-full bg-white rounded shadow text-sm">
          <thead className="bg-gray-50"><tr><th className="p-2 text-left">ID</th><th className="p-2 text-left">タイトル</th><th className="p-2">価格</th><th className="p-2">状態</th><th className="p-2">操作</th></tr></thead>
          <tbody>
            {contents.map((c) => (
              <tr key={c.id} className="border-t"><td className="p-2">{c.id}</td><td className="p-2">{c.title}</td><td className="p-2 text-center">{c.price}pt</td><td className="p-2 text-center">{c.is_active ? "有効" : "無効"}</td><td className="p-2 text-center"><button onClick={() => toggle(c.id)} className="text-blue-600 hover:underline text-xs">切替</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
