import { TransactionTable } from "@/components/transactions/TransactionTable"

export default function TransactionsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white">Transactions</h2>
          <p className="text-gray-400 mt-1">Manage and view your expenses and income.</p>
        </div>
      </div>
      
      <TransactionTable />
    </div>
  )
}
