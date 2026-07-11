"use client"

import { useEffect, useState } from "react"
import { AlertCircle, AlertTriangle } from "lucide-react"
import api from "@/lib/api"

interface AlertData {
  budget_id: string
  category: string
  limit_amount: number
  current_spend: number
  usage_percent: number
  severity: "warning" | "critical"
  message: string
}

export function BudgetAlerts({ reloadKey }: { reloadKey: number }) {
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await api.get("/budgets/alerts")
        if (res.data) {
          setAlerts(res.data)
        }
      } catch (err) {
        console.error("Failed to fetch budget alerts", err)
      } finally {
        setLoading(false)
      }
    }
    fetchAlerts()
  }, [reloadKey])

  if (loading || alerts.length === 0) return null

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div 
          key={alert.budget_id} 
          className={`flex items-start gap-4 p-4 rounded-xl border ${
            alert.severity === "critical" 
              ? "bg-red-950/20 border-red-900/30 text-red-200" 
              : "bg-yellow-950/20 border-yellow-900/30 text-yellow-200"
          }`}
        >
          <div className={`p-2 rounded-full shrink-0 ${
            alert.severity === "critical" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
          }`}>
            {alert.severity === "critical" ? <AlertCircle className="size-5" /> : <AlertTriangle className="size-5" />}
          </div>
          <div className="flex-1 pt-1">
            <h4 className="font-semibold text-sm">
              {alert.category.charAt(0).toUpperCase() + alert.category.slice(1)} Budget {alert.severity === "critical" ? "Exceeded" : "Warning"}
            </h4>
            <p className="text-sm opacity-80 mt-1">{alert.message}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
