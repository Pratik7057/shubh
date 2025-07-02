# Railway Deployment Quick Reference

This document provides a quick reference for deploying the Radha API to Railway with the domain `www.radhaapi.me`.

## Prerequisites
- Railway account (https://railway.app)
- MongoDB Atlas account with a cluster set up
- Domain name (www.radhaapi.me) with access to DNS settings

## Step 1: Push Code to GitHub
Ensure your code is in a GitHub repository that Railway can access.

## Step 2: Deploy to Railway

### Option 1: Railway Dashboard
1. Log in to Railway
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository
5. Configure the environment variables:

```
MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/radhaapi
DEFAULT_API_KEY=your_secure_default_api_key
```

6. Click "Deploy"

### Option 2: Railway CLI
1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and link project:
```bash
railway login
railway link
```

3. Set environment variables:
```bash
railway variables set MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/radhaapi
railway variables set DEFAULT_API_KEY=your_secure_default_api_key
```

4. Deploy:
```bash
railway up
```

## Step 3: Configure Domain
1. In Railway dashboard, go to your project
2. Click "Settings" > "Domains"
3. Add your domain: `www.radhaapi.me`
4. Copy the CNAME target provided by Railway

## Step 4: Configure DNS
At your domain registrar:
1. Add a CNAME record:
   - Host: `www`
   - Target: The CNAME target from Railway
   - TTL: 3600 (or automatic)

2. For the root domain (optional):
   - Add either an ALIAS/ANAME record or redirect to www

## Step 5: Verify Deployment
1. Wait for DNS propagation (can take 24-48 hours)
2. Visit `https://www.radhaapi.me`
3. Test the API endpoints:
   - `https://www.radhaapi.me/api` - Should return the default API key
   - `https://www.radhaapi.me/health` - Should return status information

## Environment Variables Reference

| Variable | Description | Required? |
|----------|-------------|-----------|
| `MONGODB_URI` | MongoDB connection string | Yes |
| `DEFAULT_API_KEY` | Default API key | No |

## Monitoring & Maintenance
- View logs: Railway dashboard > Project > Deployments > Latest deployment > Logs
- Update code: Push changes to GitHub and Railway will automatically redeploy
- Scale: Railway dashboard > Project > Settings > Resources

## Troubleshooting
- Check Railway logs for errors
- Verify MongoDB connection using the `/health` endpoint
- Check DNS settings using a tool like https://dnschecker.org/

## Railway-Specific Commands
- Restart service: `railway service restart`
- View logs: `railway logs`
- SSH into container: `railway ssh`
