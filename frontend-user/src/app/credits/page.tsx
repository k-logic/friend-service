"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import AppLayout from "@/components/AppLayout";

const PLANS = [
  { amount: 10, price: "¥1,000" },
  { amount: 50, price: "¥4,500" },
  { amount: 100, price: "¥8,000" },
  { amount: 300, price: "¥20,000" },
];

export default function CreditsPage() {
  const { account, setAccount } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleCharge = async (amount: number) => {
    setLoading(true);
    setMessage("");
    try {
      const data = await apiFetch<{ credit_balance: number }>("/api/v1/credits/charge", {
        method: "POST",
        body: JSON.stringify({ amount }),
      });
      if (account) {
        setAccount({ ...account, credit_balance: data.credit_balance });
      }
      setMessage(`${amount}ポイントをチャージしました`);
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-4 md:p-8 max-w-2xl mx-auto">
        <h2 className="text-xl font-bold mb-6">ポイント購入</h2>

        <div className="bg-white rounded-xl shadow p-6 mb-6 text-center">
          <p className="text-sm text-gray-500">現在の残高</p>
          <p className="text-4xl font-bold text-teal-600">{account?.credit_balance || 0}</p>
          <p className="text-sm text-gray-500">ポイント</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {PLANS.map((plan) => (
            <button
              key={plan.amount}
              onClick={() => handleCharge(plan.amount)}
              disabled={loading}
              className="bg-white rounded-xl shadow p-6 hover:shadow-md transition-shadow text-center disabled:opacity-50"
            >
              <p className="text-2xl font-bold text-teal-600">{plan.amount}pt</p>
              <p className="text-gray-500 text-sm mt-1">{plan.price}</p>
            </button>
          ))}
        </div>

        {message && (
          <p className="mt-4 text-center text-sm text-teal-600">{message}</p>
        )}
      </div>
    </AppLayout>
  );
}
