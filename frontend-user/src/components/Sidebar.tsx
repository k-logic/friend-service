"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { clearToken } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/search", label: "さがす", icon: "🔍" },
  { href: "/messages", label: "メッセージ", icon: "💬" },
  { href: "/likes", label: "いいね", icon: "👍" },
  { href: "/footprints", label: "足跡", icon: "👣" },
  { href: "/mypage", label: "マイページ", icon: "😊" },
  { href: "/credits", label: "ポイント購入", icon: "💎" },
  { href: "/notifications", label: "お知らせ", icon: "🔔" },
  { href: "/contact", label: "お問い合わせ", icon: "✉️" },
];

export default function Sidebar() {
  const { account, setAccount } = useAuth();
  const pathname = usePathname();

  const handleLogout = () => {
    clearToken();
    setAccount(null);
    window.location.href = "/login";
  };

  return (
    <aside className="hidden md:flex w-64 min-h-screen bg-gradient-to-b from-teal-50 to-white border-r border-gray-200 flex-col">
      {/* ロゴ */}
      <div className="p-6 text-center">
        <h1 className="text-3xl font-bold text-teal-500">Friend</h1>
      </div>

      {/* プロフィール */}
      {account && (
        <div className="px-4 pb-4 text-center border-b border-gray-200">
          <div className="w-20 h-20 mx-auto rounded-full bg-gray-200 overflow-hidden mb-2">
            {account.avatar_url ? (
              <img src={account.avatar_url} alt="" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-2xl text-gray-400">
                {account.display_name[0]}
              </div>
            )}
          </div>
          <p className="font-medium text-sm">{account.display_name} さん</p>
          <p className="text-xs text-gray-500">会員ID: {account.id}</p>

          {/* ポイント残高 */}
          <div className="mt-3 mb-2">
            <p className="text-xs text-gray-500">ポイント残高</p>
            <p className="text-2xl font-bold text-teal-600">{account.credit_balance}</p>
          </div>
          <Link
            href="/credits"
            className="inline-block bg-teal-500 text-white text-xs px-4 py-1.5 rounded-full hover:bg-teal-600"
          >
            ポイント購入
          </Link>
        </div>
      )}

      {/* ナビゲーション */}
      <nav className="flex-1 py-4">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-6 py-2.5 text-sm transition-colors ${
              pathname === item.href
                ? "bg-teal-100 text-teal-700 font-medium"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* ログアウト */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="w-full text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          ログアウト
        </button>
      </div>
    </aside>
  );
}
