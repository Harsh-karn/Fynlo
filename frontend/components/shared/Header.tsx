"use client";

import { useSession, signOut } from 'next-auth/react'
import { Bell, User, LogOut, Menu } from 'lucide-react'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { data: session } = useSession()
  const userEmail = session?.user?.email || "User"
  const userName = userEmail.split('@')[0]
  const displayName = userName.charAt(0).toUpperCase() + userName.slice(1)

  return (
    <header className="h-16 border-b border-[#2a2a4e] bg-[#1a1a2e]/80 backdrop-blur-md flex items-center justify-between px-4 md:px-6 sticky top-0 z-10 text-white">
      <div className="flex items-center gap-3">
        {onMenuClick && (
          <button 
            onClick={onMenuClick}
            className="md:hidden p-2 rounded-lg hover:bg-[#2a2a4e] text-gray-300 hover:text-white"
          >
            <Menu size={20} />
          </button>
        )}
      </div>
      
      <div className="flex items-center space-x-4">
        <button className="p-2 rounded-full hover:bg-[#2a2a4e] transition-colors relative">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="flex items-center space-x-2 p-2 rounded-full hover:bg-[#2a2a4e] transition-colors">
          <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center">
            <User size={16} />
          </div>
          <span className="text-sm font-medium">{displayName}</span>
        </div>
        <button 
          onClick={() => signOut({ callbackUrl: "/login" })} 
          className="p-2 rounded-full hover:bg-red-950/30 hover:text-red-400 text-gray-400 transition-colors"
          title="Sign Out"
        >
          <LogOut size={20} />
        </button>
      </div>
    </header>
  )
}

