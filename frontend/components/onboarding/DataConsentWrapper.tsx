"use client"

import { useEffect, useState } from "react"
import { Shield, FileText, CheckCircle, Loader2 } from "lucide-react"
import api from "@/lib/api"
import { Button } from "@/components/ui/button"

export function DataConsentWrapper({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true)
  const [hasConsented, setHasConsented] = useState<boolean | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function checkConsent() {
      try {
        const res = await api.get("/auth/me")
        if (res.data) {
          setHasConsented(res.data.data_consent_given)
        }
      } catch (err) {
        console.error("Failed to check user consent", err)
      } finally {
        setLoading(false)
      }
    }
    checkConsent()
  }, [])

  const handleAccept = async () => {
    setIsSubmitting(true)
    setError(null)
    try {
      await api.patch("/auth/me", { data_consent_given: true })
      setHasConsented(true)
    } catch (err) {
      console.error("Failed to save consent", err)
      setError("We couldn't save your preference. Please try again.")
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#0f0f0f]">
        <Loader2 className="size-8 text-indigo-500 animate-spin" />
      </div>
    )
  }

  if (hasConsented === false) {
    return (
      <div className="fixed inset-0 z-50 bg-[#0f0f0f] flex items-center justify-center p-4">
        <div className="bg-[#1a1a2e] border border-[#2a2a4e] rounded-2xl max-w-2xl w-full p-8 shadow-2xl animate-in fade-in zoom-in-95">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-4 bg-indigo-500/20 text-indigo-400 rounded-2xl">
              <Shield className="size-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Your Privacy Matters</h2>
              <p className="text-gray-400 mt-1">We need your explicit consent to process your financial data.</p>
            </div>
          </div>

          <div className="space-y-4 mb-8">
            <div className="flex gap-4 p-4 bg-[#1e1e2e] rounded-xl border border-[#2a2a4e]">
              <FileText className="size-6 text-gray-400 shrink-0" />
              <div>
                <h4 className="font-medium text-white mb-1">How we use your data</h4>
                <p className="text-sm text-gray-400 leading-relaxed">
                  Fynlo securely parses your uploaded bank statements and SMS data using automated extraction and AI models to categorize your transactions and generate insights. We do not sell your data to third parties.
                </p>
              </div>
            </div>
            <div className="flex gap-4 p-4 bg-[#1e1e2e] rounded-xl border border-[#2a2a4e]">
              <CheckCircle className="size-6 text-gray-400 shrink-0" />
              <div>
                <h4 className="font-medium text-white mb-1">Your Rights (DPDP Act)</h4>
                <p className="text-sm text-gray-400 leading-relaxed">
                  You retain full ownership of your data. You can download all your transaction history or permanently delete your account and all associated data at any time from the Settings page.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-red-300 text-sm">
              {error}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 items-center justify-end border-t border-[#2a2a4e] pt-6">
            <a href="/login" className="text-gray-400 hover:text-white text-sm font-medium transition-colors">
              I decline (Sign Out)
            </a>
            <Button 
              onClick={handleAccept} 
              disabled={isSubmitting}
              className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white px-8 h-11"
            >
              {isSubmitting ? <Loader2 className="size-4 mr-2 animate-spin" /> : null}
              I Consent and Agree
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
