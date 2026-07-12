"use client";

import { useSession, signOut } from 'next-auth/react'
import { Bell, LogOut, Menu } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import api from '@/lib/api'

interface HeaderProps {
  onMenuClick?: () => void
}

interface Notification {
  id: string
  title: string
  message: string
  type: string
  date: string
  read: boolean
}

export function Header({ onMenuClick }: HeaderProps) {
  const { data: session } = useSession()
  const userEmail = session?.user?.email || "User"
  const userName = userEmail.split('@')[0]
  const displayName = userName.charAt(0).toUpperCase() + userName.slice(1)

  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showNotifications, setShowNotifications] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (session) {
      api.get("/analytics/notifications")
        .then(res => setNotifications(res.data))
        .catch(err => console.error("Failed to fetch notifications", err))
    }
  }, [session])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

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
        <div className="relative" ref={dropdownRef}>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-full hover:bg-[#2a2a4e] transition-colors relative"
          >
            <Bell size={20} />
            {notifications.length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            )}
          </button>
          
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-[#1e1e2e] border border-[#2a2a4e] rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center justify-between p-4 border-b border-[#2a2a4e]">
                <h3 className="font-semibold text-white">Notifications</h3>
                <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded-full">
                  {notifications.length} New
                </span>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    <p>No new notifications</p>
                  </div>
                ) : (
                  <div className="flex flex-col">
                    {notifications.map((notif) => (
                      <div key={notif.id} className="p-4 border-b border-[#2a2a4e] hover:bg-[#2a2a4e]/50 transition-colors">
                        <div className="flex justify-between items-start mb-1">
                          <h4 className={`text-sm font-medium ${notif.type === 'warning' ? 'text-amber-400' : 'text-indigo-400'}`}>
                            {notif.title}
                          </h4>
                        </div>
                        <p className="text-xs text-gray-300 mt-1">{notif.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2 p-2 rounded-full hover:bg-[#2a2a4e] transition-colors">
          <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold">
            {displayName.charAt(0)}
          </div>
          <span className="text-sm font-medium hidden sm:block">{displayName}</span>
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

