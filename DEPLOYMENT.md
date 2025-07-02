# Deploying Radha API to Railway

This guide explains how to deploy the Radha API to Railway with MongoDB integration for API key storage and a custom domain.

## Prerequisites

1. A Railway account (https://railway.app)
2. A MongoDB Atlas account (https://www.mongodb.com/cloud/atlas)
3. A domain name (www.radhaapi.me)
4. Git installed on your machine

## Step 1: Set Up MongoDB Atlas

1. Log in to MongoDB Atlas and create a new project
2. Create a new cluster (the free tier is sufficient for starting)
3. Set up a database user with read and write permissions
4. Add your IP address to the IP whitelist (for development) or allow access from anywhere (for production)
5. Once the cluster is created, click "Connect" > "Connect your application"
6. Copy the connection string (it will look like: `mongodb+srv://<username>:<password>@cluster0.mongodb.net/radhaapi`)
7. Replace `<username>` and `<password>` with your actual MongoDB user credentials

## Step 2: Deploy to Railway

### Option 1: Deploy using Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Set the required environment variables:
   ```bash
   railway variables set MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/radhaapi
   railway variables set DEFAULT_API_KEY=your_secure_default_api_key
   ```

5. Deploy your application:
   ```bash
   railway up
   ```

### Option 2: Deploy using Railway Dashboard

1. Log in to Railway (https://railway.app)
2. Create a new project and select "Deploy from GitHub"
3. Connect your GitHub account and select the repository
4. Configure the environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `DEFAULT_API_KEY`: A secure default API key (optional)
5. Deploy the application

## Step 3: Set Up Custom Domain

1. In the Railway dashboard, go to your project
2. Click on "Settings" > "Domains"
3. Add your custom domain: `www.radhaapi.me`
4. Railway will provide you with DNS records (usually a CNAME record)
5. Go to your domain registrar's dashboard and add these DNS records
6. Wait for DNS propagation (can take up to 48 hours, but usually less)

## Environment Variables

The following environment variables should be configured in Railway:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://username:password@cluster0.mongodb.net/radhaapi` |
| `DEFAULT_API_KEY` | Default API key for access | `your_secure_default_api_key` |
| `PORT` | Port for the application (set by Railway automatically) | `8002` |

## Verifying Deployment

1. After deployment is complete, Railway will provide you with a URL to access your application
2. Open the URL in your browser to make sure the application is running correctly
3. Check the application logs for any errors

## Monitoring and Scaling

1. Use Railway's dashboard to monitor the application's performance and logs
2. Scale the application as needed by adjusting the resources in Railway's dashboard

## Database Backups

1. MongoDB Atlas provides automated backups
2. Configure backup settings in MongoDB Atlas dashboard to ensure data safety

## API Key Management

With the MongoDB integration:
1. API keys are now stored persistently in the database
2. The default API key is set via environment variable or generated at startup
3. New API keys can be generated through the API and will be stored in MongoDB

## Troubleshooting

If you encounter issues during deployment:

1. Check the application logs in Railway dashboard
2. Verify MongoDB connection string is correct
3. Ensure all required environment variables are set
4. Check that the MongoDB user has appropriate permissions
5. Verify that MongoDB network access allows connections from Railway's IP addresses

## Security Considerations

1. Always use a secure, random API key for the `DEFAULT_API_KEY` environment variable
2. Use a strong password for your MongoDB user
3. Consider enabling IP restrictions in MongoDB Atlas for production deployments
4. The application uses HTTPS automatically with Railway's provided domain
