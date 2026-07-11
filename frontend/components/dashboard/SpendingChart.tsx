"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"

interface TrendData {
  month: string
  income: number
  expense: number
}

interface SpendingChartProps {
  data?: TrendData[]
}

export function SpendingChart({ data = [] }: SpendingChartProps) {
  const hasData = data && data.length > 0

  return (
    <Card className="bg-[#1e1e2e] border-[#2a2a4e] text-white col-span-4 lg:col-span-2">
      <CardHeader>
        <CardTitle>Cash Flow Overview</CardTitle>
      </CardHeader>
      <CardContent className="pl-2">
        {hasData ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <XAxis dataKey="month" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value}`} />
              <Tooltip 
                cursor={{fill: '#2a2a4e'}} 
                contentStyle={{backgroundColor: '#1a1a2e', border: '1px solid #2a2a4e', borderRadius: '8px'}}
              />
              <Bar dataKey="income" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-gray-500 text-sm">
            No historical data found.
          </div>
        )}
      </CardContent>
    </Card>
  )
}

