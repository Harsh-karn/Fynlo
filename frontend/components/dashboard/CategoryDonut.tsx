"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { PieChart as PieIcon } from "lucide-react"

interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
}

interface CategoryDonutProps {
  data: CategoryBreakdown[]
}

const CATEGORY_COLORS: Record<string, string> = {
  food: "#f97316",        // Orange
  transport: "#3b82f6",   // Blue
  shopping: "#a855f7",    // Purple
  entertainment: "#ec4899", // Pink
  utilities: "#eab308",   // Yellow
  health: "#22c55e",      // Green
  education: "#06b6d4",   // Cyan
  rent: "#ef4444",        // Red
  salary: "#10b981",      // Emerald
  investment: "#14b8a6",  // Teal
  other: "#6b7280",       // Gray
}

export function CategoryDonut({ data }: CategoryDonutProps) {
  const hasData = data && data.length > 0

  const chartData = hasData 
    ? data.map(item => ({
        name: item.category.charAt(0).toUpperCase() + item.category.slice(1),
        value: item.amount,
        color: CATEGORY_COLORS[item.category.toLowerCase()] || CATEGORY_COLORS.other,
        percentage: item.percentage
      }))
    : []

  return (
    <Card className="bg-[#1e1e2e] border-[#2a2a4e] text-white col-span-4 lg:col-span-2">
      <CardHeader>
        <CardTitle>Expenses by Category</CardTitle>
      </CardHeader>
      <CardContent className="h-[250px] flex items-center justify-center">
        {!hasData ? (
          <div className="flex flex-col items-center justify-center text-center p-6 space-y-3">
            <div className="p-4 bg-indigo-500/10 rounded-full text-indigo-400">
              <PieIcon className="w-8 h-8 animate-pulse" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-200">No category breakdown found</p>
              <p className="text-xs text-gray-400 max-w-[240px] mt-1">
                Upload your bank statement or record transaction messages to populate category analysis.
              </p>
            </div>
          </div>
        ) : (
          <div className="w-full flex flex-col md:flex-row items-center justify-between gap-4 h-full">
            {/* Pie Chart container */}
            <div className="w-full md:w-1/2 h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1a1a2e", border: "1px solid #2a2a4e", borderRadius: "8px" }}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    formatter={(value: any, name: any, props: any) => [
                      `₹${Number(value).toLocaleString()} (${props.payload.percentage}%)`,
                      name
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Legend container */}
            <div className="w-full md:w-1/2 space-y-2 max-h-[200px] overflow-y-auto pr-2">
              {chartData.map((entry, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: entry.color }} />
                    <span className="text-gray-300 truncate max-w-[120px]">{entry.name}</span>
                  </div>
                  <span className="font-semibold text-white shrink-0">
                    {entry.percentage}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
