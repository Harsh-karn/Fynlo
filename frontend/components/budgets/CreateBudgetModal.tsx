"use client"

import { useState } from "react"
import { X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"

interface CreateBudgetModalProps {
  onClose: () => void
  onSuccess: () => void
}

const CATEGORIES = [
  "food", "transport", "shopping", "entertainment", 
  "utilities", "health", "education", "rent", "other"
]

export function CreateBudgetModal({ onClose, onSuccess }: CreateBudgetModalProps) {
  const [category, setCategory] = useState("food")
  const [limit, setLimit] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!limit || isNaN(Number(limit)) || Number(limit) <= 0) {
      setError("Please enter a valid limit amount")
      return
    }

    setLoading(true)
    setError(null)
    try {
      await api.post("/budgets/", {
        category,
        limit_amount: Number(limit),
        period: "monthly"
      })
      onSuccess()
    } catch (err) {
      console.error("Failed to create budget", err)
      const errorMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        || "Failed to create budget. A budget for this category may already exist."
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-[#1a1a2e] border border-[#2a2a4e] rounded-2xl w-full max-w-md shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-5 border-b border-[#2a2a4e]">
          <h2 className="text-xl font-semibold text-white">Create Budget</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors p-1 rounded-md hover:bg-white/5">
            <X className="size-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="p-3 bg-red-950/30 border border-red-900/50 rounded-lg text-red-300 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Category</label>
            <select 
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-[#1e1e2e] border border-[#2a2a4e] text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 capitalize"
            >
              {CATEGORIES.map(c => (
                <option key={c} value={c} className="capitalize">{c}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Monthly Limit (₹)</label>
            <input 
              type="number" 
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              placeholder="e.g. 5000"
              className="w-full bg-[#1e1e2e] border border-[#2a2a4e] text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="pt-4 flex gap-3">
            <Button 
              type="button" 
              onClick={onClose} 
              variant="outline" 
              className="flex-1 bg-transparent border-[#2a2a4e] text-white hover:bg-white/5"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              {loading ? <Loader2 className="size-4 animate-spin" /> : "Save Budget"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
