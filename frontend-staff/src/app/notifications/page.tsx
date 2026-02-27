"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import StaffLayout from "@/components/StaffLayout";

type Notification = {
  id: number;
  account_id: number;
  type: string;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await apiFetch<Notification[]>("/api/v1/notifications?limit=100");
      setNotifications(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const markAsRead = async (id: number) => {
    try {
      const updated = await apiFetch<Notification>(`/api/v1/notifications/${id}/read`, {
        method: "PATCH",
      });
      setNotifications((prev) => prev.map((n) => (n.id === updated.id ? updated : n)));
    } catch {
      // ignore
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiFetch("/api/v1/notifications/read-all", { method: "PATCH" });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // ignore
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const formatDate = (s: string) => new Date(s).toLocaleString("ja-JP");

  const typeLabel = (type: string) => {
    switch (type) {
      case "system": return "システム";
      case "like": return "いいね";
      case "message": return "メッセージ";
      case "credit": return "クレジット";
      default: return type;
    }
  };

  const typeColor = (type: string) => {
    switch (type) {
      case "system": return "bg-blue-100 text-blue-700";
      case "like": return "bg-pink-100 text-pink-700";
      case "message": return "bg-green-100 text-green-700";
      case "credit": return "bg-yellow-100 text-yellow-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <StaffLayout>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold">お知らせ</h2>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-sm text-blue-600 hover:underline"
            >
              すべて既読にする
            </button>
          )}
        </div>

        {loading ? (
          <p className="text-gray-400 text-sm">読み込み中...</p>
        ) : notifications.length === 0 ? (
          <div className="bg-white rounded shadow p-8 text-center text-gray-400">
            お知らせはありません
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`bg-white rounded shadow px-4 py-3 flex items-start gap-3 ${
                  !n.is_read ? "border-l-4 border-purple-500" : ""
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${typeColor(n.type)}`}>
                      {typeLabel(n.type)}
                    </span>
                    <span className={`text-sm font-bold ${!n.is_read ? "text-gray-900" : "text-gray-500"}`}>
                      {n.title}
                    </span>
                  </div>
                  {n.body && (
                    <p className={`text-sm ${!n.is_read ? "text-gray-700" : "text-gray-400"}`}>
                      {n.body}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">{formatDate(n.created_at)}</p>
                </div>
                {!n.is_read && (
                  <button
                    onClick={() => markAsRead(n.id)}
                    className="text-xs text-blue-600 hover:underline whitespace-nowrap mt-1"
                  >
                    既読
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </StaffLayout>
  );
}
