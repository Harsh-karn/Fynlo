"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import api from "@/lib/api"
import { Users, TrendingUp, Activity, ShieldAlert, Cpu } from "lucide-react"

interface OpsMetrics {
  users: {
    total: number
    pro: number
    new_24h: number
    conversion_rate_pct: number
  }
  transactions: {
    total: number
    processed_24h: number
    needs_review_backlog: number
  }
  revenue: {
    mrr_inr: number
  }
  system: {
    status: string
    ml_model_active: boolean
    ai_api_cost_saved_inr: number
  }
}

export default function AdminDashboard() {
  const { status } = useSession()
  const router = useRouter()
  const [metrics, setMetrics] = useState<OpsMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const response = await api.get("/ops/metrics")
        setMetrics(response.data)
      } catch (err: unknown) {
        if (err && typeof err === 'object' && 'response' in err) {
          const axiosErr = err as { response?: { data?: { error?: { message?: string } } } }
          setError(axiosErr.response?.data?.error?.message || "Failed to load metrics")
        } else {
          setError(err instanceof Error ? err.message : "Failed to load metrics")
        }
      } finally {
        setLoading(false)
      }
    }

    if (status === "authenticated") {
      fetchMetrics()
    }
  }, [status])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full pt-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-950/40 border border-red-700/40 text-red-400 p-4 rounded-xl">
          {error}
        </div>
      </div>
    )
  }

  if (!metrics) return null

  return (
    <div className="max-w-6xl mx-auto space-y-8 py-4">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Activity className="text-indigo-400" />
          Ops Metrics Dashboard
        </h1>
        <p className="text-gray-400 text-sm mt-1">Live monitoring of users, revenue, and ML performance.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Users Card */}
        <div className="bg-white/[0.03] border border-white/[0.07] p-6 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Users className="text-blue-400 size-5" />
            <h3 className="font-semibold text-gray-200">Users</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">{metrics.users.total}</div>
          <p className="text-sm text-gray-400">+{metrics.users.new_24h} in last 24h</p>
        </div>

        {/* Conversion Card */}
        <div className="bg-white/[0.03] border border-white/[0.07] p-6 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="text-green-400 size-5" />
            <h3 className="font-semibold text-gray-200">Conversion & MRR</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">₹{metrics.revenue.mrr_inr}</div>
          <p className="text-sm text-gray-400">{metrics.users.conversion_rate_pct}% Pro Conversion</p>
        </div>

        {/* Transactions Card */}
        <div className="bg-white/[0.03] border border-white/[0.07] p-6 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="text-purple-400 size-5" />
            <h3 className="font-semibold text-gray-200">Processing Load</h3>
          </div>
          <div className="text-3xl font-bold text-white mb-2">{metrics.transactions.total}</div>
          <p className="text-sm text-gray-400">+{metrics.transactions.processed_24h} in last 24h</p>
        </div>

        {/* Needs Review Backlog */}
        <div className="bg-red-950/20 border border-red-900/30 p-6 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <ShieldAlert className="text-red-400 size-5" />
            <h3 className="font-semibold text-red-200">Review Backlog</h3>
          </div>
          <div className="text-3xl font-bold text-red-400 mb-2">{metrics.transactions.needs_review_backlog}</div>
          <p className="text-sm text-red-300/70">Uncategorized transactions</p>
        </div>
      </div>

      {/* ML Cost Savings */}
      <div className="bg-indigo-950/20 border border-indigo-500/20 p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-indigo-500/10 rounded-xl">
            <Cpu className="text-indigo-400 size-6" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Local ML Engine Savings</h3>
            <p className="text-sm text-indigo-200/70">API costs saved vs. using Gemini LLM</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-emerald-400">₹{metrics.system.ai_api_cost_saved_inr}</div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">Saved Lifetime</p>
        </div>
      </div>
    </div>
  )
}
