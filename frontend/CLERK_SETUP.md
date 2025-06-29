# Clerk Authentication Setup

## Overview
This project uses [Clerk](https://clerk.dev/) for authentication. Clerk provides a complete authentication and user management solution that's easy to implement in Next.js applications.

## Setup Instructions

### 1. Create a Clerk Account
1. Go to [clerk.dev](https://clerk.dev/) and sign up for an account
2. Create a new application in the Clerk dashboard
3. Configure your application settings (authentication methods, branding, etc.)

### 2. Get Your API Keys
From your Clerk dashboard:
1. Navigate to the API Keys section
2. Copy your Publishable Key and Secret Key

### 3. Update Environment Variables
Update the `.env.local` file in the project root with your Clerk API keys:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
CLERK_SECRET_KEY=sk_test_YOUR_SECRET_KEY
```

### 4. Authentication Flow
The application is already configured with the following authentication flow:

- **Sign In URL**: `/login`
- **Sign Up URL**: `/signup`
- **After Sign In URL**: `/` (redirects to home page after login)
- **After Sign Up URL**: `/` (redirects to home page after signup)

### 5. Protected Routes
The following routes are public and don't require authentication:
- Home page (`/`)
- Login page (`/login`)
- Signup page (`/signup`)
- Jobs API (`/api/jobs`)

All other routes require authentication. This is configured in the middleware.js file.

### 6. User Interface
The application includes:
- Login and signup forms connected to Clerk
- User button for account management
- Conditional rendering based on authentication state

## Additional Resources
- [Clerk Documentation](https://clerk.dev/docs)
- [Next.js Authentication with Clerk](https://clerk.dev/docs/nextjs/get-started-with-nextjs)