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

import { Button } from "@/components/ui/button"
import api from "@/lib/api"
import { CreditCard, ChevronLeft, ChevronRight, AlertCircle, RefreshCw } from "lucide-react"

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
  confidence_score?: number
  needs_review?: boolean
}


export function TransactionTable() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState(20)
  const [total, setTotal] = useState(0)
  const [reloadKey, setReloadKey] = useState(0)

  const [updating, setUpdating] = useState<string | null>(null)

  useEffect(() => {
    const fetchTransactions = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await api.get(`/transactions/?page=${page}&limit=${limit}`)
        if (res.data) {
          setTransactions(res.data.items || [])
          setTotal(res.data.total || 0)
        }
      } catch (e) {
        console.error("Failed to fetch transactions:", e)
        setError("Could not retrieve transactions. Please check your network connection.")
      } finally {
        setLoading(false)
      }
    }
    fetchTransactions()
  }, [page, limit, reloadKey])

  const handleCategoryChange = async (txId: string, newCategory: string) => {
    try {
      setUpdating(txId)
      const res = await api.patch(`/transactions/${txId}`, { category: newCategory })
      if (res.data) {
        setTransactions(txs => txs.map(tx => tx.id === txId ? { ...tx, category: newCategory, needs_review: false } : tx))
      }
    } catch (e) {
      console.error("Failed to update category:", e)
    } finally {
      setUpdating(null)
    }
  }

  const totalPages = Math.ceil(total / limit)

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

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-950/10 p-12 text-center flex flex-col items-center justify-center space-y-4">
        <div className="p-4 bg-red-500/10 rounded-full text-red-400">
          <AlertCircle className="w-8 h-8" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">Failed to load transactions</p>
          <p className="text-xs text-gray-400 max-w-[280px] mt-1">
            {error}
          </p>
        </div>
        <Button
          onClick={() => setReloadKey(k => k + 1)}
          variant="outline"
          className="bg-transparent border-[#2a2a4e] text-white hover:bg-[#2a2a4e]/50 gap-2 px-5"
        >
          <RefreshCw className="size-4" />
          Try Again
        </Button>
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
    <div className="rounded-xl border border-[#2a2a4e] bg-[#1e1e2e] overflow-hidden flex flex-col">
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
                  <div className="flex items-center gap-2">
                    <select
                      value={tx.category}
                      disabled={updating === tx.id}
                      onChange={(e) => handleCategoryChange(tx.id, e.target.value)}
                      className={`text-xs px-2 py-1 rounded-md border appearance-none cursor-pointer outline-none transition-colors ${
                        tx.needs_review 
                          ? 'border-red-500/50 bg-red-500/10 text-red-400 focus:border-red-500' 
                          : categoryColors[tx.category] || categoryColors.other
                      }`}
                    >
                      {Object.keys(categoryColors).map(cat => (
                        <option key={cat} value={cat} className="bg-[#1e1e2e] text-white">
                          {cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </option>
                      ))}
                    </select>
                    {tx.needs_review && (
                      <div className="flex items-center gap-1 text-red-400" title="Low confidence, please review">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {tx.confidence_score !== undefined && (
                          <span className="text-[10px]">{(tx.confidence_score * 100).toFixed(0)}%</span>
                        )}
                      </div>
                    )}
                    {!tx.needs_review && tx.confidence_score !== undefined && (
                       <span className="text-[10px] text-gray-500" title="AI Confidence">
                         {(tx.confidence_score * 100).toFixed(0)}%
                       </span>
                    )}
                  </div>
                </TableCell>
                <TableCell className={`text-right font-medium whitespace-nowrap ${tx.type === 'credit' ? 'text-emerald-500' : 'text-white'}`}>
                  {tx.type === 'credit' ? '+' : '-'}₹{tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-[#2a2a4e] bg-[#1a1a2e]/30 text-sm">
        <div className="text-gray-400">
          Showing <span className="text-white font-medium">{Math.min((page - 1) * limit + 1, total)}</span> to{" "}
          <span className="text-white font-medium">{Math.min(page * limit, total)}</span> of{" "}
          <span className="text-white font-medium">{total}</span> results
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-xs">Rows per page:</span>
            <select
              value={limit}
              onChange={(e) => {
                setLimit(Number(e.target.value))
                setPage(1)
              }}
              className="bg-[#1e1e2e] border border-[#2a2a4e] text-white text-xs rounded px-2 py-1 outline-none focus:border-indigo-500"
            >
              {[10, 20, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="icon-sm"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="bg-transparent border-[#2a2a4e] text-white hover:bg-[#2a2a4e]/50 disabled:opacity-30"
            >
              <ChevronLeft className="size-4" />
            </Button>
            <span className="text-gray-300 px-2 min-w-[3rem] text-center">
              Page {page} of {totalPages || 1}
            </span>
            <Button
              variant="outline"
              size="icon-sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="bg-transparent border-[#2a2a4e] text-white hover:bg-[#2a2a4e]/50 disabled:opacity-30"
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

