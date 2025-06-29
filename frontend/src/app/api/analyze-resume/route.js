// /app/api/analyze-resume/route.js
import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    // Parse the multipart form data 
    const formData = await request.formData();
    const file = formData.get("resume");

    if (!file) {
      return NextResponse.json(
        { error: "No file provided" },
        { status: 400 }
      );
    }

    // Check file type
    if (!file.type || file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: "File must be a PDF" },
        { status: 400 }
      );
    }

    // Create a new FormData object to send to Flask
    const flaskFormData = new FormData();
    flaskFormData.append("resume", file);

    // Send the file to the Flask server
    const flaskResponse = await fetch("http://localhost:5000/api/analyze-resume", {
      method: "POST",
      body: flaskFormData,
    });

    if (!flaskResponse.ok) {
      const errorData = await flaskResponse.json();
      return NextResponse.json(
        { error: errorData.error || "Error analyzing resume" },
        { status: flaskResponse.status }
      );
    }

    const results = await flaskResponse.json();
    return NextResponse.json(results);
  } catch (error) {
    console.error("Error:", error);
    return NextResponse.json(
      { error: error.message || "An error occurred" },
      { status: 500 }
    );
  }
}