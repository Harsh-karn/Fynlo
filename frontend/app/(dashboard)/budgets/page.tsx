"use client"

import { useState } from "react"
import { BudgetList } from "@/components/budgets/BudgetList"
import { BudgetAlerts } from "@/components/budgets/BudgetAlerts"
import { CreateBudgetModal } from "@/components/budgets/CreateBudgetModal"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default function BudgetsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  const handleBudgetCreated = () => {
    setIsModalOpen(false)
    setReloadKey(k => k + 1)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white">Budgets & Alerts</h2>
          <p className="text-gray-400 mt-1">Set spending limits and get notified when you approach them.</p>
        </div>
        <Button 
          onClick={() => setIsModalOpen(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white gap-2"
        >
          <Plus className="size-4" />
          Create Budget
        </Button>
      </div>

      <BudgetAlerts reloadKey={reloadKey} />
      
      <BudgetList reloadKey={reloadKey} />

      {isModalOpen && (
        <CreateBudgetModal 
          onClose={() => setIsModalOpen(false)} 
          onSuccess={handleBudgetCreated} 
        />
      )}
    </div>
  )
}
