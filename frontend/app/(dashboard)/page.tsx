"use client";

import { useEffect, useState } from "react";
import { StatsCards } from "@/components/dashboard/StatsCards"
import { SpendingChart } from "@/components/dashboard/SpendingChart"
import { CategoryDonut } from "@/components/dashboard/CategoryDonut"
import api from "@/lib/api"

export default function DashboardPage() {
  const [stats, setStats] = useState({
    income: 0,
    expense: 0,
    savings: 0,
    savingsRate: 0.0
  });
  const [trends, setTrends] = useState<any[]>([]);
  const [breakdown, setBreakdown] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
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
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Dashboard</h2>
        <p className="text-gray-400 mt-1">Live from your Android Device.</p>
      </div>
      
      {loading ? (
         <div className="text-gray-500 animate-pulse text-lg py-4">Syncing live financial data...</div>
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

