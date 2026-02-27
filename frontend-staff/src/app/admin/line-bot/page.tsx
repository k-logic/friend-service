"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Bot = { id: number; line_bot_id: string; memo: string | null; webhook_url: string | null; is_active: boolean; subscriber_count: number; monthly_delivery_count: number };

export default function LineBotPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [botId, setBotId] = useState("");
  const [webhook, setWebhook] = useState("");

  useEffect(() => {
    apiFetch<Bot[]>("/api/v1/admin/line-bot").then(setBots).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!botId) return;
    const b = await apiFetch<Bot>("/api/v1/admin/line-bot", {
      method: "POST",
      body: JSON.stringify({ line_bot_id: botId, webhook_url: webhook || null }),
    });
    setBots((prev) => [...prev, b]);
    setBotId(""); setWebhook("");
  };

  const toggle = async (id: number) => {
    const updated = await apiFetch<Bot>(`/api/v1/admin/line-bot/${id}/toggle`, { method: "PATCH" });
    setBots((prev) => prev.map((b) => (b.id === id ? updated : b)));
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">LINE Bot管理</h2>
        <div className="bg-white rounded shadow p-4 mb-4 flex gap-3 items-end">
          <div><label className="text-xs text-gray-500">Bot ID</label><input value={botId} onChange={(e) => setBotId(e.target.value)} className="block border rounded px-2 py-1 text-sm" /></div>
          <div className="flex-1"><label className="text-xs text-gray-500">Webhook URL</label><input value={webhook} onChange={(e) => setWebhook(e.target.value)} className="block w-full border rounded px-2 py-1 text-sm" /></div>
          <button onClick={handleCreate} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">追加</button>
        </div>
        <table className="w-full bg-white rounded shadow text-xs">
          <thead className="bg-gray-50"><tr><th className="p-2">ID</th><th className="p-2 text-left">Bot ID</th><th className="p-2 text-left">Webhook</th><th className="p-2">登録数</th><th className="p-2">配信数</th><th className="p-2">状態</th><th className="p-2">操作</th></tr></thead>
          <tbody>
            {bots.map((b) => (
              <tr key={b.id} className="border-t"><td className="p-2 text-center">{b.id}</td><td className="p-2">{b.line_bot_id}</td><td className="p-2 truncate max-w-xs">{b.webhook_url}</td><td className="p-2 text-center">{b.subscriber_count}</td><td className="p-2 text-center">{b.monthly_delivery_count}</td><td className="p-2 text-center"><span className={b.is_active ? "text-green-600" : "text-red-600"}>{b.is_active ? "有効" : "無効"}</span></td><td className="p-2 text-center"><button onClick={() => toggle(b.id)} className="text-blue-600 hover:underline">切替</button></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
