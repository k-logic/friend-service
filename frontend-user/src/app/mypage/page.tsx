"use client";

import { useRef, useState } from "react";
import { useAuth } from "@/lib/auth";
import { apiUpload, toFullUrl } from "@/lib/api";
import AppLayout from "@/components/AppLayout";

export default function MyPage() {
  const { account, setAccount } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const updated = await apiUpload<any>("/api/v1/auth/avatar", formData);
      setAccount(updated);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <AppLayout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <h2 className="text-xl font-bold mb-6">マイページ</h2>
        <div className="bg-white rounded-xl shadow p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div
              className="relative w-20 h-20 rounded-full bg-gray-200 overflow-hidden cursor-pointer group"
              onClick={() => fileRef.current?.click()}
            >
              {account?.avatar_url ? (
                <img src={toFullUrl(account.avatar_url)!} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-2xl text-gray-400">
                  {account?.display_name?.[0]}
                </div>
              )}
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-xs font-medium">
                  {uploading ? "..." : "変更"}
                </span>
              </div>
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleAvatarChange}
              />
            </div>
            <div>
              <p className="text-lg font-bold">{account?.display_name}</p>
              <p className="text-sm text-gray-500">ID: {account?.id}</p>
              <p className="text-sm text-gray-500">{account?.email}</p>
            </div>
          </div>

          <div className="border-t pt-4">
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">ポイント残高</dt>
                <dd className="font-bold text-teal-600">{account?.credit_balance} pt</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">ステータス</dt>
                <dd>{account?.status === "active" ? "有効" : "停止中"}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
