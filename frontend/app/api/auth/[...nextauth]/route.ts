import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import api from "@/lib/api"

async function refreshAccessToken(token: any) {
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
            return {
              id: "1",
              accessToken: res.data.access_token,
              refreshToken: res.data.refresh_token,
              accessTokenExpires: Date.now() + 30 * 60 * 1000,
            } as any
          }
          return null
        } catch (e) {
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
      // Initial sign in
      if (user) {
        (token as any).accessToken = (user as any).accessToken;
        (token as any).refreshToken = (user as any).refreshToken;
        (token as any).accessTokenExpires = (user as any).accessTokenExpires;
        return token
      }

      // Return previous token if the access token has not expired yet
      if (Date.now() < ((token as any).accessTokenExpires as number)) {
        return token
      }

      // Access token has expired, try to update it
      return refreshAccessToken(token)
    },
    async session({ session, token }) {
      (session as any).accessToken = (token as any).accessToken;
      (session as any).error = (token as any).error;
      return session
    }
  }
})

export { handler as GET, handler as POST }

