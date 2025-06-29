import {
  ClerkProvider,
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton
} from '@clerk/nextjs';
import './globals.css'
import Link from 'next/link';

export default function Home() {
  return (
    <ClerkProvider>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        <nav className="bg-white shadow-sm p-4">
          <div className="container mx-auto flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-blue-800">
              Readume
            </Link>
            <div className="flex items-center gap-4">
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    Sign In
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </nav>

        <main className="container mx-auto px-4 py-12">
          <SignedOut>
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-6">Welcome to Readume</h1>
              <p className="text-xl text-gray-600 mb-8">Optimize your resume and find the perfect job match</p>
              <div className="flex justify-center gap-4">
                <SignInButton mode="modal">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium">
                    Get Started
                  </button>
                </SignInButton>
              </div>
            </div>
          </SignedOut>
          
          <SignedIn>
            <div className="max-w-4xl mx-auto">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">Welcome to Your Dashboard</h1>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <Link href="/upload" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <h2 className="text-xl font-semibold text-blue-800 mb-2">Upload Resume</h2>
                  <p className="text-gray-600">Analyze your resume and get personalized recommendations</p>
                </Link>
                
                <Link href="/jobs" className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <h2 className="text-xl font-semibold text-blue-800 mb-2">Browse Jobs</h2>
                  <p className="text-gray-600">Explore job listings that match your skills and experience</p>
                </Link>
              </div>
            </div>
          </SignedIn>
        </main>
      </div>
    </ClerkProvider>
  );
}