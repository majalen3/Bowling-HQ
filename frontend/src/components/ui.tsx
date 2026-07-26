export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-16">
      <div className="h-10 w-10 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
    </div>
  )
}

interface ErrorCardProps {
  message?: string
}

export function ErrorCard({ message = 'Something went wrong.' }: ErrorCardProps) {
  return (
    <div className="rounded-lg bg-red-900/30 border border-red-700 p-4 text-red-300">
      {message}
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
}

export function StatCard({ label, value, sub }: StatCardProps) {
  return (
    <div className="rounded-xl bg-gray-800 border border-gray-700 p-5">
      <p className="text-xs text-gray-400 uppercase tracking-wider">{label}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
      {sub && <p className="text-sm text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}
