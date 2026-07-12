go# Custom Domain Setup Guide (GoDaddy)

Since you purchased your domain from **GoDaddy**, you don't need to buy anything from Vercel or Render. You simply need to point your GoDaddy domain to your existing hosting platforms using DNS records.

Assuming your domain is `yourdomain.com`:

## 1. Frontend (Next.js)
We will host the main website at `yourdomain.com` (and `www.yourdomain.com`).

**In your GoDaddy DNS settings, add the following records:**
*   **Type**: `A`
    *   **Name**: `@`
    *   **Value**: `76.76.21.21` (Vercel's IP address)
*   **Type**: `CNAME`
    *   **Name**: `www`
    *   **Value**: `cname.vercel-dns.com`

**Next Steps**: Go to your Vercel Dashboard -> Fynlo Project -> Settings -> Domains, and add `yourdomain.com`. Vercel will verify the GoDaddy records and issue an SSL certificate automatically.

---

## 2. Backend (FastAPI on Render)
We will host the API on a subdomain: `api.yourdomain.com`.

**In your GoDaddy DNS settings, add the following record:**
*   **Type**: `CNAME`
    *   **Name**: `api`
    *   **Value**: `fynlo-api.onrender.com` (Replace with your actual Render URL if different)

**Next Steps**: Go to your Render Dashboard -> Web Service -> Settings -> Custom Domains, and add `api.yourdomain.com`.

---

## 3. Update Codebase Environment Variables
Once the domains are active, you must update your environment variables so the apps talk to the new domains instead of the temporary ones.

**Frontend (`frontend/.env.local` or Vercel Env Vars):**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
```

**Android App (`android/app/src/main/java/com/example/flowmoney/MainActivity.kt`):**
Update the WebView URL in `MainActivity.kt`:
```kotlin
loadUrl("https://yourdomain.com")
```

**Backend (`backend/.env` or Render Env Vars):**
Update your environment variable so CORS allows requests from your new domain:
```env
FRONTEND_URL=https://yourdomain.com
```
