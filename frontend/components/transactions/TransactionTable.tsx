"use client"

import { useEffect, useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import api from "@/lib/api"
import { CreditCard } from "lucide-react"

const categoryColors: Record<string, string> = {
  food: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  transport: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  shopping: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  entertainment: "bg-pink-500/10 text-pink-500 border-pink-500/20",
  utilities: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  health: "bg-green-500/10 text-green-500 border-green-500/20",
  salary: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  other: "bg-gray-500/10 text-gray-500 border-gray-500/20",
}

interface Transaction {
  id: string
  transaction_date: string
  description: string
  merchant_name?: string
  category: string
  amount: number
  type: 'credit' | 'debit'
}

export function TransactionTable() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const res = await api.get('/transactions/')
        if (res.data && res.data.items) {
          setTransactions(res.data.items)
        }
      } catch (e) {
        console.error("Failed to fetch transactions:", e)
      } finally {
        setLoading(false)
      }
    }
    fetchTransactions()
  }, [])

  if (loading) {
    return (
      <div className="rounded-xl border border-[#2a2a4e] bg-[#1e1e2e] p-6 space-y-4 animate-pulse">
        <div className="h-6 w-1/4 bg-white/5 rounded"></div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4 items-center">
              <div className="h-10 w-full bg-white/5 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-xl border border-[#2a2a4e] bg-[#1e1e2e] p-12 text-center flex flex-col items-center justify-center space-y-3">
        <div className="p-4 bg-indigo-500/10 rounded-full text-indigo-400">
          <CreditCard className="w-8 h-8 animate-pulse" />
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-200">No recent transactions</p>
          <p className="text-xs text-gray-400 max-w-[240px] mt-1">
            Connect an Android device to sync messages or upload statements manually to populate transactions.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-[#2a2a4e] bg-[#1e1e2e] overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-[#2a2a4e] hover:bg-transparent">
              <TableHead className="text-gray-400">Date</TableHead>
              <TableHead className="text-gray-400">Description</TableHead>
              <TableHead className="text-gray-400">Merchant</TableHead>
              <TableHead className="text-gray-400">Category</TableHead>
              <TableHead className="text-right text-gray-400">Amount</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((tx) => (
              <TableRow key={tx.id} className="border-[#2a2a4e] hover:bg-[#2a2a4e]/50">
                <TableCell className="font-medium text-gray-300 whitespace-nowrap">{new Date(tx.transaction_date).toLocaleDateString()}</TableCell>
                <TableCell className="text-gray-300 max-w-[200px] truncate">{tx.description}</TableCell>
                <TableCell className="text-gray-300">{tx.merchant_name || '-'}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={categoryColors[tx.category] || categoryColors.other}>
                    {tx.category.charAt(0).toUpperCase() + tx.category.slice(1)}
                  </Badge>
                </TableCell>
                <TableCell className={`text-right font-medium whitespace-nowrap ${tx.type === 'credit' ? 'text-emerald-500' : 'text-white'}`}>
                  {tx.type === 'credit' ? '+' : '-'}₹{(tx.amount / 100).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
