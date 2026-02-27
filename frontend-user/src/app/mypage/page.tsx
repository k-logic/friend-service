"use client";

import { useAuth } from "@/lib/auth";
import AppLayout from "@/components/AppLayout";

export default function MyPage() {
  const { account } = useAuth();

  return (
    <AppLayout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <h2 className="text-xl font-bold mb-6">マイページ</h2>
        <div className="bg-white rounded-xl shadow p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-gray-200 overflow-hidden">
              {account?.avatar_url ? (
                <img src={account.avatar_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-2xl text-gray-400">
                  {account?.display_name?.[0]}
                </div>
              )}
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
