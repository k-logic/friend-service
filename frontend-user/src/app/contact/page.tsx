"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

export default function ContactPage() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await apiFetch("/api/v1/inquiries", {
        method: "POST",
        body: JSON.stringify({ subject, body }),
      });
      setSent(true);
      setSubject("");
      setBody("");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <AppLayout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <h2 className="text-xl font-bold mb-6">お問い合わせ</h2>

        {sent ? (
          <div className="bg-white rounded-xl shadow p-4 md:p-8 text-center">
            <p className="text-teal-600 font-medium mb-2">お問い合わせを送信しました</p>
            <p className="text-sm text-gray-500">担当者からの返信をお待ちください</p>
            <button
              onClick={() => setSent(false)}
              className="mt-4 text-sm text-teal-500 hover:underline"
            >
              新しいお問い合わせ
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">件名</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-400"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">内容</label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-teal-400"
                required
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              type="submit"
              className="w-full py-2.5 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium"
            >
              送信
            </button>
          </form>
        )}
      </div>
    </AppLayout>
  );
}
