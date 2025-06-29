/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Explicitly tell Next.js to use the App Router only
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig