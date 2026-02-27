"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

type Persona = {
  id: number;
  name: string;
  gender: string | null;
  age: number | null;
  avatar_url: string | null;
  bio: string | null;
};

export default function PersonaDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [liked, setLiked] = useState(false);

  useEffect(() => {
    apiFetch<Persona>(`/api/v1/personas/${params.id}`).then(setPersona).catch(() => {});
    // いいね状態を取得
    apiFetch<{ id: number; persona_id: number }[]>("/api/v1/likes").then((likes) => {
      setLiked(likes.some((l) => l.persona_id === Number(params.id)));
    }).catch(() => {});
    // 足跡記録
    apiFetch("/api/v1/footprints", {
      method: "POST",
      body: JSON.stringify({ persona_id: Number(params.id) }),
    }).catch(() => {});
  }, [params.id]);

  const handleStartChat = async () => {
    try {
      const session = await apiFetch<{ id: number }>("/api/v1/sessions", {
        method: "POST",
        body: JSON.stringify({ persona_id: Number(params.id) }),
      });
      router.push(`/chat/${session.id}`);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleLike = async () => {
    try {
      if (liked) {
        await apiFetch(`/api/v1/likes/${params.id}`, { method: "DELETE" });
        setLiked(false);
      } else {
        await apiFetch("/api/v1/likes", {
          method: "POST",
          body: JSON.stringify({ persona_id: Number(params.id) }),
        });
        setLiked(true);
      }
    } catch {
      // 既にいいね済みなどのエラー
    }
  };

  if (!persona) return <AppLayout><div className="p-4">読み込み中...</div></AppLayout>;

  return (
    <AppLayout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow p-6 md:p-8 text-center">
          <div className="w-24 h-24 md:w-32 md:h-32 mx-auto rounded-full bg-gray-200 overflow-hidden border-4 border-pink-200 mb-4">
            {persona.avatar_url ? (
              <img src={toFullUrl(persona.avatar_url)!} alt={persona.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-4xl text-gray-400">
                {persona.name[0]}
              </div>
            )}
          </div>
          <h2 className="text-xl font-bold">{persona.name}</h2>
          <p className="text-gray-500">
            {persona.gender === "male" ? "男性" : persona.gender === "female" ? "女性" : ""}
            {persona.gender && persona.age ? " / " : ""}
            {persona.age ? `${persona.age}歳` : ""}
          </p>
          {persona.bio && <p className="mt-4 text-gray-600 text-sm">{persona.bio}</p>}

          <div className="mt-6 flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
            <button
              onClick={handleLike}
              className={`px-6 py-2 rounded-full font-medium transition-colors ${
                liked
                  ? "bg-pink-500 text-white"
                  : "bg-pink-100 text-pink-500 hover:bg-pink-200"
              }`}
            >
              {liked ? "いいね済み" : "いいね"}
            </button>
            <button
              onClick={handleStartChat}
              className="px-6 py-2 bg-teal-500 text-white rounded-full hover:bg-teal-600 font-medium"
            >
              チャットを始める
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
