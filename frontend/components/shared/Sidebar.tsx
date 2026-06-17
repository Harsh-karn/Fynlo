import Link from 'next/link'
import { Home, CreditCard, Upload, PieChart, Wallet, Settings } from 'lucide-react'

export function Sidebar() {
  return (
    <div className="w-64 h-full bg-[#1a1a2e] text-white flex flex-col border-r border-[#2a2a4e]">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">Fynlo</h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        <NavItem href="/" icon={<Home size={20} />} label="Overview" />
        <NavItem href="/transactions" icon={<CreditCard size={20} />} label="Transactions" />
        <NavItem href="/upload" icon={<Upload size={20} />} label="Upload Statement" />
        <NavItem href="/analytics" icon={<PieChart size={20} />} label="Analytics" />
        <NavItem href="/budgets" icon={<Wallet size={20} />} label="Budgets" />
      </nav>
      
      <div className="p-4 border-t border-[#2a2a4e]">
        <NavItem href="/settings" icon={<Settings size={20} />} label="Settings" />
      </div>
    </div>
  )
}

function NavItem({ href, icon, label }: { href: string, icon: React.ReactNode, label: string }) {
  return (
    <Link href={href} className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-[#2a2a4e] transition-colors text-gray-300 hover:text-white">
      {icon}
      <span>{label}</span>
    </Link>
  )
}
