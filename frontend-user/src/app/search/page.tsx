"use client";

import { useEffect, useState } from "react";
import { apiFetch, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import Link from "next/link";

type Persona = {
  id: number;
  name: string;
  gender: string | null;
  age: number | null;
  avatar_url: string | null;
  bio: string | null;
};

export default function SearchPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);

  useEffect(() => {
    apiFetch<Persona[]>("/api/v1/personas").then(setPersonas).catch(() => {});
  }, []);

  return (
    <AppLayout>
      <div className="p-4 md:p-8">
        <h2 className="text-xl font-bold mb-6">さがす</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
          {personas.map((p) => (
            <Link key={p.id} href={`/persona/${p.id}`} className="text-center group">
              <div className="w-20 h-20 sm:w-24 sm:h-24 mx-auto rounded-full bg-gray-200 overflow-hidden border-2 border-pink-200 group-hover:border-pink-400 transition-colors">
                {p.avatar_url ? (
                  <img src={toFullUrl(p.avatar_url)!} alt={p.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-3xl text-gray-400">
                    {p.name[0]}
                  </div>
                )}
              </div>
              <p className="mt-2 text-sm font-medium">{p.name}</p>
              <p className="text-xs text-gray-500">
                {p.gender === "male" ? "男性" : p.gender === "female" ? "女性" : ""}
                {p.gender && p.age ? " / " : ""}
                {p.age ? `${p.age}歳` : ""}
              </p>
            </Link>
          ))}
          {personas.length === 0 && (
            <p className="col-span-full text-center text-gray-400 py-12">
              まだペルソナが登録されていません
            </p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
