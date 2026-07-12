import Link from "next/link"
import { Shield, Brain, Zap, ArrowRight, CheckCircle2 } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0f0f16] text-white selection:bg-indigo-500/30">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/5 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xl">
            F
          </div>
          <span className="font-semibold text-lg tracking-tight">Fynlo</span>
        </div>
        <div className="flex items-center gap-4 text-sm font-medium">
          <Link href="/login" className="text-gray-300 hover:text-white transition-colors">Log In</Link>
          <Link href="/register" className="bg-white text-black px-4 py-2 rounded-full hover:bg-gray-200 transition-colors">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6 pt-32 pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium mb-8 border border-indigo-500/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          Phase 3 Public Launch is Live
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-8 leading-tight">
          Financial intelligence, <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
            powered by AI.
          </span>
        </h1>
        
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed">
          Automate your expense tracking without sacrificing your privacy. 
          Fynlo categorizes your spending automatically while remaining 100% DPDP compliant.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/register" className="flex items-center gap-2 bg-indigo-600 text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-indigo-700 transition-all shadow-[0_0_40px_-10px_rgba(79,70,229,0.5)]">
            Start tracking for free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </main>

      {/* Features */}
      <section className="py-24 bg-[#14141d] border-y border-white/5">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-[#1e1e2e] border border-white/5">
              <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center text-indigo-400 mb-6">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Categorization</h3>
              <p className="text-gray-400 leading-relaxed">Advanced language models automatically tag and sort your transactions with high precision.</p>
            </div>
            <div className="p-8 rounded-2xl bg-[#1e1e2e] border border-white/5">
              <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center text-purple-400 mb-6">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Bank-Grade Security</h3>
              <p className="text-gray-400 leading-relaxed">Encrypted at rest and in transit. Fully compliant with India&apos;s DPDP Act. Your data is yours.</p>
            </div>
            <div className="p-8 rounded-2xl bg-[#1e1e2e] border border-white/5">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 mb-6">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Real-time Insights</h3>
              <p className="text-gray-400 leading-relaxed">Set dynamic budget thresholds and get alerted before you overspend. Total financial clarity.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-32 max-w-5xl mx-auto px-6 text-center">
        <h2 className="text-4xl font-bold tracking-tight mb-4">Simple, transparent pricing</h2>
        <p className="text-gray-400 mb-16 max-w-xl mx-auto">Start for free, upgrade when you need more power. No hidden fees or surprises.</p>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto text-left">
          {/* Free Tier */}
          <div className="p-10 rounded-3xl bg-[#14141d] border border-white/5 flex flex-col">
            <h3 className="text-2xl font-semibold mb-2">Starter</h3>
            <p className="text-gray-400 mb-6">Perfect for manual tracking</p>
            <div className="mb-8">
              <span className="text-5xl font-bold">₹0</span>
              <span className="text-gray-400">/month</span>
            </div>
            <ul className="space-y-4 mb-8 flex-1">
              {["Unlimited manual transactions", "Basic budget limits", "Standard reporting", "Community support"].map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-gray-300">
                  <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0" />
                  {feature}
                </li>
              ))}
            </ul>
            <Link href="/register" className="w-full py-3 px-6 text-center rounded-xl font-medium border border-white/10 hover:bg-white/5 transition-colors">
              Get Started
            </Link>
          </div>

          {/* Pro Tier */}
          <div className="p-10 rounded-3xl bg-gradient-to-b from-indigo-900/40 to-[#1e1e2e] border border-indigo-500/30 flex flex-col relative overflow-hidden">
            <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-indigo-400 to-transparent"></div>
            <h3 className="text-2xl font-semibold mb-2 text-indigo-100">Fynlo Pro</h3>
            <p className="text-indigo-300/70 mb-6">Unlock the full power of AI</p>
            <div className="mb-8">
              <span className="text-5xl font-bold">₹299</span>
              <span className="text-gray-400">/month</span>
            </div>
            <ul className="space-y-4 mb-8 flex-1">
              {[
                "Unlimited AI Categorization", 
                "Automated PDF Statement Parsing", 
                "Priority Email Support", 
                "Export to CSV/JSON",
                "Point-in-time recovery"
              ].map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-indigo-100">
                  <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0" />
                  {feature}
                </li>
              ))}
            </ul>
            <Link href="/register?plan=pro" className="w-full py-3 px-6 text-center rounded-xl font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-900/20">
              Upgrade to Pro
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 text-center text-gray-500 text-sm">
        <p>© 2026 Fynlo. All rights reserved. <br/> Strictly adhering to the Digital Personal Data Protection (DPDP) Act.</p>
      </footer>
    </div>
  )
}
