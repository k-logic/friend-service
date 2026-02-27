"use client";


import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { clearToken } from "@/lib/api";

const NAV_SECTIONS = [
  {
    title: "オペレーター",
    adminOnly: false,
    items: [
      { href: "/operator", label: "チャット" },
      { href: "/personas/search", label: "ペルソナ検索" },
      { href: "/templates", label: "テンプレート" },
      { href: "/notifications", label: "お知らせ" },
    ],
  },
  {
    title: "ペルソナ管理",
    adminOnly: true,
    items: [
      { href: "/personas", label: "ペルソナ一覧・作成" },
    ],
  },
  {
    title: "ユーザ管理",
    adminOnly: false,
    items: [
      { href: "/admin/users", label: "ユーザ検索" },
    ],
  },
  {
    title: "ユーザ管理（管理者）",
    adminOnly: true,
    items: [
      { href: "/admin/age-verification", label: "年齢認証管理" },
    ],
  },
  {
    title: "有料情報関連",
    adminOnly: true,
    items: [{ href: "/admin/paid-contents", label: "有料情報管理" }],
  },
  {
    title: "メール関連",
    adminOnly: true,
    items: [
      { href: "/admin/mail", label: "メール配信" },
      { href: "/admin/invitations", label: "招待管理" },
    ],
  },
  {
    title: "サポート",
    adminOnly: true,
    items: [
      { href: "/admin/inquiries", label: "問い合わせ管理" },
    ],
  },
  {
    title: "LINE",
    adminOnly: true,
    items: [{ href: "/admin/line-bot", label: "LINE Bot管理" }],
  },
];

export default function AdminSidebar() {
  const { account } = useAuth();
  const pathname = usePathname();

  const handleLogout = () => {
    clearToken();
    window.location.href = "/login";
  };

  return (
    <aside className="w-56 min-h-screen bg-white border-r border-gray-200 flex flex-col text-sm">
      <div className="p-4 border-b">
        <h1 className="font-bold text-lg">管理画面</h1>
        <p className="text-xs text-gray-500">[{account?.role}] {account?.display_name}</p>
      </div>

      <nav className="flex-1 overflow-y-auto">
        {NAV_SECTIONS.filter((section) => !section.adminOnly || account?.role === "admin").map((section) => (
          <div key={section.title}>
            <div className="px-4 py-2 bg-purple-100 text-purple-800 font-bold text-xs">
              {section.title}
            </div>
            {section.items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-4 py-2 hover:bg-gray-100 ${
                  pathname === item.href ? "text-purple-700 font-bold bg-purple-50" : "text-blue-600"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        ))}
      </nav>

      <div className="p-3 border-t">
        <button onClick={handleLogout} className="text-xs text-blue-600 hover:underline">
          ログアウト
        </button>
      </div>
    </aside>
  );
}
