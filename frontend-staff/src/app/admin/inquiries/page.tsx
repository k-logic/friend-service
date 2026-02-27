"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Inquiry = { id: number; account_id: number; account_display_name: string | null; subject: string; body: string; status: string; admin_reply: string | null; created_at: string };

export default function AdminInquiriesPage() {
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [detailTarget, setDetailTarget] = useState<Inquiry | null>(null);
  const [replyTarget, setReplyTarget] = useState<Inquiry | null>(null);
  const [replyText, setReplyText] = useState("");

  useEffect(() => {
    apiFetch<Inquiry[]>("/api/v1/inquiries").then(setInquiries).catch(() => {});
  }, []);

  const openReply = (inq: Inquiry) => {
    setReplyTarget(inq);
    setReplyText(inq.admin_reply || "");
  };

  const handleReply = async () => {
    if (!replyTarget) return;
    await apiFetch(`/api/v1/inquiries/${replyTarget.id}/reply`, {
      method: "PATCH",
      body: JSON.stringify({ admin_reply: replyText }),
    });
    setReplyTarget(null);
    setReplyText("");
    apiFetch<Inquiry[]>("/api/v1/inquiries").then(setInquiries);
  };


  return (
    <StaffLayout>
      <div className="p-6">
        <h2 className="text-lg font-bold mb-4">サポート問い合わせ</h2>

        <table className="w-full bg-white rounded shadow text-xs">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">日時</th>
              <th className="p-2 text-left">会員ID</th>
              <th className="p-2 text-left">件名</th>
              <th className="p-2">ステータス</th>
              <th className="p-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {inquiries.map((inq) => (
              <tr key={inq.id} className="border-t">
                <td className="p-2">{new Date(inq.created_at).toLocaleString("ja-JP")}</td>
                <td className="p-2">{inq.account_display_name || "-"} (#{inq.account_id})</td>
                <td
                  className="p-2 text-blue-600 cursor-pointer hover:underline"
                  onClick={() => setDetailTarget(inq)}
                >
                  {inq.subject}
                </td>
                <td className="p-2 text-center">
                  <span className={inq.status === "open" ? "text-red-600 font-bold" : "text-green-600"}>{inq.status}</span>
                </td>
                <td className="p-2 text-center">
                  <button
                    onClick={() => openReply(inq)}
                    className="text-blue-600 hover:underline"
                  >
                    返信
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {detailTarget && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center" onClick={() => setDetailTarget(null)}>
            <div className="bg-white rounded shadow-lg p-6 w-[480px] max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold">問い合わせ内容</h3>
                <span className={`text-xs font-bold ${detailTarget.status === "open" ? "text-red-600" : "text-green-600"}`}>{detailTarget.status}</span>
              </div>
              <p className="text-xs text-gray-400 mb-2">
                {detailTarget.account_display_name || "-"} (ID: {detailTarget.account_id}) / {new Date(detailTarget.created_at).toLocaleString("ja-JP")}
              </p>
              <div className="bg-gray-50 rounded p-3 mb-3">
                <p className="text-xs text-gray-500 font-bold mb-1">件名: {detailTarget.subject}</p>
                <p className="text-sm whitespace-pre-wrap">{detailTarget.body}</p>
              </div>
              {detailTarget.admin_reply && (
                <div className="bg-purple-50 rounded p-3 mb-3">
                  <p className="text-xs text-purple-500 font-bold mb-1">返信内容:</p>
                  <p className="text-sm whitespace-pre-wrap text-purple-700">{detailTarget.admin_reply}</p>
                </div>
              )}
              <div className="flex gap-2 justify-end">
                <button onClick={() => { setDetailTarget(null); openReply(detailTarget); }} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">返信</button>
                <button onClick={() => setDetailTarget(null)} className="px-4 py-1.5 bg-gray-300 rounded text-sm">閉じる</button>
              </div>
            </div>
          </div>
        )}

        {replyTarget && (
          <div className="fixed inset-0 bg-black/30 flex items-center justify-center">
            <div className="bg-white rounded shadow-lg p-6 w-[480px] max-h-[80vh] overflow-y-auto">
              <h3 className="font-bold mb-3">問い合わせ返信</h3>
              <div className="mb-3 bg-gray-50 rounded p-3">
                <p className="text-xs text-gray-500 font-bold mb-1">件名: {replyTarget.subject}</p>
                <p className="text-sm whitespace-pre-wrap">{replyTarget.body}</p>
              </div>
              <label className="text-xs text-gray-500 font-bold">返信内容</label>
              <textarea value={replyText} onChange={(e) => setReplyText(e.target.value)} rows={4} className="w-full border rounded p-2 text-sm mt-1" />
              <div className="flex gap-2 mt-3">
                <button onClick={handleReply} className="px-4 py-1.5 bg-purple-600 text-white rounded text-sm">送信</button>
                <button onClick={() => setReplyTarget(null)} className="px-4 py-1.5 bg-gray-300 rounded text-sm">キャンセル</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </StaffLayout>
  );
}
