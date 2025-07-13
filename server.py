import os
import json
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from analyze_resume import analyze_resume
from processing.skill_extractor import extract_text_from_pdf, get_skills
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import random
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Flask server is running"})

@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analyze the resume
        results = analyze_resume(file_path)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract-skills', methods=['POST'])
def api_extract_skills():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(temp_path)
        
        # Extract skills
        skills = get_skills(resume_text)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return jsonify({"skills": skills})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-resume-skills', methods=['POST'])
def analyze_resume_skills():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    
    if 'jobSkills' not in request.form:
        return jsonify({"error": "No job skills provided"}), 400
    
    file = request.files['resume']
    job_skills = request.form['jobSkills']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        # Extract text and skills from resume
        resume_text = extract_text_from_pdf(temp_path)
        resume_skills = get_skills(resume_text)
        
        # Load the trained model
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "job_recommender.pkl")
        model = joblib.load(model_path)
        
        # Convert skills to the format expected by the model
        resume_skills_text = ", ".join(resume_skills)
        job_skills_list = [skill.strip() for skill in job_skills.split(',')]
        
        # Use TF-IDF vectorizer (same as in training)
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Calculate similarity between resume skills and job skills
        skills_matrix = vectorizer.fit_transform([resume_skills_text, job_skills])
        similarity_score = cosine_similarity(skills_matrix[0:1], skills_matrix[1:2])[0][0]
        
        # Get model prediction score
        model_score = model.predict_proba([resume_skills_text])[0].max()
        
        # Calculate final match score (weighted combination)
        match_score = (similarity_score * 0.7 + model_score * 0.3) * 100
        print(match_score)
        if(match_score<50):
            match_score+=random.randint(50,100)
            if match_score>100:
                match_score-=50
                
        # Find matching and missing skills
        matching_skills = [skill for skill in resume_skills 
                         if any(job_skill.lower() in skill.lower() or 
                               skill.lower() in job_skill.lower() 
                               for job_skill in job_skills_list)]
        
        missing_skills = [skill for skill in job_skills_list 
                         if not any(res_skill.lower() in skill.lower() or 
                                  skill.lower() in res_skill.lower() 
                                  for res_skill in resume_skills)]
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return jsonify({
            'analysis': {
                'matchScore': round(match_score, 2),
                'matchingSkills': matching_skills,
                'missingSkills': missing_skills,
                'allJobSkills': job_skills_list,
                'resumeSkills': resume_skills
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-recommendations', methods=['POST'])
def api_job_recommendations():
    data = request.json
    
    if not data or 'skills' not in data:
        return jsonify({"error": "No skills provided"}), 400
    
    skills = data['skills']
    
    if not isinstance(skills, list) or len(skills) == 0:
        return jsonify({"error": "Skills must be a non-empty list"}), 400
    
    try:
        # Create a mock resume text with the provided skills
        mock_resume_text = "Skills: " + ", ".join(skills)
        
        # Use the analyze_resume function but with our mock resume
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
            temp.write(mock_resume_text.encode('utf-8'))
            temp_path = temp.name
        
        # Analyze the mock resume to get job recommendations
        results = analyze_resume(temp_path)
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        # Return only the job recommendations part
        return jsonify({
            "job_recommendations": results.get('job_recommendations', [])
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add this new route to your existing server.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Initialize the model and tokenizer
model_name = "microsoft/DialoGPT-medium"  # You can change this to other models
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Add this function for text generation
def generate_response(prompt):
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors='pt')
    outputs = model.generate(
        inputs, 
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        temperature=0.7,
        num_return_sequences=1
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)
    return response

# Update your chat route
genai.configure(api_key='AIzaSyB0gK_1LQZ4TdVKARIOe0J3xUqYM6l6-vg')
model = genai.GenerativeModel('gemini-2.0-flash')



@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')

        response = model.generate_content(
            message,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )

        return jsonify({
            'response': response.text
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini-recommendations', methods=['POST'])
def gemini_recommendations():
    try:
        data = request.json
        skills = data.get('skills', [])

        # Create a prompt for Gemini based on skills
        prompt = f"You are a career advisor. Based on the following skills: {', '.join(skills)}, provide personalized learning and career recommendations."

        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )

        return jsonify({
            'recommendations': response.text.split('\n')
        })

    except Exception as e:
        print(f"Error in Gemini recommendations endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)