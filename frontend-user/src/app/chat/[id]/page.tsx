"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import AppLayout from "@/components/AppLayout";

type Message = {
  id: number;
  session_id: number;
  sender_type: string;
  sender_id: number;
  title: string | null;
  content: string;
  image_url: string | null;
  credit_cost: number;
  created_at: string;
};

type Persona = { id: number; name: string; avatar_url: string | null };
type Session = { id: number; persona_id: number };

export default function ChatPage() {
  const params = useParams();
  const { account } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [content, setContent] = useState("");
  const [sending, setSending] = useState(false);
  const [persona, setPersona] = useState<Persona | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sessionId = Number(params.id);

  // セッション情報からペルソナ名を取得
  useEffect(() => {
    (async () => {
      try {
        const sessions = await apiFetch<Session[]>("/api/v1/sessions");
        const session = sessions.find((s) => s.id === sessionId);
        if (session) {
          const p = await apiFetch<Persona>(`/api/v1/personas/${session.persona_id}`);
          setPersona(p);
        }
      } catch {}
    })();
  }, [sessionId]);

  const lastIdRef = useRef(0);

  const poll = async () => {
    try {
      const data = await apiFetch<{ messages: Message[]; last_message_id: number | null }>(
        `/api/v1/messages/poll?session_id=${sessionId}&last_message_id=${lastIdRef.current}`
      );
      if (data.messages.length > 0) {
        setMessages((prev) => {
          const existingIds = new Set(prev.map((m) => m.id));
          const newMsgs = data.messages.filter((m) => !existingIds.has(m.id));
          return newMsgs.length > 0 ? [...prev, ...newMsgs] : prev;
        });
        lastIdRef.current = data.last_message_id || lastIdRef.current;
      }
    } catch {}
  };

  useEffect(() => {
    poll();
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || sending) return;
    setSending(true);
    try {
      await apiFetch("/api/v1/messages/send", {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          content,
        }),
      });
      setContent("");
      await poll();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-screen">
        {/* メッセージ表示エリア */}
        <div className="flex-1 overflow-y-auto p-3 md:p-6 space-y-3 md:space-y-4">
          {messages.map((msg) => {
            const isUser = msg.sender_type === "user";
            return (
              <div key={msg.id} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[75%] md:max-w-md ${isUser ? "order-1" : ""}`}>
                  <p className={`text-xs font-bold mb-1 ${isUser ? "text-right" : ""}`}>
                    {isUser ? account?.display_name || "あなた" : persona?.name || "..."}
                  </p>
                  <div
                    className={`px-4 py-3 rounded-2xl text-sm ${
                      isUser
                        ? "bg-orange-100 text-gray-800 rounded-br-sm"
                        : "bg-pink-100 text-gray-800 rounded-bl-sm"
                    }`}
                  >
                    {msg.image_url && (
                      <img src={msg.image_url} alt="" className="max-w-full md:max-w-xs rounded mb-2" />
                    )}
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  <p className={`text-xs text-gray-400 mt-1 ${isUser ? "text-right" : ""}`}>
                    {new Date(msg.created_at).toLocaleTimeString("ja-JP", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* 入力エリア */}
        <form onSubmit={handleSend} className="border-t bg-white p-2 md:p-4">
          <div className="flex gap-2">
            <textarea
              placeholder="メッセージ"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={2}
              className="flex-1 px-3 py-2 border rounded text-sm resize-none focus:outline-none focus:ring-1 focus:ring-teal-400"
            />
            <button
              type="submit"
              disabled={sending || !content.trim()}
              className="px-4 md:px-6 bg-teal-500 text-white rounded hover:bg-teal-600 disabled:opacity-50 font-medium text-sm"
            >
              送信
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}
