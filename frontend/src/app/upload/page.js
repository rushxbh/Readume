"use client";
import { useState } from "react";
import Link from "next/link";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [skills, setSkills] = useState([]);
  const [jobRecommendations, setJobRecommendations] = useState([]);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError("");
    } else {
      setFile(null);
      setFileName("");
      setError("Please select a valid PDF file");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile);
      setFileName(droppedFile.name);
      setError("");
    } else {
      setError("Please drop a valid PDF file");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a resume file");
      return;
    }

    setIsLoading(true);
    setError("");
    
    const formData = new FormData();
    formData.append("resume", file);

    try {
      const response = await fetch("/api/analyze-resume", {
        method: "POST",
        body: formData,
      });

      // Check for non-OK status
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }
      
      // Try to parse JSON response safely
      let data;
      try {
        const text = await response.text();
        data = JSON.parse(text);
        console.log(data)
      } catch (parseError) {
        console.error("JSON Parse Error:", parseError);
        throw new Error(`Failed to parse analysis results: ${parseError.message}`);
      }
      
      // Check for error in the data
      if (data.error) {
        throw new Error(data.error);
      }

      // Set data in state
      setSkills(data.skills || []);
      setJobRecommendations(data.job_recommendations || []);
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "An error occurred while analyzing the resume");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-blue-800">
            Readume
          </Link>
          <div className="flex gap-4 items-center">
            <Link href="/login" className="text-gray-700 hover:text-blue-600 transition-colors">
              Login
            </Link>
            <Link
              href="/signup"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
            Upload Your Resume
          </h1>

          <div className="bg-white p-6 rounded-xl shadow-md mb-8">
            <form onSubmit={handleSubmit}>
              <div
                className={`border-2 border-dashed rounded-lg p-8 mb-6 text-center cursor-pointer ${
                  error ? "border-red-400" : "border-blue-300 hover:border-blue-500"
                }`}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => document.getElementById("resumeFile").click()}
              >
                <input
                  type="file"
                  id="resumeFile"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <div className="mb-4">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-12 w-12 mx-auto text-blue-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
                <p className="text-lg font-medium mb-1">
                  Drag & Drop your resume here or click to browse
                </p>
                <p className="text-sm text-gray-500">Supports PDF files only</p>
                {fileName && (
                  <p className="mt-2 text-blue-600 font-medium">{fileName}</p>
                )}
                {error && <p className="mt-2 text-red-500">{error}</p>}
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                disabled={isLoading}
              >
                {isLoading ? "Analyzing..." : "Analyze Resume"}
              </button>
            </form>
          </div>

          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-lg text-gray-700">
                Analyzing your resume... This may take a moment.
              </p>
            </div>
          )}

          {skills.length > 0 && !isLoading && (
            <div className="bg-white p-6 rounded-xl shadow-md mb-8">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">
                Extracted Skills
              </h2>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {jobRecommendations.length > 0 && !isLoading && (
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">
                Job Recommendations
              </h2>
              <div className="space-y-4">
                {jobRecommendations.map((job, index) => {
                  // Safely parse the confidence value
                  const confidenceString = job.confidence || "0%";
                  const confidenceValue = parseFloat(confidenceString) || 0;
                  
                  return (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {index + 1}. {job.title}
                        </h3>
                        <span className="bg-blue-600 text-white px-2 py-1 rounded text-sm">
                          {job.confidence}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${confidenceValue}%` }}
                        ></div>
                      </div>
                      {job.skills_matched && job.skills_matched.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">Matched skills:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {job.skills_matched.map((skill, skillIndex) => (
                              <span
                                key={skillIndex}
                                className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full text-xs"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}