"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, apiUpload, API_BASE } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import StaffLayout from "@/components/StaffLayout";

type Persona = {
  id: number;
  name: string;
  gender: string | null;
  age: number | null;
  avatar_url: string | null;
  bio: string | null;
  registered_at: string | null;
  is_active: boolean;
};

function resolveImageUrl(url: string | null): string | null {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${API_BASE}${url}`;
}

type ModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; persona: Persona };

export default function PersonasPage() {
  const { account } = useAuth();
  const router = useRouter();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [modal, setModal] = useState<ModalState>({ mode: "closed" });

  // モーダルフォーム
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");
  const [bio, setBio] = useState("");
  const [registeredAt, setRegisteredAt] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const resetForm = () => {
    setName("");
    setGender("");
    setAge("");
    setBio("");
    setRegisteredAt("");
    setIsActive(true);
    setAvatarFile(null);
    setAvatarPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const openCreate = () => {
    resetForm();
    setModal({ mode: "create" });
  };

  const openEdit = (persona: Persona) => {
    setName(persona.name);
    setGender(persona.gender || "");
    setAge(persona.age?.toString() || "");
    setBio(persona.bio || "");
    setRegisteredAt(persona.registered_at || "");
    setIsActive(persona.is_active);
    setAvatarFile(null);
    setAvatarPreview(resolveImageUrl(persona.avatar_url));
    if (fileInputRef.current) fileInputRef.current.value = "";
    setModal({ mode: "edit", persona });
  };

  const closeModal = () => {
    setModal({ mode: "closed" });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setAvatarFile(f);
    if (f) {
      setAvatarPreview(URL.createObjectURL(f));
    }
  };

  const handleSave = async () => {
    if (!name) return;
    setSaving(true);
    try {
      if (modal.mode === "create") {
        const p = await apiFetch<Persona>("/api/v1/personas", {
          method: "POST",
          body: JSON.stringify({
            name,
            gender: gender || null,
            age: age ? Number(age) : null,
            bio: bio || null,
            registered_at: registeredAt || null,
          }),
        });
        let created = p;
        if (avatarFile) {
          created = await apiUpload<Persona>(`/api/v1/personas/${p.id}/avatar`, avatarFile);
        }
        setPersonas((prev) => [created, ...prev]);
      } else if (modal.mode === "edit") {
        const updated = await apiFetch<Persona>(`/api/v1/personas/${modal.persona.id}`, {
          method: "PATCH",
          body: JSON.stringify({
            name,
            gender: gender || null,
            age: age ? Number(age) : null,
            bio: bio || null,
            registered_at: registeredAt || null,
            is_active: isActive,
          }),
        });
        let result = updated;
        if (avatarFile) {
          result = await apiUpload<Persona>(`/api/v1/personas/${modal.persona.id}/avatar`, avatarFile);
        }
        setPersonas((prev) => prev.map((p) => (p.id === result.id ? result : p)));
      }
      closeModal();
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  if (!account || account.role !== "admin") {
    return null;
  }

  return (
    <StaffLayout>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">ペルソナ管理</h2>
          <button
            onClick={openCreate}
            className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
          >
            新規作成
          </button>
        </div>

        <table className="w-full bg-white rounded shadow text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">ID</th>
              <th className="p-2">画像</th>
              <th className="p-2 text-left">名前</th>
              <th className="p-2">性別</th>
              <th className="p-2">年齢</th>
              <th className="p-2 text-left">自己紹介</th>
              <th className="p-2">登録日</th>
              <th className="p-2">状態</th>
            </tr>
          </thead>
          <tbody>
            {personas.map((p) => (
              <tr
                key={p.id}
                className="border-t hover:bg-gray-50 cursor-pointer"
                onClick={() => openEdit(p)}
              >
                <td className="p-2">{p.id}</td>
                <td className="p-2 text-center">
                  {p.avatar_url ? (
                    <img
                      src={resolveImageUrl(p.avatar_url)!}
                      alt=""
                      className="w-10 h-10 rounded-full object-cover mx-auto"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 text-xs mx-auto">
                      無
                    </div>
                  )}
                </td>
                <td className="p-2">{p.name}</td>
                <td className="p-2 text-center">{p.gender === "male" ? "男性" : p.gender === "female" ? "女性" : "-"}</td>
                <td className="p-2 text-center">{p.age || "-"}</td>
                <td className="p-2 text-gray-600 max-w-xs truncate">{p.bio || "-"}</td>
                <td className="p-2 text-center">{p.registered_at || "-"}</td>
                <td className="p-2 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs ${p.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {p.is_active ? "有効" : "無効"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* モーダル */}
      {modal.mode !== "closed" && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={closeModal}>
          <div
            className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-bold mb-4">
              {modal.mode === "create" ? "ペルソナ新規作成" : "ペルソナ編集"}
            </h3>

            <div className="space-y-3">
              {/* アバター */}
              <div className="flex items-center gap-4">
                <label className="cursor-pointer">
                  {avatarPreview ? (
                    <img src={avatarPreview} alt="" className="w-16 h-16 rounded-full object-cover" />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 text-sm">
                      画像
                    </div>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                </label>
                <span className="text-xs text-gray-400">クリックして画像を選択</span>
              </div>

              {/* 名前 */}
              <div>
                <label className="text-xs text-gray-500">名前 *</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="block w-full border rounded px-3 py-1.5 text-sm"
                />
              </div>

              {/* 性別・年齢 */}
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="text-xs text-gray-500">性別</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="block w-full border rounded px-3 py-1.5 text-sm"
                  >
                    <option value="">未設定</option>
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                  </select>
                </div>
                <div className="w-24">
                  <label className="text-xs text-gray-500">年齢</label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="block w-full border rounded px-3 py-1.5 text-sm"
                  />
                </div>
              </div>

              {/* 登録日 */}
              <div>
                <label className="text-xs text-gray-500">登録日</label>
                <input
                  type="date"
                  value={registeredAt}
                  onChange={(e) => setRegisteredAt(e.target.value)}
                  className="block w-full border rounded px-3 py-1.5 text-sm"
                />
              </div>

              {/* 自己紹介 */}
              <div>
                <label className="text-xs text-gray-500">自己紹介</label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                  className="block w-full border rounded px-3 py-1.5 text-sm resize-none"
                />
              </div>

              {/* 状態（編集時のみ） */}
              {modal.mode === "edit" && (
                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-500">状態</label>
                  <select
                    value={isActive ? "true" : "false"}
                    onChange={(e) => setIsActive(e.target.value === "true")}
                    className="border rounded px-3 py-1.5 text-sm"
                  >
                    <option value="true">有効</option>
                    <option value="false">無効</option>
                  </select>
                </div>
              )}
            </div>

            {/* ボタン */}
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={closeModal}
                className="px-4 py-1.5 border rounded text-sm text-gray-600 hover:bg-gray-50"
              >
                キャンセル
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !name}
                className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm hover:bg-purple-700 disabled:opacity-50"
              >
                {saving ? "保存中..." : modal.mode === "create" ? "作成" : "保存"}
              </button>
            </div>
          </div>
        </div>
      )}
    </StaffLayout>
  );
}
