"use client";

export default function LoadingSpinner({ message = "読み込み中..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="animate-spin h-8 w-8 border-4 border-teal-500 border-t-transparent rounded-full" />
      <p className="mt-3 text-sm text-gray-400">{message}</p>
    </div>
  );
}
