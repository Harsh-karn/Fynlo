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

export function TransactionTable() {
  const [transactions, setTransactions] = useState<any[]>([])
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

  if (loading) return <div className="p-8 text-center text-gray-500">Loading transactions...</div>
  if (transactions.length === 0) return <div className="p-8 text-center text-gray-500">No transactions found.</div>

  return (
    <div className="rounded-md border border-[#2a2a4e] bg-[#1e1e2e]">
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
              <TableCell className="font-medium text-gray-300">{new Date(tx.transaction_date).toLocaleDateString()}</TableCell>
              <TableCell className="text-gray-300">{tx.description}</TableCell>
              <TableCell className="text-gray-300">{tx.merchant_name || '-'}</TableCell>
              <TableCell>
                <Badge variant="outline" className={categoryColors[tx.category] || categoryColors.other}>
                  {tx.category.charAt(0).toUpperCase() + tx.category.slice(1)}
                </Badge>
              </TableCell>
              <TableCell className={`text-right font-medium ${tx.type === 'credit' ? 'text-emerald-500' : 'text-white'}`}>
                {tx.type === 'credit' ? '+' : '-'}₹{(tx.amount / 100).toLocaleString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
