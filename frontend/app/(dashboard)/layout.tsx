"use client"

import { useState } from 'react'
import { Sidebar } from '@/components/shared/Sidebar'
import { Header } from '@/components/shared/Header'
import { DeviceRegistrar } from '@/components/DeviceRegistrar'

import { DataConsentWrapper } from '@/components/onboarding/DataConsentWrapper'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <DataConsentWrapper>
      <div className="flex h-screen bg-[#0f0f0f] text-gray-100 font-sans overflow-hidden">
        {/* Desktop Sidebar */}
        <div className="hidden md:flex md:w-64 md:shrink-0">
          <Sidebar onClose={() => setSidebarOpen(false)} />
        </div>

        {/* Mobile Sidebar Backdrop & Drawer */}
        {sidebarOpen && (
          <div className="fixed inset-0 z-40 md:hidden flex">
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
              onClick={() => setSidebarOpen(false)}
            />
            {/* Sidebar content */}
            <div className="relative w-64 bg-[#1a1a2e] flex flex-col border-r border-[#2a2a4e] shadow-2xl z-50">
              <Sidebar onClose={() => setSidebarOpen(false)} />
            </div>
          </div>
        )}

        <div className="flex-1 flex flex-col overflow-hidden">
          <Header onMenuClick={() => setSidebarOpen(true)} />
          <main className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
            <DeviceRegistrar />
            {children}
          </main>
        </div>
      </div>
    </DataConsentWrapper>
  )
}
