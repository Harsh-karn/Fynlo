import Link from 'next/link'
import { Home, CreditCard, Upload, PieChart, Wallet, Settings, X, ShieldAlert } from 'lucide-react'

interface SidebarProps {
  onClose?: () => void
}

export function Sidebar({ onClose }: SidebarProps) {
  return (
    <div className="w-full h-full bg-[#1a1a2e] text-white flex flex-col border-r border-[#2a2a4e]">
      <div className="p-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">Fynlo</h1>
        {onClose && (
          <button onClick={onClose} className="md:hidden p-1 rounded-lg hover:bg-[#2a2a4e] text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        )}
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        <NavItem href="/" icon={<Home size={20} />} label="Overview" onClick={onClose} />
        <NavItem href="/transactions" icon={<CreditCard size={20} />} label="Transactions" onClick={onClose} />
        <NavItem href="/upload" icon={<Upload size={20} />} label="Upload Statement" onClick={onClose} />
        <NavItem href="/analytics" icon={<PieChart size={20} />} label="Analytics" onClick={onClose} />
        <NavItem href="/budgets" icon={<Wallet size={20} />} label="Budgets" onClick={onClose} />
      </nav>
      
      <div className="p-4 border-t border-[#2a2a4e]">
        <NavItem href="/admin" icon={<ShieldAlert size={20} />} label="Ops / Admin" onClick={onClose} />
        <NavItem href="/settings" icon={<Settings size={20} />} label="Settings" onClick={onClose} />
      </div>
    </div>
  )
}

function NavItem({ href, icon, label, onClick }: { href: string, icon: React.ReactNode, label: string, onClick?: () => void }) {
  return (
    <Link href={href} onClick={onClick} className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-[#2a2a4e] transition-colors text-gray-300 hover:text-white">
      {icon}
      <span>{label}</span>
    </Link>
  )
}
