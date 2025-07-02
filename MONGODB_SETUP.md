# MongoDB Setup Guide for Radha API

This guide will help you set up MongoDB Atlas for use with the Radha API.

## Step 1: Create a MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up for a free account.
2. After signing up, click "Build a Database" to create a new cluster.
3. Choose the "FREE" shared cluster option.
4. Select your preferred cloud provider and region (choose one close to your users).
5. Click "Create Cluster" (this may take a few minutes).

## Step 2: Configure Database Access

1. In the left sidebar, click on "Database Access" under "Security".
2. Click "Add New Database User".
3. Enter a username and password (make sure to remember these).
4. For user privileges, select "Read and write to any database".
5. Click "Add User" to create the database user.

## Step 3: Configure Network Access

1. In the left sidebar, click on "Network Access" under "Security".
2. Click "Add IP Address".
3. For development, you can choose "Allow Access from Anywhere" (0.0.0.0/0).
4. For production, you should restrict access to specific IP addresses.
5. Click "Confirm" to add the IP address.

## Step 4: Connect to Your Cluster

1. In the left sidebar, click on "Database" under "Deployment".
2. Click "Connect" on your cluster.
3. Choose "Connect your application".
4. Select "Python" as the driver and the appropriate version.
5. Copy the connection string.
6. Replace `<password>` with your database user's password.
7. Replace `myFirstDatabase` with `radhaapi` or your preferred database name.

## Step 5: Set the Environment Variable

### Windows (PowerShell)
```powershell
$env:MONGODB_URI = "mongodb+srv://username:password@cluster0.mongodb.net/radhaapi"
```

### Linux/macOS
```bash
export MONGODB_URI="mongodb+srv://username:password@cluster0.mongodb.net/radhaapi"
```

### For Railway Deployment
Add the MONGODB_URI as an environment variable in the Railway dashboard:
1. Go to your project in Railway
2. Click "Variables"
3. Add a new variable named `MONGODB_URI` with your connection string

## Step 6: Test the Connection

Run the MongoDB setup test script:
```bash
python setup_mongo.py
```

If successful, you should see a message confirming the connection.

## Step 7: Run the Application

Start the application with:
```bash
python main.py
```

The application should now be using MongoDB for API key storage.

## Troubleshooting

### Connection Issues
- Check that your username and password are correct.
- Verify that your IP address has been added to the whitelist.
- Ensure the network where you're running the application isn't blocking MongoDB connections.

### Authentication Errors
- Double-check the username and password in the connection string.
- Make sure you've replaced `<password>` with your actual password.

### Network Errors
- If using Railway, ensure that outbound connections to MongoDB are allowed.

### Database Not Found
- The database will be created automatically on first access, so this error is unlikely.
- If you specified a custom database name, make sure it's correct in the connection string.

## Additional Resources
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Connection String URI Format](https://docs.mongodb.com/manual/reference/connection-string/)
