"use client";

import { useEffect, useState } from "react";
import { StatsCards } from "@/components/dashboard/StatsCards"
import { SpendingChart } from "@/components/dashboard/SpendingChart"
import { CategoryDonut } from "@/components/dashboard/CategoryDonut"
import { AlertCircle, RefreshCw, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"

interface TrendData {
  month: string
  income: number
  expense: number
}

interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState({
    income: 0,
    expense: 0,
    savings: 0,
    savingsRate: 0.0
  });
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dateStr = `${yyyy}-${mm}`;

        const [summaryRes, trendsRes, breakdownRes] = await Promise.all([
          api.get(`/analytics/summary?date=${dateStr}`),
          api.get(`/analytics/trends`),
          api.get(`/analytics/category-breakdown?date=${dateStr}`)
        ]);

        if (summaryRes.data) {
          setStats({
            income: summaryRes.data.total_income || 0,
            expense: summaryRes.data.total_expense || 0,
            savings: summaryRes.data.net_savings || 0,
            savingsRate: summaryRes.data.savings_rate || 0.0
          });
        }
        if (trendsRes.data) {
          setTrends(trendsRes.data);
        }
        if (breakdownRes.data) {
          setBreakdown(breakdownRes.data);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
        setError("Failed to load dashboard statistics. Please check your connection.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [reloadKey]);

  const totalTransactions = trends.reduce((acc, curr) => acc + curr.income + curr.expense, 0);
  const isDashboardEmpty = totalTransactions === 0 && breakdown.length === 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white">Dashboard</h2>
          <p className="text-gray-400 mt-1">Live from your Android Device.</p>
        </div>
        {isDashboardEmpty && !loading && !error && (
          <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-300 text-sm">
            <Info className="size-4 shrink-0" />
            <span>Upload a statement or sync your device to populate analytics.</span>
          </div>
        )}
      </div>
      
      {loading ? (
        <div className="space-y-6 animate-pulse">
          {/* StatsCards loading skeleton */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-[#1e1e2e] border border-[#2a2a4e] rounded-xl h-28 p-6 flex flex-col justify-between">
                <div className="h-4 w-1/2 bg-white/5 rounded"></div>
                <div className="h-6 w-3/4 bg-white/5 rounded"></div>
              </div>
            ))}
          </div>

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
            <h3 className="text-lg font-semibold text-white">Unable to load Dashboard</h3>
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
        <>
          <StatsCards {...stats} />
          
          <div className="grid gap-6 grid-cols-1 md:grid-cols-4">
            <SpendingChart data={trends} />
            <CategoryDonut data={breakdown} />
          </div>
        </>
      )}
    </div>
  )
}

