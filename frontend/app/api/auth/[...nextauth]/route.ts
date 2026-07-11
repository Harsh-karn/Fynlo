import NextAuth, { User, Session } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { JWT } from "next-auth/jwt"
import api from "@/lib/api"

interface CustomUser extends User {
  accessToken?: string
  refreshToken?: string
  accessTokenExpires?: number
}

interface CustomJWT extends JWT {
  accessToken?: string
  refreshToken?: string
  accessTokenExpires?: number
  error?: string
}

interface CustomSession extends Session {
  accessToken?: string
  error?: string
}

async function refreshAccessToken(token: CustomJWT): Promise<CustomJWT> {
  try {
    const response = await api.post("/auth/refresh", {
      refresh_token: token.refreshToken,
    })

    const refreshedTokens = response.data

    return {
      ...token,
      accessToken: refreshedTokens.access_token,
      accessTokenExpires: Date.now() + 30 * 60 * 1000, // Token expires in 30 mins
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken,
    }
  } catch (error) {
    console.error("Error refreshing access token", error)
    return {
      ...token,
      error: "RefreshAccessTokenError",
    }
  }
}

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          // Send as urlencoded form data to backend
          const params = new URLSearchParams()
          params.append('username', credentials?.username || '')
          params.append('password', credentials?.password || '')

          const res = await api.post("/auth/login", params, {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded"
            }
          })
          
          if (res.data && res.data.access_token) {
            const user: CustomUser = {
              id: "1",
              accessToken: res.data.access_token,
              refreshToken: res.data.refresh_token,
              accessTokenExpires: Date.now() + 30 * 60 * 1000,
            }
            return user
          }
          return null
        } catch {
          return null
        }
      }
    })
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token, user }) {
      const customToken = token as CustomJWT
      const customUser = user as CustomUser

      // Initial sign in
      if (customUser) {
        customToken.accessToken = customUser.accessToken
        customToken.refreshToken = customUser.refreshToken
        customToken.accessTokenExpires = customUser.accessTokenExpires
        return customToken
      }

      // Return previous token if the access token has not expired yet
      if (customToken.accessTokenExpires && Date.now() < customToken.accessTokenExpires) {
        return customToken
      }

      // Access token has expired, try to update it
      return refreshAccessToken(customToken)
    },
    async session({ session, token }) {
      const customSession = session as CustomSession
      const customToken = token as CustomJWT

      customSession.accessToken = customToken.accessToken
      customSession.error = customToken.error
      return customSession
    }
  }
})

export { handler as GET, handler as POST }
