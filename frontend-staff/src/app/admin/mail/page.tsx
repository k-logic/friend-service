"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Campaign = { id: number; type: string; subject: string; status: string; created_at: string };

export default function AdminMailPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [type, setType] = useState("blast");

  useEffect(() => {
    apiFetch<Campaign[]>("/api/v1/admin/mail/campaigns").then(setCampaigns).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!subject || !body) return;
    const c = await apiFetch<Campaign>("/api/v1/admin/mail/campaigns", {
      method: "POST",
      body: JSON.stringify({ type, subject, body }),
    });
    setCampaigns((prev) => [c, ...prev]);
    setSubject(""); setBody("");
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">メール配信管理</h2>
        <div className="bg-white rounded shadow p-4 mb-4 space-y-3">
          <div className="flex gap-3">
            <select value={type} onChange={(e) => setType(e.target.value)} className="border rounded px-2 py-1 text-sm">
              <option value="blast">一斉送信</option>
              <option value="scheduled">予約送信</option>
              <option value="periodic">定期送信</option>
            </select>
            <input placeholder="件名" value={subject} onChange={(e) => setSubject(e.target.value)} className="flex-1 border rounded px-2 py-1 text-sm" />
            <button onClick={handleCreate} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">作成</button>
          </div>
          <textarea placeholder="本文" value={body} onChange={(e) => setBody(e.target.value)} rows={3} className="w-full border rounded p-2 text-sm resize-none" />
        </div>
        <table className="w-full bg-white rounded shadow text-xs">
          <thead className="bg-gray-50"><tr><th className="p-2">ID</th><th className="p-2">種別</th><th className="p-2 text-left">件名</th><th className="p-2">状態</th><th className="p-2">作成日</th></tr></thead>
          <tbody>
            {campaigns.map((c) => (
              <tr key={c.id} className="border-t"><td className="p-2 text-center">{c.id}</td><td className="p-2 text-center">{c.type}</td><td className="p-2">{c.subject}</td><td className="p-2 text-center">{c.status}</td><td className="p-2 text-center">{new Date(c.created_at).toLocaleDateString("ja-JP")}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
