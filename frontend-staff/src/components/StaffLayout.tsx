"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import AdminSidebar from "./AdminSidebar";

export default function StaffLayout({ children }: { children: React.ReactNode }) {
  const { account, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !account) {
      router.push("/login");
    }
  }, [loading, account, router]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><p>読み込み中...</p></div>;
  }

  if (!account) return null;

  return (
    <div className="flex min-h-screen">
      <AdminSidebar />
      <main className="flex-1 bg-gray-50">{children}</main>
    </div>
  );
}
