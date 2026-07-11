"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SpendingChart } from "@/components/dashboard/SpendingChart"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"

interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
}

interface TrendData {
  month: string
  income: number
  expense: number
}

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<TrendData[]>([])
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      setError(null)
      try {
        const today = new Date()
        const yyyy = today.getFullYear()
        const mm = String(today.getMonth() + 1).padStart(2, '0')
        const dateStr = `${yyyy}-${mm}`

        const [trendsRes, breakdownRes] = await Promise.all([
          api.get("/analytics/trends"),
          api.get(`/analytics/category-breakdown?date=${dateStr}`)
        ])

        if (trendsRes.data) {
          setTrends(trendsRes.data)
        }
        if (breakdownRes.data) {
          setBreakdown(breakdownRes.data)
        }
      } catch (err) {
        console.error("Failed to load analytics data", err)
        setError("Failed to load analytics charts and category breakdown.")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [reloadKey])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Analytics</h2>
        <p className="text-gray-400 mt-1">Deep dive into your spending habits.</p>
      </div>

      {loading ? (
        <div className="space-y-6 animate-pulse">
          {/* Charts loading skeleton */}
          <div className="grid gap-6 grid-cols-1 md:grid-cols-4">
            {[1, 2].map((i) => (
              <div key={i} className="bg-[#1e1e2e] border border-[#2a2a4e] rounded-xl h-[350px] p-6 col-span-4 lg:col-span-2 flex flex-col justify-between">
                <div className="h-6 w-1/4 bg-white/5 rounded"></div>
                <div className="flex-1 flex items-center justify-center">
                  <div className="w-32 h-32 rounded-full border-4 border-dashed border-white/5 animate-spin"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-red-500/20 bg-red-950/10 p-8 text-center flex flex-col items-center justify-center space-y-4 max-w-xl mx-auto my-12">
          <div className="p-4 bg-red-500/10 rounded-full text-red-400">
            <AlertCircle className="w-10 h-10" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Unable to load Analytics</h3>
            <p className="text-sm text-gray-400 mt-2 leading-relaxed">
              {error}
            </p>
          </div>
          <Button
            onClick={() => setReloadKey((k) => k + 1)}
            variant="outline"
            className="bg-[#1e1e2e] border-[#2a2a4e] text-white hover:bg-[#2a2a4e]/50 gap-2 px-5"
          >
            <RefreshCw className="size-4" />
            Try Again
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-4">
          <SpendingChart data={trends} />
          
          <Card className="bg-[#1e1e2e] border-[#2a2a4e] text-white col-span-4 lg:col-span-2">
            <CardHeader>
              <CardTitle>Top Categories This Month</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {breakdown.length > 0 ? (
                  breakdown.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center pb-2 border-b border-white/[0.03]">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-200">
                          {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
                        </span>
                        <span className="text-xs text-gray-400">
                          {item.percentage}% of total expenses
                        </span>
                      </div>
                      <span className="font-bold text-white">₹{item.amount.toLocaleString()}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-8 text-sm">
                    No categories found. Upload a statement or add transactions to begin tracking.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
