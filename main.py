import joblib
import numpy as np
from processing.skill_extractor import extract_text_from_pdf, get_skills

# 📌 Load trained ML model
model = joblib.load("models/job_recommender.pkl")

# 📌 Extract skills from resume
resume_path = "data/DHairyash_s_Resume.pdf"
resume_text = extract_text_from_pdf(resume_path)

# Use the new get_skills function to get a comprehensive list of skills
extracted_skills = get_skills(resume_text)

# Convert skills to a string format for prediction
skills_text = ", ".join(extracted_skills)
print(f"📋 Extracted Skills: {skills_text}")

# 📌 Get probability scores for all job titles
# Get the classes (job titles) from the model
job_titles = model.classes_

# Predict probability scores for each job title
proba_scores = model.predict_proba([skills_text])[0]

# Get top 10 job matches first (to allow for filtering)
top_indices = np.argsort(proba_scores)[-10:][::-1]  # Get indices of top 10 scores
top_jobs = [job_titles[i] for i in top_indices]
top_scores = [proba_scores[i] for i in top_indices]

# Filter for diversity - try to include different job categories
filtered_jobs = []
filtered_scores = []
job_categories = set()

for job, score in zip(top_jobs, top_scores):
    # Extract job category (first word or two of job title)
    category = ' '.join(job.split()[:2])
    
    # If we haven't seen this category or we have fewer than 5 jobs, include it
    if category not in job_categories or len(filtered_jobs) < 5:
        filtered_jobs.append(job)
        filtered_scores.append(score)
        job_categories.add(category)
    
    # Stop once we have 5 diverse jobs
    if len(filtered_jobs) >= 5:
        break

# If we couldn't get 5 diverse jobs, add more from the top list
if len(filtered_jobs) < 5:
    remaining = [job for job in top_jobs if job not in filtered_jobs]
    remaining_scores = [score for job, score in zip(top_jobs, top_scores) if job not in filtered_jobs]
    
    # Add remaining jobs until we have 5
    filtered_jobs.extend(remaining[:5-len(filtered_jobs)])
    filtered_scores.extend(remaining_scores[:5-len(filtered_scores)])

# 📌 Display results
print("\n🔮 Top Job Recommendations Based on Your Skills:")
print("------------------------------------------------")
for i, (job, score) in enumerate(zip(filtered_jobs, filtered_scores), 1):
    confidence = score * 100
    print(f"{i}. {job} (Confidence: {confidence:.1f}%)")

# Also return the original single prediction for compatibility
predicted_job = model.predict([skills_text])[0]
print(f"\n🎯 Primary Job Match: {predicted_job}")
