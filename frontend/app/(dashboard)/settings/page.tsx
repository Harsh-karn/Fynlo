"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useSession, signOut } from "next-auth/react"
import { Button } from "@/components/ui/button"
import {
  Download,
  Trash2,
  AlertTriangle,
  User,
  FileJson,
  FileSpreadsheet,
  LogOut,
  Shield,
  CheckCircle,
} from "lucide-react"
import api from "@/lib/api"

export default function SettingsPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const [deleteConfirm, setDeleteConfirm] = useState(false)
  const [deleteInput, setDeleteInput] = useState("")
  const [deleting, setDeleting] = useState(false)
  const [exporting, setExporting] = useState<"csv" | "json" | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  async function handleExport(format: "csv" | "json") {
    setExporting(format)
    setErrorMsg(null)
    try {
      const response = await api.get(`/auth/me/export?format=${format}`, {
        responseType: "blob",
      })
      const mimeType = format === "json" ? "application/json" : "text/csv"
      const ext = format === "json" ? "json" : "csv"
      const blob = new Blob([response.data as BlobPart], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `fynlo_export.${ext}`
      document.body.appendChild(a)
      a.click()
      URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setSuccessMsg(`Your data has been exported as ${format.toUpperCase()}.`)
      setTimeout(() => setSuccessMsg(null), 4000)
    } catch {
      setErrorMsg("Failed to export data. Please try again.")
    } finally {
      setExporting(null)
    }
  }

  async function handleDeleteAccount() {
    if (deleteInput !== "DELETE") return
    setDeleting(true)
    setErrorMsg(null)
    try {
      await api.delete("/auth/me")
      await signOut({ redirect: false })
      router.push("/login?deleted=true")
    } catch {
      setErrorMsg("Failed to delete account. Please try again or contact support.")
      setDeleting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 py-4">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your account, data, and privacy preferences.</p>
      </div>

      {/* Success / Error banners */}
      {successMsg && (
        <div className="flex items-center gap-3 p-4 bg-green-950/40 border border-green-700/40 rounded-xl text-green-400 text-sm">
          <CheckCircle className="shrink-0 size-5" />
          {successMsg}
        </div>
      )}
      {errorMsg && (
        <div className="flex items-center gap-3 p-4 bg-red-950/40 border border-red-700/40 rounded-xl text-red-400 text-sm">
          <AlertTriangle className="shrink-0 size-5" />
          {errorMsg}
        </div>
      )}

      {/* Profile card */}
      <section className="bg-white/[0.03] border border-white/[0.07] rounded-2xl p-6 space-y-3">
        <div className="flex items-center gap-3 mb-4">
          <User className="size-5 text-indigo-400" />
          <h2 className="font-semibold text-white text-lg">Profile</h2>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500 mb-1">Name</p>
            <p className="text-white font-medium">{(session?.user as { name?: string })?.name ?? "—"}</p>
          </div>
          <div>
            <p className="text-gray-500 mb-1">Email</p>
            <p className="text-white font-medium">{(session?.user as { email?: string })?.email ?? "—"}</p>
          </div>
        </div>
      </section>

      {/* Data Export */}
      <section className="bg-white/[0.03] border border-white/[0.07] rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3 mb-1">
          <Download className="size-5 text-indigo-400" />
          <h2 className="font-semibold text-white text-lg">Export My Data</h2>
        </div>
        <p className="text-gray-400 text-sm leading-relaxed">
          Download a complete copy of your transactions and profile. Your right under India&apos;s{" "}
          <span className="text-indigo-400 font-medium">DPDP Act</span> — data portability, always on.
        </p>
        <div className="flex flex-wrap gap-3 pt-1">
          <Button
            id="export-csv-btn"
            variant="outline"
            onClick={() => handleExport("csv")}
            disabled={exporting !== null}
            className="bg-white/[0.04] border-white/[0.10] text-white hover:bg-white/[0.08] gap-2"
          >
            <FileSpreadsheet className="size-4 text-green-400" />
            {exporting === "csv" ? "Exporting…" : "Export as CSV"}
          </Button>
          <Button
            id="export-json-btn"
            variant="outline"
            onClick={() => handleExport("json")}
            disabled={exporting !== null}
            className="bg-white/[0.04] border-white/[0.10] text-white hover:bg-white/[0.08] gap-2"
          >
            <FileJson className="size-4 text-yellow-400" />
            {exporting === "json" ? "Exporting…" : "Export as JSON"}
          </Button>
        </div>
      </section>

      {/* Privacy & Compliance badge */}
      <section className="bg-indigo-950/30 border border-indigo-800/30 rounded-2xl p-5 flex items-start gap-4">
        <Shield className="size-6 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <p className="text-white font-medium text-sm">DPDP Act Compliance</p>
          <p className="text-gray-400 text-xs mt-1 leading-relaxed">
            Fynlo is built to comply with India&apos;s Digital Personal Data Protection Act, 2023. You can export or delete
            your data at any time. Deleted data is permanently erased within 30 days.
          </p>
        </div>
      </section>

      {/* Sign out */}
      <section className="bg-white/[0.03] border border-white/[0.07] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-3">
          <LogOut className="size-5 text-gray-400" />
          <h2 className="font-semibold text-white text-lg">Sign Out</h2>
        </div>
        <p className="text-gray-400 text-sm mb-4">Sign out of your Fynlo account on this device.</p>
        <Button
          id="signout-btn"
          variant="outline"
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="bg-white/[0.04] border-white/[0.10] text-white hover:bg-white/[0.08]"
        >
          Sign Out
        </Button>
      </section>

      {/* Danger Zone */}
      <section className="bg-red-950/20 border border-red-800/30 rounded-2xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Trash2 className="size-5 text-red-400" />
          <h2 className="font-semibold text-red-400 text-lg">Danger Zone</h2>
        </div>
        <p className="text-gray-400 text-sm leading-relaxed">
          <strong className="text-red-400">Permanently delete</strong> your account and all associated data — transactions,
          statements, budgets, and profile. This action is{" "}
          <strong className="text-red-400">irreversible</strong>.
        </p>

        {!deleteConfirm ? (
          <Button
            id="delete-account-btn"
            variant="destructive"
            onClick={() => setDeleteConfirm(true)}
            className="bg-red-900/50 hover:bg-red-800/60 border border-red-700/50 text-red-300"
          >
            Delete My Account
          </Button>
        ) : (
          <div className="space-y-4 p-4 bg-red-950/30 border border-red-800/40 rounded-xl">
            <p className="text-sm text-red-300 font-medium">
              Type <code className="bg-red-900/40 px-1.5 py-0.5 rounded text-red-200 font-mono">DELETE</code> to confirm:
            </p>
            <input
              id="delete-confirm-input"
              type="text"
              value={deleteInput}
              onChange={(e) => setDeleteInput(e.target.value)}
              placeholder="Type DELETE to confirm"
              className="w-full bg-white/[0.05] border border-red-800/50 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-500/70 placeholder:text-gray-600"
            />
            <div className="flex gap-3">
              <Button
                id="confirm-delete-btn"
                variant="destructive"
                disabled={deleteInput !== "DELETE" || deleting}
                onClick={handleDeleteAccount}
                className="bg-red-700 hover:bg-red-600 text-white"
              >
                {deleting ? "Deleting…" : "Permanently Delete Account"}
              </Button>
              <Button
                id="cancel-delete-btn"
                variant="outline"
                onClick={() => { setDeleteConfirm(false); setDeleteInput("") }}
                className="bg-white/[0.04] border-white/[0.10] text-white hover:bg-white/[0.08]"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
