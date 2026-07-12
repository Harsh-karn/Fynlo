"use client"

import { useEffect } from "react"
import { usePathname } from "next/navigation"

interface AdUnitProps {
  adSlot: string
  adFormat?: "auto" | "fluid" | "horizontal" | "vertical" | "rectangle"
  fullWidthResponsive?: boolean
  className?: string
}

export function AdUnit({ 
  adSlot, 
  adFormat = "auto", 
  fullWidthResponsive = true,
  className = ""
}: AdUnitProps) {
  const pathname = usePathname()

  useEffect(() => {
    try {
      // @ts-ignore
      const adsbygoogle = window.adsbygoogle || []
      adsbygoogle.push({})
    } catch (err) {
      console.error("AdSense error", err)
    }
  }, [pathname])

  return (
    <div className={`my-6 overflow-hidden flex justify-center bg-[#1e1e2e]/50 border border-white/5 rounded-xl ${className}`}>
      {/* 
        This is a responsive ad unit.
        In development, AdSense usually won't render actual ads unless added to allowed test domains.
      */}
      <ins
        className="adsbygoogle w-full block"
        data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
        data-ad-slot={adSlot}
        data-ad-format={adFormat}
        data-full-width-responsive={fullWidthResponsive ? "true" : "false"}
      />
    </div>
  )
}
