"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Template = { id: number; label: string; content: string };

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [label, setLabel] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    apiFetch<Template[]>("/api/v1/templates").then(setTemplates).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!label || !content) return;
    const t = await apiFetch<Template>("/api/v1/templates", {
      method: "POST",
      body: JSON.stringify({ label, content }),
    });
    setTemplates((prev) => [...prev, t]);
    setLabel(""); setContent("");
  };

  const handleDelete = async (id: number) => {
    await apiFetch(`/api/v1/templates/${id}`, { method: "DELETE" });
    setTemplates((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">テンプレート管理</h2>

        <div className="bg-white rounded shadow p-4 mb-6 space-y-3">
          <div className="flex gap-3">
            <input placeholder="ラベル (例: %OPE01%)" value={label} onChange={(e) => setLabel(e.target.value)} className="border rounded px-2 py-1 text-sm w-48" />
            <button onClick={handleCreate} className="px-4 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700">追加</button>
          </div>
          <textarea placeholder="テンプレート内容" value={content} onChange={(e) => setContent(e.target.value)} rows={3} className="w-full border rounded p-2 text-sm resize-none" />
        </div>

        <div className="space-y-2">
          {templates.map((t) => (
            <div key={t.id} className="bg-white rounded shadow p-3 flex justify-between items-start">
              <div>
                <span className="font-mono text-purple-600 text-sm font-bold">{t.label}</span>
                <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">{t.content}</p>
              </div>
              <button onClick={() => handleDelete(t.id)} className="text-red-500 text-xs hover:underline ml-4">削除</button>
            </div>
          ))}
        </div>
      </div>
    </StaffLayout>
  );
}
