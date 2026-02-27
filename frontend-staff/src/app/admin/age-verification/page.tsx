"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Verification = { id: number; account_id: number; account_display_name: string | null; status: string; submitted_at: string; reviewed_at: string | null };

export default function AgeVerificationPage() {
  const [items, setItems] = useState<Verification[]>([]);

  useEffect(() => {
    apiFetch<Verification[]>("/api/v1/age-verification").then(setItems).catch(() => {});
  }, []);

  const review = async (id: number, status: string) => {
    await apiFetch(`/api/v1/age-verification/${id}/review`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    apiFetch<Verification[]>("/api/v1/age-verification").then(setItems);
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">年齢認証管理</h2>
        <table className="w-full bg-white rounded shadow text-xs">
          <thead className="bg-gray-50"><tr><th className="p-2">ID</th><th className="p-2">会員</th><th className="p-2">ステータス</th><th className="p-2">申請日</th><th className="p-2">操作</th></tr></thead>
          <tbody>
            {items.map((v) => (
              <tr key={v.id} className="border-t">
                <td className="p-2 text-center">{v.id}</td>
                <td className="p-2 text-center">{v.account_display_name || "-"} (#{v.account_id})</td>
                <td className="p-2 text-center"><span className={v.status === "pending" ? "text-orange-600 font-bold" : v.status === "approved" ? "text-green-600" : "text-red-600"}>{v.status}</span></td>
                <td className="p-2 text-center">{new Date(v.submitted_at).toLocaleString("ja-JP")}</td>
                <td className="p-2 text-center">
                  {v.status === "pending" && (
                    <span className="space-x-2">
                      <button onClick={() => review(v.id, "approved")} className="text-green-600 hover:underline">承認</button>
                      <button onClick={() => review(v.id, "rejected")} className="text-red-600 hover:underline">拒否</button>
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </StaffLayout>
  );
}
