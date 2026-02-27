"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Persona = {
  id: number;
  name: string;
  gender: string | null;
  age: number | null;
  avatar_url: string | null;
  bio: string | null;
  is_active: boolean;
};

export default function PersonaSearchPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    apiFetch<Persona[]>("/api/v1/personas").then(setPersonas).catch(() => {});
  }, []);

  const filtered = personas.filter(
    (p) =>
      p.name.toLowerCase().includes(query.toLowerCase()) ||
      (p.bio && p.bio.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">ペルソナ検索</h2>

        <div className="mb-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="名前・自己紹介で検索..."
            className="border rounded px-3 py-2 text-sm w-80"
          />
        </div>

        <table className="w-full bg-white rounded shadow text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">名前</th>
              <th className="p-2">性別</th>
              <th className="p-2">年齢</th>
              <th className="p-2 text-left">自己紹介</th>
              <th className="p-2">状態</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-2">{p.id}</td>
                <td className="p-2">{p.name}</td>
                <td className="p-2 text-center">{p.gender === "male" ? "男性" : p.gender === "female" ? "女性" : "-"}</td>
                <td className="p-2 text-center">{p.age || "-"}</td>
                <td className="p-2 text-gray-600">{p.bio || "-"}</td>
                <td className="p-2 text-center">
                  {p.is_active ? "有効" : "無効"}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="p-4 text-center text-gray-400">
                  該当するペルソナがありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
