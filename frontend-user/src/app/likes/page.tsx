"use client";

import { useEffect, useState } from "react";
import { apiFetch, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import Link from "next/link";

type Like = { id: number; persona_id: number; created_at: string };
type Persona = { id: number; name: string; age: number | null; avatar_url: string | null };

export default function LikesPage() {
  const [likes, setLikes] = useState<Like[]>([]);
  const [personas, setPersonas] = useState<Record<number, Persona>>({});

  useEffect(() => {
    (async () => {
      const data = await apiFetch<Like[]>("/api/v1/likes");
      setLikes(data);
      const map: Record<number, Persona> = {};
      await Promise.all(
        data.map(async (l) => {
          try {
            map[l.persona_id] = await apiFetch<Persona>(`/api/v1/personas/${l.persona_id}`);
          } catch {}
        })
      );
      setPersonas(map);
    })();
  }, []);

  return (
    <AppLayout>
      <div className="p-4 md:p-8">
        <h2 className="text-xl font-bold mb-6">いいね</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 md:gap-6">
          {likes.map((l) => {
            const p = personas[l.persona_id];
            return (
              <Link key={l.id} href={`/persona/${l.persona_id}`} className="text-center">
                <div className="w-20 h-20 mx-auto rounded-full bg-gray-200 overflow-hidden border-2 border-pink-300">
                  {p?.avatar_url ? (
                    <img src={toFullUrl(p.avatar_url)!} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-2xl text-gray-400">
                      {p?.name?.[0] || "?"}
                    </div>
                  )}
                </div>
                <p className="mt-2 text-sm font-medium">{p?.name || "..."}</p>
              </Link>
            );
          })}
          {likes.length === 0 && (
            <p className="col-span-full text-center text-gray-400 py-12">まだいいねしていません</p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
