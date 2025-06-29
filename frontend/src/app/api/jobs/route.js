import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET() {
  try {
    // Try multiple possible locations for the CSV file
    const possiblePaths = [
      // Try in frontend root
      path.join(process.cwd(), 'linkedin_jobs_india.csv'),
      // Try in data directory (create if needed)
      path.join(process.cwd(), 'data', 'linkedin_jobs_india.csv'),
      // Try in public directory
      path.join(process.cwd(), 'public', 'linkedin_jobs_india.csv')
    ];
    
    let csvPath = "../data/linkedin_jobs_india.csv";
    let fileContent = null;
    
    // Find the first path that exists
    for (const testPath of possiblePaths) {
      
      try {
        if (fs.existsSync(testPath)) {
          csvPath = testPath;
          fileContent = fs.readFileSync(csvPath, 'utf8');
          console.log(`Found CSV file at: ${csvPath}`);
          break;
        }
      } catch (err) {
        console.log(`File not found at: ${testPath}`);
      }
    }
    
    // If no file found, return mock data
    if (!fileContent) {
      console.log('No CSV file found, returning mock data');
      return NextResponse.json({ jobs: [] });
    }
    
    // Parse the CSV content
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    return NextResponse.json({ jobs: records });
  } catch (error) {
    console.error('Error fetching jobs:', error);
    // Return mock data in case of any error
    return NextResponse.json({ jobs: getMockJobData() });
  }
}

// Function to generate mock job data
// function getMockJobData() {
//   return [
//     {
//       job_title: "Software Engineer",
//       company_name: "Tech Solutions Inc.",
//       job_location: "Bangalore, India",
//       job_schedule_type: "Full-time",
//       job_work_from_home: "Yes",
//       job_posted_date: "2023-05-15",
//       job_type_skills: "Software",
//       job_skills: "JavaScript, React, Node.js, MongoDB"
//     },
//     {
//       job_title: "Data Scientist",
//       company_name: "Data Analytics Ltd.",
//       job_location: "Mumbai, India",
//       job_schedule_type: "Full-time",
//       job_work_from_home: "No",
//       job_posted_date: "2023-05-10",
//       job_type_skills: "Data Science",
//       job_skills: "Python, SQL, Machine Learning, Statistics"
//     },
//     {
//       job_title: "UX/UI Designer",
//       company_name: "Creative Designs",
//       job_location: "Delhi, India",
//       job_schedule_type: "Contract",
//       job_work_from_home: "Yes",
//       job_posted_date: "2023-05-12",
//       job_type_skills: "Design",
//       job_skills: "Figma, Adobe XD, User Research, Prototyping"
//     },
//     {
//       job_title: "Product Manager",
//       company_name: "Product Innovations",
//       job_location: "Hyderabad, India",
//       job_schedule_type: "Full-time",
//       job_work_from_home: "No",
//       job_posted_date: "2023-05-08",
//       job_type_skills: "Management",
//       job_skills: "Product Development, Agile, Scrum, Roadmapping"
//     },
//     {
//       job_title: "Marketing Specialist",
//       company_name: "Marketing Solutions",
//       job_location: "Chennai, India",
//       job_schedule_type: "Full-time",
//       job_work_from_home: "Yes",
//       job_posted_date: "2023-05-14",
//       job_type_skills: "Marketing",
//       job_skills: "Digital Marketing, SEO, Content Creation, Analytics"
//     }
//   ];
// }