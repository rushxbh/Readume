import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { email, password } = await request.json();

    // Validate input
    if (!email || !password) {
      return NextResponse.json(
        { message: 'Email and password are required' },
        { status: 400 }
      );
    }

    // For demo purposes, accept any valid-looking email/password
    // In a real app, you would verify against your database
    if (email.includes('@') && password.length >= 6) {
      // Create a simple session (in a real app, use a proper auth system)
      return NextResponse.json(
        { 
          message: 'Login successful',
          user: { email, id: '123', name: email.split('@')[0] }
        },
        { status: 200 }
      );
    }

    return NextResponse.json(
      { message: 'Invalid credentials' },
      { status: 401 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}