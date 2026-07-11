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
import api from "@/lib/api"

const registerSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  email: z.string().email({ message: "Please enter a valid email address." }),
  phone_number: z.string().optional().or(z.literal("")),
  password: z.string().min(8, { message: "Password must be at least 8 characters." }),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match.",
  path: ["confirmPassword"],
})

type RegisterFormValues = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      phone_number: "",
      password: "",
      confirmPassword: "",
    },
  })

  async function onSubmit(data: RegisterFormValues) {
    setLoading(true)
    setErrorMsg(null)
    try {
      // 1. Call Backend Registration Endpoint
      await api.post("/auth/register", {
        email: data.email,
        password: data.password,
        name: data.name,
        phone_number: data.phone_number || null,
        currency: "INR" // Default currency
      })

      // 2. Auto-login on success
      const loginResult = await signIn("credentials", {
        username: data.email,
        password: data.password,
        redirect: false,
      })

      if (loginResult?.error) {
        // Redirect to login if auto-login fails for some reason
        router.push("/login?registered=true")
      } else {
        router.push("/")
        router.refresh()
      }
    } catch (err) {
      const error = err as {
        response?: {
          data?: {
            error?: {
              message?: string;
            };
          };
          status?: number;
        };
      };
      if (error.response?.data?.error?.message) {
        setErrorMsg(error.response.data.error.message)
      } else if (error.response?.status === 400) {
        setErrorMsg("A user with this email already exists.")
      } else {
        setErrorMsg("Failed to create account. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#0a0a16] overflow-hidden px-4 py-12">
      {/* Background Glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl -z-10 animate-pulse delay-700"></div>

      <div className="w-full max-w-md bg-white/[0.02] backdrop-blur-xl border border-white/[0.05] rounded-2xl shadow-2xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Fynlo
          </h1>
          <p className="text-gray-400 text-sm">
            Create your account to start tracking UPI expenses
          </p>
        </div>

        {errorMsg && (
          <div className="flex items-center gap-2 p-3 bg-red-950/30 border border-red-800/40 rounded-lg text-red-400 text-sm">
            <AlertCircle className="shrink-0 size-4" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-gray-300">Full Name</Label>
            <Input
              id="name"
              type="text"
              placeholder="John Doe"
              {...register("name")}
              className={`bg-white/[0.03] border-white/[0.08] text-white focus:border-indigo-500/50 focus:ring-indigo-500/10 h-10 px-3 ${
                errors.name ? "border-red-500 focus:border-red-500" : ""
              }`}
            />
            {errors.name && (
              <p className="text-red-400 text-xs mt-1">{errors.name.message}</p>
            )}
          </div>

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
            <Label htmlFor="phone_number" className="text-gray-300">Phone Number (Optional)</Label>
            <Input
              id="phone_number"
              type="text"
              placeholder="+919876543210"
              {...register("phone_number")}
              className="bg-white/[0.03] border-white/[0.08] text-white focus:border-indigo-500/50 focus:ring-indigo-500/10 h-10 px-3"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-gray-300">Password</Label>
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

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-gray-300">Confirm Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              {...register("confirmPassword")}
              className={`bg-white/[0.03] border-white/[0.08] text-white focus:border-indigo-500/50 focus:ring-indigo-500/10 h-10 px-3 ${
                errors.confirmPassword ? "border-red-500 focus:border-red-500" : ""
              }`}
            />
            {errors.confirmPassword && (
              <p className="text-red-400 text-xs mt-1">{errors.confirmPassword.message}</p>
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
                Creating account...
              </>
            ) : (
              "Register"
            )}
          </Button>
        </form>

        <div className="text-center text-xs text-gray-500 pt-2 border-t border-white/[0.05]">
          Already have an account?{" "}
          <Link href="/login" className="text-indigo-400 hover:underline">
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  )
}
