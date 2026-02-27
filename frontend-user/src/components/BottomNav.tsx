"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/search", label: "さがす", icon: "🔍" },
  { href: "/messages", label: "メッセージ", icon: "💬" },
  { href: "/likes", label: "いいね", icon: "👍" },
  { href: "/mypage", label: "マイページ", icon: "😊" },
  { href: "/notifications", label: "お知らせ", icon: "🔔" },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
      <div className="flex justify-around items-center h-14">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-0.5 text-[10px] ${
                isActive ? "text-teal-600 font-bold" : "text-gray-400"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
