"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { signIn } from "next-auth/react"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, AlertCircle } from "lucide-react"

const loginSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
  password: z.string().min(8, { message: "Password must be at least 8 characters." }),
})

type LoginFormValues = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  async function onSubmit(data: LoginFormValues) {
    setLoading(true)
    setAuthError(null)
    try {
      const result = await signIn("credentials", {
        username: data.email,
        password: data.password,
        redirect: false,
      })

      if (result?.error) {
        setAuthError("Invalid email or password. Please try again.")
      } else {
        router.push("/")
        router.refresh()
      }
    } catch (error) {
      setAuthError("An unexpected error occurred. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#0a0a16] overflow-hidden px-4">
      {/* Background Glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl -z-10 animate-pulse delay-700"></div>

      <div className="w-full max-w-md bg-white/[0.02] backdrop-blur-xl border border-white/[0.05] rounded-2xl shadow-2xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Fynlo
          </h1>
          <p className="text-gray-400 text-sm">
            Sign in to access your live financial dashboard
          </p>
        </div>

        {authError && (
          <div className="flex items-center gap-2 p-3 bg-red-950/30 border border-red-800/40 rounded-lg text-red-400 text-sm">
            <AlertCircle className="shrink-0 size-4" />
            <span>{authError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-gray-300">Email Address</Label>
            <Input
              id="email"
              type="email"
              placeholder="name@example.com"
              {...register("email")}
              className={`bg-white/[0.03] border-white/[0.08] text-white focus:border-indigo-500/50 focus:ring-indigo-500/10 h-10 px-3 ${
                errors.email ? "border-red-500 focus:border-red-500" : ""
              }`}
            />
            {errors.email && (
              <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label htmlFor="password" className="text-gray-300">Password</Label>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              {...register("password")}
              className={`bg-white/[0.03] border-white/[0.08] text-white focus:border-indigo-500/50 focus:ring-indigo-500/10 h-10 px-3 ${
                errors.password ? "border-red-500 focus:border-red-500" : ""
              }`}
            />
            {errors.password && (
              <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:to-pink-600 text-white font-semibold transition-all h-10 shadow-lg shadow-indigo-500/20 active:scale-[0.98]"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </Button>
        </form>

        <div className="text-center text-xs text-gray-500 pt-2 border-t border-white/[0.05]">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-indigo-400 hover:underline">
            Register here
          </Link>
        </div>
      </div>
    </div>
  )
}
