"use client";

import { useEffect, useState } from "react";
import { apiFetch, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import LoadingSpinner from "@/components/LoadingSpinner";
import Link from "next/link";

type Session = {
  id: number;
  persona_id: number;
  status: string;
  last_persona_message: string | null;
  created_at: string;
  updated_at: string;
};

type Persona = {
  id: number;
  name: string;
  age: number | null;
  avatar_url: string | null;
};

export default function MessagesPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [personas, setPersonas] = useState<Record<number, Persona>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const allSessions = await apiFetch<Session[]>("/api/v1/sessions");
        const sessions = allSessions.filter((s) => s.status === "active");
        setSessions(sessions);

        const personaMap: Record<number, Persona> = {};
        const uniqueIds = [...new Set(sessions.map((s) => s.persona_id))];
        await Promise.all(
          uniqueIds.map(async (pid) => {
            try {
              const p = await apiFetch<Persona>(`/api/v1/personas/${pid}`);
              personaMap[pid] = p;
            } catch {}
          })
        );
        setPersonas(personaMap);
      } catch {}
      setLoading(false);
    })();
  }, []);

  return (
    <AppLayout>
      <div className="p-4 md:p-8">
        <h2 className="text-xl font-bold mb-6">メッセージ</h2>
        {loading ? <LoadingSpinner /> : (
        <div className="space-y-3">
          {sessions.map((s) => {
            const persona = personas[s.persona_id];
            return (
              <Link
                key={s.id}
                href={`/chat/${s.id}`}
                className="flex items-center gap-4 p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="w-14 h-14 rounded-full bg-gray-200 overflow-hidden flex-shrink-0">
                  {persona?.avatar_url ? (
                    <img src={toFullUrl(persona.avatar_url)!} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xl text-gray-400">
                      {persona?.name?.[0] || "?"}
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">
                      {persona?.name || "不明"}
                      {persona?.age && <span className="text-gray-500 text-sm ml-2">{persona.age}歳</span>}
                    </p>
                    <span className="text-xs text-gray-400">
                      {new Date(s.updated_at).toLocaleDateString("ja-JP", { month: "numeric", day: "numeric" })}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 truncate">
                    {s.last_persona_message
                      ? s.last_persona_message.slice(0, 15) + (s.last_persona_message.length > 15 ? "..." : "")
                      : "メッセージはまだありません"}
                  </p>
                </div>
              </Link>
            );
          })}
          {sessions.length === 0 && (
            <p className="text-center text-gray-400 py-12">メッセージはまだありません</p>
          )}
        </div>
        )}
      </div>
    </AppLayout>
  );
}
