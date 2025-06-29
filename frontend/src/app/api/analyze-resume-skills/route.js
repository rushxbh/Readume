import { NextResponse } from "next/server";

export async function POST(request) {
    console.log('starting')
  try {
    const formData = await request.formData();
    const file = formData.get("resume");
    const jobSkills = formData.get("jobSkills");

    if (!file) {
      return NextResponse.json(
        { error: "No file provided" },
        { status: 400 }
      );
    }

    if (!jobSkills) {
      return NextResponse.json(
        { error: "No job skills provided" },
        { status: 400 }
      );
    }

    // Create FormData for Flask server
    const flaskFormData = new FormData();
    flaskFormData.append("resume", file);
    flaskFormData.append("jobSkills", jobSkills);

    // Send to Flask server
    const flaskResponse = await fetch("http://localhost:5000/api/analyze-resume-skills", {
      method: "POST",
      body: flaskFormData,
    });

    if (!flaskResponse.ok) {
      const errorData = await flaskResponse.json();
      console.log("Flask Error:", errorData.error);
      return NextResponse.json(
        { error: errorData.error || "Error analyzing resume" },
        { status: flaskResponse.status }
      );
    }

    const results = await flaskResponse.json();
    return NextResponse.json(results);
  } catch (error) {
    console.log("Error:", error);
    return NextResponse.json(
      { error: error || "An error occurred" },
      { status: 500 }
    );
  }
}