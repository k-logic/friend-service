"use client";

import { useEffect, useRef, useState } from "react";
import { apiFetch, API_BASE } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import StaffLayout from "@/components/StaffLayout";

type Session = { id: number; user_id: number; user_display_name: string | null; user_avatar_url: string | null; persona_id: number; persona_name: string | null; persona_avatar_url: string | null; status: string; updated_at: string };
type Message = { id: number; sender_type: string; sender_id: number; sender_display_name: string | null; title: string | null; content: string; image_url: string | null; created_at: string };
type Template = { id: number; label: string; content: string };

function resolveImageUrl(url: string): string {
  if (url.startsWith("/uploads/")) return `${API_BASE}${url}`;
  return url;
}

function Avatar({ src, name, size = 32 }: { src: string | null | undefined; name: string; size?: number }) {
  if (src) {
    return (
      <img
        src={resolveImageUrl(src)}
        alt={name}
        className="rounded-full object-cover flex-shrink-0"
        style={{ width: size, height: size }}
      />
    );
  }
  const initial = name.charAt(0) || "?";
  return (
    <div
      className="rounded-full bg-gray-300 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold"
      style={{ width: size, height: size }}
    >
      {initial}
    </div>
  );
}

export default function OperatorPage() {
  const { account } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastId, setLastId] = useState(0);
  const [content, setContent] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // セッション一覧取得（全アクティブセッション）
  useEffect(() => {
    apiFetch<Session[]>("/api/v1/sessions").then(setSessions).catch(() => {});
    apiFetch<Template[]>("/api/v1/templates").then(setTemplates).catch(() => {});
  }, []);

  // メッセージポーリング
  useEffect(() => {
    if (!selectedSession) return;
    setMessages([]);
    setLastId(0);

    const poll = async (lid: number) => {
      try {
        const data = await apiFetch<{ messages: Message[]; last_message_id: number | null }>(
          `/api/v1/messages/poll?session_id=${selectedSession.id}&last_message_id=${lid}`
        );
        if (data.messages.length > 0) {
          setMessages((prev) => [...prev, ...data.messages]);
          setLastId(data.last_message_id || 0);
          return data.last_message_id || lid;
        }
        return lid;
      } catch {
        return lid;
      }
    };

    let currentLastId = 0;
    poll(0).then((id) => { currentLastId = id; });

    const interval = setInterval(async () => {
      currentLastId = await poll(currentLastId);
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!content.trim() || !selectedSession || sending) return;
    setSending(true);
    try {
      await apiFetch("/api/v1/messages/send", {
        method: "POST",
        body: JSON.stringify({ session_id: selectedSession.id, content }),
      });
      setContent("");
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSending(false);
    }
  };

  const applyTemplate = (t: Template) => {
    setContent(t.content);
  };

  return (
    <StaffLayout>
      <div className="flex h-screen">
        {/* 左: セッション一覧 */}
        <div className="w-96 border-r bg-white overflow-y-auto">
          <div className="p-3 bg-gray-100 font-bold text-sm border-b">チャット一覧</div>
          <div>
            {sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => setSelectedSession(s)}
                className={`flex items-center gap-3 px-3 py-2.5 cursor-pointer hover:bg-blue-50 border-b ${
                  selectedSession?.id === s.id ? "bg-blue-100" : ""
                }`}
              >
                <Avatar src={s.user_avatar_url} name={s.user_display_name || "U"} size={36} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-medium truncate">{s.user_display_name || `ユーザ #${s.user_id}`}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-gray-500">
                    <Avatar src={s.persona_avatar_url} name={s.persona_name || "P"} size={16} />
                    <span className="truncate">{s.persona_name || `#${s.persona_id}`}</span>
                    <span className="ml-auto flex-shrink-0">{new Date(s.updated_at).toLocaleString("ja-JP", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {sessions.length === 0 && <p className="p-4 text-center text-gray-400 text-sm">セッションなし</p>}
        </div>

        {/* 右: チャット */}
        <div className="flex-1 flex flex-col">
          {selectedSession ? (
            <>
              {/* ヘッダー */}
              <div className="p-3 bg-white border-b text-sm flex items-center gap-3">
                <Avatar src={selectedSession.persona_avatar_url} name={selectedSession.persona_name || "P"} size={28} />
                <span>{selectedSession.persona_name || `ペルソナ #${selectedSession.persona_id}`}</span>
                <span className="text-gray-400">|</span>
                <Avatar src={selectedSession.user_avatar_url} name={selectedSession.user_display_name || "U"} size={28} />
                <span>{selectedSession.user_display_name || `ユーザ #${selectedSession.user_id}`}</span>
              </div>

              {/* メッセージ */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((msg) => {
                  const isPersona = msg.sender_type === "persona";
                  const avatarUrl = isPersona ? selectedSession.persona_avatar_url : selectedSession.user_avatar_url;
                  const senderName = isPersona
                    ? (selectedSession.persona_name || "ペルソナ")
                    : (msg.sender_display_name || `ユーザ #${msg.sender_id}`);
                  return (
                    <div key={msg.id} className={`flex items-end gap-2 ${isPersona ? "justify-end" : "justify-start"}`}>
                      {!isPersona && <Avatar src={avatarUrl} name={senderName} size={28} />}
                      <div className={`max-w-md px-3 py-2 rounded text-sm ${isPersona ? "bg-pink-100" : "bg-orange-100"}`}>
                        <p className="font-bold text-xs mb-1">{senderName}</p>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(msg.created_at).toLocaleTimeString("ja-JP")}
                        </p>
                      </div>
                      {isPersona && <Avatar src={avatarUrl} name={senderName} size={28} />}
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* テンプレート */}
              {templates.length > 0 && (
                <div className="px-4 py-2 bg-gray-50 border-t flex gap-2 flex-wrap">
                  {templates.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => applyTemplate(t)}
                      className="px-3 py-1 bg-gray-200 rounded text-xs hover:bg-gray-300"
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              )}

              {/* 送信フォーム */}
              <div className="p-3 bg-white border-t flex gap-2">
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={3}
                  className="flex-1 border rounded p-2 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-purple-400"
                  placeholder="メッセージを入力..."
                />
                <button
                  onClick={handleSend}
                  disabled={sending || !content.trim()}
                  className="px-4 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 text-sm"
                >
                  送信
                </button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              左のリストからセッションを選択してください
            </div>
          )}
        </div>
      </div>
    </StaffLayout>
  );
}
