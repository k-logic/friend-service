"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import AppLayout from "@/components/AppLayout";
import LoadingSpinner from "@/components/LoadingSpinner";

type Notification = {
  id: number;
  type: string;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Notification[]>("/api/v1/notifications")
      .then(setNotifications)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const markRead = async (id: number) => {
    await apiFetch(`/api/v1/notifications/${id}/read`, { method: "PATCH" });
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  };

  const markAllRead = async () => {
    await apiFetch("/api/v1/notifications/read-all", { method: "PATCH" });
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  return (
    <AppLayout>
      <div className="p-4 md:p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">お知らせ</h2>
          <button onClick={markAllRead} className="text-sm text-teal-500 hover:underline">
            すべて既読にする
          </button>
        </div>
        {loading ? <LoadingSpinner /> : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className={`p-4 bg-white rounded-lg shadow-sm cursor-pointer ${
                !n.is_read ? "border-l-4 border-teal-500" : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <p className={`font-medium text-sm ${!n.is_read ? "text-teal-700" : "text-gray-600"}`}>
                  {n.title}
                </p>
                <span className="text-xs text-gray-400">
                  {new Date(n.created_at).toLocaleDateString("ja-JP")}
                </span>
              </div>
              {n.body && <p className="text-sm text-gray-500 mt-1">{n.body}</p>}
            </div>
          ))}
          {notifications.length === 0 && (
            <p className="text-center text-gray-400 py-12">お知らせはありません</p>
          )}
        </div>
        )}
      </div>
    </AppLayout>
  );
}
