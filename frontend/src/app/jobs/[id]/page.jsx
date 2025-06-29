"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function JobDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [resumeMatch, setResumeMatch] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        const response = await fetch('/api/jobs');
        
        if (!response.ok) {
          throw new Error('Failed to fetch jobs');
        }
        
        const data = await response.json();
        const jobId = params.id;
        const foundJob = data.jobs[jobId];
        
        if (!foundJob) {
          throw new Error('Job not found');
        }
        
        setJob(foundJob);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchJobDetails();
  }, [params.id]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
      setError(null);
    } else {
      setResumeFile(null);
      setError('Please upload a PDF resume');
    }
  };

  const analyzeResume = async () => {
    if (!resumeFile) {
      setError('Please upload your resume first');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('jobSkills', job.job_skills); // Send job skills for analysis
      
      const response = await fetch('/api/analyze-resume-skills', {
        method: 'POST',
        body: formData,
      });
      console.log(response)
      if (!response.ok) {
        throw new Error('Failed to analyze resume');
      }

      const data = await response.json();
      console.log(data)
      setResumeMatch(data.analysis); // Use the ML model's analysis directly
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
          <p className="mt-4 text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={() => router.back()} 
          className="mb-6 flex items-center text-blue-600 hover:text-blue-800"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Jobs
        </button>

        {job && (
          <div className="bg-white shadow-lg rounded-lg overflow-hidden">
            <div className="p-6 border-b">
              <h1 className="text-2xl font-bold text-gray-900">{job.job_title}</h1>
              <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600">
                <span className="mr-4 font-medium text-blue-600">{job.company_name}</span>
                <span className="mr-4">{job.job_location}</span>
                {job.job_schedule_type && <span className="mr-4">{job.job_schedule_type}</span>}
                {job.job_work_from_home === "Yes" && (
                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Remote</span>
                )}
              </div>
            </div>

            <div className="p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Skills Required</h2>
                <div className="flex flex-wrap gap-2">
                  {job.job_skills && job.job_skills.split(',').map((skill, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                      {skill.trim()}
                    </span>
                  ))}
                  {!job.job_skills && <p className="text-gray-500">No specific skills listed</p>}
                </div>
              </div>

              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Check Your Resume Match</h2>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload your resume (PDF)
                    </label>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      className="block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                    />
                  </div>
                  
                  <button
                    onClick={analyzeResume}
                    disabled={!resumeFile || analyzing}
                    className={`w-full py-2 px-4 rounded-md font-medium ${
                      !resumeFile || analyzing
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {analyzing ? 'Analyzing...' : 'Check Match'}
                  </button>
                  
                  {error && (
                    <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                      <span className="block sm:inline">{error}</span>
                    </div>
                  )}
                </div>
              </div>

              {resumeMatch && (
                <div className="mt-6 bg-white p-4 rounded-lg shadow">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Resume Match Analysis</h3>
                  
                  <div className="mb-4">
                    <div className="flex items-center">
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded-full">
                          <div 
                            className="h-4 bg-blue-600 rounded-full" 
                            style={{ width: `${resumeMatch.matchScore}%` }}
                          ></div>
                        </div>
                      </div>
                      <span className="ml-4 text-lg font-semibold text-blue-600">
                        {Math.round(resumeMatch.matchScore)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Your    Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {resumeMatch.matchingSkills.map((skill, index) => (
                          <span key={index} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Missing Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {resumeMatch.missingSkills.map((skill, index) => (
                          <span key={index} className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-center mt-6">
                <a
                  href={job.job_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Apply on LinkedIn
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}