"use client";

import { useEffect, useState } from "react";
import { apiFetch, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import Link from "next/link";

type Footprint = { id: number; persona_id: number; created_at: string };
type Persona = { id: number; name: string; age: number | null; avatar_url: string | null };

export default function FootprintsPage() {
  const [footprints, setFootprints] = useState<Footprint[]>([]);
  const [personas, setPersonas] = useState<Record<number, Persona>>({});

  useEffect(() => {
    (async () => {
      const data = await apiFetch<Footprint[]>("/api/v1/footprints/mine");
      setFootprints(data);
      const map: Record<number, Persona> = {};
      const uniqueIds = [...new Set(data.map((f) => f.persona_id))];
      await Promise.all(
        uniqueIds.map(async (pid) => {
          try {
            map[pid] = await apiFetch<Persona>(`/api/v1/personas/${pid}`);
          } catch {}
        })
      );
      setPersonas(map);
    })();
  }, []);

  return (
    <AppLayout>
      <div className="p-4 md:p-8">
        <h2 className="text-xl font-bold mb-6">足跡</h2>
        <div className="space-y-3">
          {footprints.map((f) => {
            const p = personas[f.persona_id];
            return (
              <Link
                key={f.id}
                href={`/persona/${f.persona_id}`}
                className="flex items-center gap-4 p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 rounded-full bg-gray-200 overflow-hidden">
                  {p?.avatar_url ? (
                    <img src={toFullUrl(p.avatar_url)!} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-lg text-gray-400">
                      {p?.name?.[0] || "?"}
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{p?.name || "..."}</p>
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(f.created_at).toLocaleDateString("ja-JP")}
                </span>
              </Link>
            );
          })}
          {footprints.length === 0 && (
            <p className="text-center text-gray-400 py-12">まだ閲覧履歴はありません</p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
