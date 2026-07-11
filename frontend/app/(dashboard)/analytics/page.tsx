"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SpendingChart } from "@/components/dashboard/SpendingChart"
import api from "@/lib/api"
import { Loader2 } from "lucide-react"

interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
}

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<any[]>([])
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
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
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Analytics</h2>
        <p className="text-gray-400 mt-1">Deep dive into your spending habits.</p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-gray-500 animate-pulse text-lg py-4">
          <Loader2 className="animate-spin size-5" />
          <span>Crunching financial data...</span>
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
