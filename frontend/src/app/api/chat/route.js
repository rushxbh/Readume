import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { message, resumeSkills, chatHistory } = await request.json();

    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        resumeSkills,
        chatHistory
      }),
    });

    if (!response.ok) {
        const err=await response.json()
        console.log(err)
      throw new Error('Failed to get response from LLM');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: error.message || 'Failed to process chat message' },
      { status: 500 }
    );
  }
}