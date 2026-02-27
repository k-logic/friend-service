"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";
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

export default function PersonasPage() {
  const { account } = useAuth();
  const router = useRouter();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() => {
    if (account && account.role !== "admin") {
      router.replace("/personas/search");
      return;
    }
  }, [account, router]);

  useEffect(() => {
    if (account?.role === "admin") {
      apiFetch<Persona[]>("/api/v1/personas").then(setPersonas).catch(() => {});
    }
  }, [account]);

  const handleCreate = async () => {
    if (!name) return;
    const p = await apiFetch<Persona>("/api/v1/personas", {
      method: "POST",
      body: JSON.stringify({ name, gender: gender || null, age: age ? Number(age) : null, bio: bio || null }),
    });
    setPersonas((prev) => [p, ...prev]);
    setName("");
    setGender("");
    setAge("");
    setBio("");
  };

  if (!account || account.role !== "admin") {
    return null;
  }

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">ペルソナ管理</h2>

        <div className="bg-white rounded shadow p-4 mb-6 flex gap-3 items-end">
          <div>
            <label className="text-xs text-gray-500">名前</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="block border rounded px-2 py-1 text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">性別</label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="block border rounded px-2 py-1 text-sm"
            >
              <option value="">未設定</option>
              <option value="male">男性</option>
              <option value="female">女性</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500">年齢</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="block border rounded px-2 py-1 text-sm w-20"
            />
          </div>
          <div className="flex-1">
            <label className="text-xs text-gray-500">自己紹介</label>
            <input
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="block w-full border rounded px-2 py-1 text-sm"
            />
          </div>
          <button
            onClick={handleCreate}
            className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
          >
            追加
          </button>
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
            {personas.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-2">{p.id}</td>
                <td className="p-2">{p.name}</td>
                <td className="p-2 text-center">{p.gender === "male" ? "男性" : p.gender === "female" ? "女性" : "-"}</td>
                <td className="p-2 text-center">{p.age || "-"}</td>
                <td className="p-2 text-gray-600">{p.bio || "-"}</td>
                <td className="p-2 text-center">{p.is_active ? "有効" : "無効"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
