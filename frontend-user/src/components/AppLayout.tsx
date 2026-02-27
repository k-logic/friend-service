"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { account, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !account) {
      router.push("/login");
    }
  }, [loading, account, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <div className="animate-spin h-10 w-10 border-4 border-teal-500 border-t-transparent rounded-full" />
        <p className="mt-4 text-sm text-gray-400">読み込み中...</p>
      </div>
    );
  }

  if (!account) return null;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 bg-gray-50 pb-16 md:pb-0">{children}</main>
      <BottomNav />
    </div>
  );
}
