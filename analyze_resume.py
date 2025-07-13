import sys
import os
import json
import re
import numpy as np
import joblib
import logging
from datetime import datetime
from collections import Counter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.skill_extractor import extract_text_from_pdf, get_skills
# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=os.path.join(logs_dir, "resume_analysis.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def analyze_resume(resume_path):
    """
    Analyze a resume and return extracted skills and job recommendations
    """
    start_time = datetime.now()
    logging.info(f"Starting analysis for resume: {resume_path}")
    
    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume_path)
        
        # Extract skills
        extracted_skills = get_skills(resume_text)
        logging.info(f"Extracted {len(extracted_skills)} skills")
        
        # Categorize skills
        skill_categories = categorize_skills(extracted_skills)
        
        # Calculate resume score
        resume_score = calculate_resume_score(extracted_skills, resume_text)
        
        # Load the trained model
        try:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "job_recommender.pkl")
            model = joblib.load(model_path)
        except Exception as model_error:
            logging.error(f"Error loading model: {str(model_error)}")
            return {
                'skills': extracted_skills,
                'skill_categories': skill_categories,
                'resume_score': resume_score,
                'job_recommendations': [],
                'error': f"Model loading error: {str(model_error)}"
            }
        
        # Convert skills to string format for prediction
        skills_text = ", ".join(extracted_skills)
        
        # Get job titles and probability scores
        job_titles = model.classes_
        proba_scores = model.predict_proba([skills_text])[0]
        
        # Get top 15 job matches first (to allow for better filtering)
        top_indices = np.argsort(proba_scores)[-15:][::-1]
        top_jobs = [job_titles[i] for i in top_indices]
        top_scores = [proba_scores[i] for i in top_indices]
        
        # Enhanced diversity filtering
        filtered_jobs, filtered_scores = get_diverse_job_recommendations(top_jobs, top_scores)
        
        # Format results
        job_recommendations = []
        for job, score in zip(filtered_jobs, filtered_scores):
            confidence = score * 100
            job_recommendations.append({
                'title': job,
                'confidence': f"{confidence:.1f}%",
                'match_score': int(confidence),
                'skills_matched': get_matching_skills_for_job(job, extracted_skills)
            })
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        logging.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        return {
            'skills': extracted_skills,
            'skill_categories': skill_categories,
            'resume_score': resume_score,
            'job_recommendations': job_recommendations,
            'processing_time': f"{processing_time:.2f} seconds"
        }
        
    except Exception as e:
        logging.error(f"Error analyzing resume: {str(e)}")
        return {
            'skills': [],
            'skill_categories': {},
            'resume_score': 0,
            'job_recommendations': [],
            'error': str(e)
        }

def categorize_skills(skills):
    """Categorize skills into technical, soft, and domain-specific categories"""
    # This is a simplified implementation - in a real system, you'd have a more comprehensive categorization
    technical_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'mongodb', 'aws', 'docker', 
                        'kubernetes', 'machine learning', 'data science', 'tensorflow', 'pytorch']
    soft_skills = ['communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking', 
                  'time management', 'creativity', 'adaptability', 'collaboration']
    
    categories = {
        'technical': [skill for skill in skills if any(tech.lower() in skill.lower() for tech in technical_skills)],
        'soft': [skill for skill in skills if any(soft.lower() in skill.lower() for soft in soft_skills)],
        'domain': [skill for skill in skills if skill not in 
                  [s for s in skills if any(tech.lower() in s.lower() for tech in technical_skills)] and
                  skill not in [s for s in skills if any(soft.lower() in s.lower() for soft in soft_skills)]]
    }
    
    return categories

def calculate_resume_score(skills, resume_text):
    """Calculate a score for the resume based on skills and content"""
    # This is a simplified scoring system - in a real system, you'd have a more sophisticated algorithm
    base_score = min(len(skills) * 5, 50)  # Up to 50 points for skills
    
    # Check for education keywords
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
    education_score = min(sum(1 for keyword in education_keywords if keyword.lower() in resume_text.lower()) * 5, 15)
    
    # Check for experience indicators
    experience_indicators = ['experience', 'year', 'work', 'job', 'position', 'role']
    experience_score = min(sum(1 for indicator in experience_indicators if indicator.lower() in resume_text.lower()) * 5, 20)
    
    # Check for project indicators
    project_indicators = ['project', 'developed', 'built', 'created', 'implemented']
    project_score = min(sum(1 for indicator in project_indicators if indicator.lower() in resume_text.lower()) * 3, 15)
    
    total_score = base_score + education_score + experience_score + project_score
    return min(total_score, 100)  # Cap at 100

def get_diverse_job_recommendations(jobs, scores, max_jobs=5):
    """Get a diverse set of job recommendations"""
    filtered_jobs = []
    filtered_scores = []
    job_categories = set()
    job_industries = set()
    
    # First pass: try to get jobs from different categories and industries
    for job, score in zip(jobs, scores):
        # Extract job category and industry (simplified approach)
        category = ' '.join(job.split()[:2])
        industry = job.split()[-1] if len(job.split()) > 2 else ''
        
        # If we haven't seen this category or industry, include it
        if (category not in job_categories or industry not in job_industries) and len(filtered_jobs) < max_jobs:
            filtered_jobs.append(job)
            filtered_scores.append(score)
            job_categories.add(category)
            if industry:
                job_industries.add(industry)
        
        if len(filtered_jobs) >= max_jobs:
            break
    
    # Second pass: if we don't have enough jobs, add more based on score
    if len(filtered_jobs) < max_jobs:
        remaining_jobs = [job for job in jobs if job not in filtered_jobs]
        remaining_scores = [score for job, score in zip(jobs, scores) if job not in filtered_jobs]
        
        # Sort remaining jobs by score
        sorted_remaining = sorted(zip(remaining_jobs, remaining_scores), key=lambda x: x[1], reverse=True)
        
        # Add remaining jobs until we have max_jobs
        for job, score in sorted_remaining:
            if len(filtered_jobs) >= max_jobs:
                break
            filtered_jobs.append(job)
            filtered_scores.append(score)
    
    return filtered_jobs, filtered_scores

def get_matching_skills_for_job(job_title, skills):
    """Get skills that match with a specific job title"""
    # This is a simplified implementation - in a real system, you'd have a job-skill mapping database
    job_title_lower = job_title.lower()
    
    # Define some common job-skill mappings
    job_skill_mappings = {
        'data scientist': ['python', 'r', 'statistics', 'machine learning', 'data analysis', 'sql'],
        'software engineer': ['java', 'python', 'javascript', 'algorithms', 'data structures'],
        'web developer': ['html', 'css', 'javascript', 'react', 'node', 'angular'],
        'product manager': ['product development', 'agile', 'scrum', 'user research', 'roadmap'],
        'designer': ['ui', 'ux', 'figma', 'sketch', 'adobe', 'design thinking']
    }
    
    # Find the closest job title in our mappings
    matching_job = None
    for known_job in job_skill_mappings.keys():
        if known_job in job_title_lower or job_title_lower in known_job:
            matching_job = known_job
            break
    
    if matching_job:
        relevant_skills = job_skill_mappings[matching_job]
        return [skill for skill in skills if any(relevant.lower() in skill.lower() for relevant in relevant_skills)]
    
    # Fallback: return skills that appear in the job title
    return [skill for skill in skills if skill.lower() in job_title_lower or any(word.lower() in skill.lower() for word in job_title_lower.split())]

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            error_result = {'error': 'No resume path provided', 'skills': [], 'job_recommendations': []}
            print(json.dumps(error_result))
            sys.exit(1)
        
        resume_path = sys.argv[1]
        try:
            logging.info(f"Received request to analyze resume: {resume_path}")
        except Exception as log_error:
            # If logging fails, continue without it
            pass
        
        results = analyze_resume(resume_path)
        
        # Ensure we have a valid JSON structure even if something goes wrong
        if not isinstance(results, dict):
            results = {'error': 'Invalid result format', 'skills': [], 'job_recommendations': []}
        
        print(json.dumps(results, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        # Catch any JSON serialization errors
        error_result = {
            'error': f"Script execution error: {str(e)}",
            'skills': [],
            'job_recommendations': []
        }
        print(json.dumps(error_result))
        sys.exit(1)