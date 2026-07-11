"use client"

import { useEffect, useState } from "react"
import { Wallet, AlertCircle, RefreshCw, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"

interface Budget {
  id: string
  category: string
  limit_amount: number
  period: string
  current_spend: number
  usage_percent: number
}

const CATEGORY_COLORS: Record<string, string> = {
  food: "bg-orange-500",
  transport: "bg-blue-500",
  shopping: "bg-purple-500",
  entertainment: "bg-pink-500",
  utilities: "bg-yellow-500",
  health: "bg-green-500",
  education: "bg-cyan-500",
  rent: "bg-red-500",
  salary: "bg-emerald-500",
  investment: "bg-teal-500",
  other: "bg-gray-500",
}

export function BudgetList({ reloadKey }: { reloadKey: number }) {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [localReload, setLocalReload] = useState(0)

  useEffect(() => {
    const fetchBudgets = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await api.get("/budgets/")
        if (res.data) {
          setBudgets(res.data)
        }
      } catch (e) {
        console.error("Failed to fetch budgets", e)
        setError("Could not retrieve your budgets. Please try again.")
      } finally {
        setLoading(false)
      }
    }
    fetchBudgets()
  }, [reloadKey, localReload])

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/budgets/${id}`)
      setLocalReload(k => k + 1)
    } catch (e) {
      console.error("Failed to delete budget", e)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-[#1e1e2e] border border-[#2a2a4e] rounded-xl h-40 p-6 flex flex-col justify-between">
            <div className="flex justify-between">
              <div className="h-5 w-1/3 bg-white/5 rounded"></div>
              <div className="h-5 w-1/4 bg-white/5 rounded"></div>
            </div>
            <div className="space-y-2 mt-4">
              <div className="h-2 w-full bg-white/5 rounded-full"></div>
              <div className="h-4 w-1/2 bg-white/5 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-500/20 bg-red-950/10 p-12 text-center flex flex-col items-center justify-center space-y-4">
        <div className="p-4 bg-red-500/10 rounded-full text-red-400">
          <AlertCircle className="w-8 h-8" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">Failed to load budgets</p>
          <p className="text-xs text-gray-400 mt-1">{error}</p>
        </div>
        <Button onClick={() => setLocalReload(k => k + 1)} variant="outline" className="bg-transparent border-[#2a2a4e] text-white hover:bg-[#2a2a4e]/50 gap-2">
          <RefreshCw className="size-4" /> Try Again
        </Button>
      </div>
    )
  }

  if (budgets.length === 0) {
    return (
      <div className="rounded-2xl border border-[#2a2a4e] bg-[#1e1e2e] p-16 text-center flex flex-col items-center justify-center space-y-4">
        <div className="p-5 bg-indigo-500/10 rounded-full text-indigo-400">
          <Wallet className="w-10 h-10 animate-pulse" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">No Budgets Set</h3>
          <p className="text-sm text-gray-400 max-w-md mt-2 mx-auto leading-relaxed">
            Take control of your spending by setting limits for your favorite categories like Food, Shopping, or Utilities.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {budgets.map((budget) => {
        const isCritical = budget.usage_percent >= 100
        const isWarning = budget.usage_percent >= 80 && budget.usage_percent < 100
        
        let progressColor = CATEGORY_COLORS[budget.category.toLowerCase()] || CATEGORY_COLORS.other
        if (isCritical) progressColor = "bg-red-500"
        else if (isWarning) progressColor = "bg-yellow-500"

        return (
          <div key={budget.id} className="bg-[#1e1e2e] border border-[#2a2a4e] rounded-xl p-6 hover:border-[#3a3a5e] transition-colors relative group">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="font-semibold text-lg text-white capitalize">{budget.category}</h3>
                <p className="text-sm text-gray-400 capitalize">{budget.period} limit</p>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-bold text-white text-lg">₹{budget.limit_amount.toLocaleString()}</span>
                <button 
                  onClick={() => handleDelete(budget.id)}
                  className="p-1.5 text-gray-400 hover:text-red-400 rounded-md hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                  title="Delete budget"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Spent: <strong className="text-gray-200">₹{budget.current_spend.toLocaleString(undefined, { maximumFractionDigits: 2 })}</strong></span>
                <span className={`font-medium ${isCritical ? 'text-red-400' : isWarning ? 'text-yellow-400' : 'text-gray-400'}`}>
                  {budget.usage_percent.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${progressColor}`}
                  style={{ width: `${Math.min(budget.usage_percent, 100)}%` }}
                />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
