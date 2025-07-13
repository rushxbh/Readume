import re
import pytesseract
from PIL import Image
import pdf2image
from transformers import pipeline

# 📌 Configure OCR (Tesseract)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 📌 Load Hugging Face NLP Model
generator = pipeline("text2text-generation", model="google/flan-t5-small")

def extract_text_from_image(image_path):
    """Extract text from image using Tesseract OCR"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using Tesseract OCR on each page"""
    images = pdf2image.convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    return text

def extract_skills(resume_text):
    """
    Extracts skills from resume text using the Hugging Face model.
    Handles long texts by chunking.
    
    Args:
        resume_text (str): The raw text extracted from a resume
        
    Returns:
        str: Raw output from the model containing skills
    """
    # Filter out non-relevant sections before passing to the model
    cleaned_text = re.sub(r'\b(?:education|experience|projects|work|summary|contact|phone|email|linkedin|github)\b', '', resume_text, flags=re.IGNORECASE)
    
    # Split text into chunks to handle token limit
    chunks = []
    max_chunk_length = 300  # Reduced to be safer with token limits
    words = cleaned_text.split()
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(word) + 1  # +1 for the space
        if current_length <= max_chunk_length:
            current_chunk.append(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    print(f"Split resume into {len(chunks)} chunks to process")
    
    # Process each chunk and combine results
    all_outputs = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        # Improved prompt with more specific instructions
        prompt = f"""
You are a resume parser that extracts technical skills.
From the resume text below, identify ONLY technical skills like programming languages, frameworks, tools, and technologies.
Format your response as: Technical Skills: skill1, skill2, skill3

Resume text: {chunk}
"""

        try:
            output = generator(
                prompt,
                max_length=256,
                num_beams=2,
                do_sample=False,
                temperature=0.3  # Lower temperature for more focused output
            )
            all_outputs.append(output[0]['generated_text'])
            print(f"Chunk {i+1} processed successfully")
        except Exception as e:
            print(f"Error in model inference for chunk {i+1}: {str(e)}")
    
    # Combine all outputs
    combined_output = "\n".join(all_outputs)
    
    # Return only the combined output (not the regex skills)
    return combined_output

def clean_skills(skills_text):
    """
    Clean the extracted skills text and extract only technical skills.
    Handles multiple skill sections from different chunks.
    """
    skills_dict = {"Technical Skills": []}
    
    if not skills_text or "comma-separated values" in skills_text.lower():
        print("⚠️ Warning: Model failed to extract actual skills.")
        return skills_dict
    
    # Match all Technical Skills sections with improved regex
    tech_matches = re.findall(r"(?:Technical Skills:?|Skills:?)\s*([\w\s,.\-+#/()]+)(?:\n|$)", skills_text, re.IGNORECASE)
    
    # If no matches with the specific format, try to extract any comma-separated list
    if not tech_matches:
        print("⚠️ No skills section found, trying to extract any skills list...")
        # Look for comma-separated lists that might be skills
        tech_matches = re.findall(r"([A-Za-z]+(?:,\s*[A-Za-z]+)+)", skills_text)
    
    all_skills = []
    for match in tech_matches:
        skills = [skill.strip() for skill in match.split(",")]
        all_skills.extend(skills)
    
    # Remove duplicates, empty strings, and very short strings (likely not skills)
    unique_skills = list(set([skill for skill in all_skills if skill and len(skill) > 2]))
    
    # Filter out common non-technical terms that might be misidentified as skills
    non_tech_terms = ['and', 'the', 'with', 'for', 'from', 'have', 'has', 'had', 'not', 'are', 'this', 'that', 
                      'these', 'those', 'they', 'them', 'their', 'there', 'here', 'where', 'when', 'what', 'who',
                      'how', 'why', 'which', 'such', 'some', 'many', 'much', 'more', 'most', 'other', 'another',
                      'resume', 'skill', 'skills', 'technical', 'include', 'includes', 'including']
    
    filtered_skills = [skill for skill in unique_skills if skill.lower() not in non_tech_terms]
    
    # Common technical skills to help with validation
    common_tech_skills = ['python', 'java', 'javascript', 'js', 'c++', 'c#', 'ruby', 'php', 'html', 'css', 
                         'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring', 'aws', 
                         'azure', 'gcp', 'docker', 'kubernetes', 'git', 'sql', 'nosql', 'mongodb', 'mysql', 
                         'postgresql', 'oracle', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn',
                         'machine learning', 'ai', 'artificial intelligence', 'data science', 'linux', 'unix',
                         'bash', 'powershell', 'rest', 'api', 'graphql', 'json', 'xml', 'yaml', 'agile', 'scrum']
    
    # Boost confidence in skills that match common technical skills
    final_skills = []
    for skill in filtered_skills:
        if any(common.lower() in skill.lower() or skill.lower() in common.lower() for common in common_tech_skills):
            final_skills.append(skill)  # It's likely a real technical skill
        elif len(skill) > 4 and not skill.isdigit():  # Longer terms that aren't just numbers
            final_skills.append(skill)
    
    skills_dict["Technical Skills"] = final_skills
    
    print(f"Found {len(final_skills)} unique technical skills after filtering")
    
    return skills_dict

def extract_skills_with_regex(resume_text):
    """
    Use regex patterns to extract common technical skills directly from resume text.
    This complements the model-based approach for better accuracy.
    """
    # Common programming languages
    programming_langs = r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Go|Rust|Scala|R|MATLAB|Perl|Shell|Bash|PowerShell|SQL|NoSQL|HTML|CSS|XML|JSON|YAML|BlockChain)\b'
    
    # Frameworks and libraries
    frameworks = r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|ASP\.NET|Laravel|Ruby on Rails|TensorFlow|PyTorch|Keras|Pandas|NumPy|Scikit-learn|Bootstrap|jQuery|D3\.js)\b'
    
    # Databases
    databases = r'\b(MySQL|PostgreSQL|MongoDB|SQLite|Oracle|SQL Server|Redis|Cassandra|DynamoDB|Firebase|Elasticsearch)\b'
    
    # Cloud platforms and DevOps
    cloud_devops = r'\b(AWS|Amazon Web Services|Azure|Google Cloud|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab|Bitbucket|CI/CD|Terraform|Ansible|Puppet|Chef)\b'
    
    # Data science and ML
    data_ml = r'\b(Machine Learning|Deep Learning|NLP|Natural Language Processing|Computer Vision|Data Mining|Data Analysis|Big Data|Hadoop|Spark|Data Visualization|Statistics|A/B Testing)\b'
    
    # Other technical skills
    other_tech = r'\b(RESTful API|GraphQL|Microservices|Serverless|Agile|Scrum|Kanban|UI/UX|Responsive Design|Mobile Development|Web Development|Testing|Debugging|Performance Optimization)\b'
    
    # Combine all patterns
    all_patterns = [programming_langs, frameworks, databases, cloud_devops, data_ml, other_tech]
    
    # Extract skills using regex
    regex_skills = []
    for pattern in all_patterns:
        matches = re.finditer(pattern, resume_text, re.IGNORECASE)
        for match in matches:
            skill = match.group(0)
            regex_skills.append(skill)
    
    # Remove duplicates and sort
    regex_skills = sorted(list(set(regex_skills)))
    
    return regex_skills

def get_skills(resume_text):
    """
    Complete skill extraction pipeline for use in main.py
    
    Args:
        resume_text (str): The raw text extracted from a resume
        
    Returns:
        list: List of extracted technical skills
    """
    # Extract skills using both approaches
    model_output = extract_skills(resume_text)
    model_skills = clean_skills(model_output)
    
    # Also get regex-based skills
    regex_skills = extract_skills_with_regex(resume_text)
    
    # Combine skills from both approaches
    all_skills = set(model_skills["Technical Skills"] + regex_skills)
    
    # Final filtering to remove any remaining non-technical terms
    non_tech_terms = ['and', 'the', 'with', 'for', 'from', 'have', 'has', 'had', 'not', 'are', 'this', 'that']
    final_skills = [skill for skill in all_skills if skill.lower() not in non_tech_terms]
    
    # Sort skills alphabetically for better presentation
    final_skills = sorted(final_skills)
    
    return final_skills

def process_resume(file_path):
    """
    Process a resume file and extract skills using both model-based and regex-based approaches
    
    Args:
        file_path (str): Path to the resume file (PDF or image)
        
    Returns:
        dict: Dictionary containing extracted skills
    """
    print(f"Processing resume: {file_path}")
    
    # Extract text from PDF or image
    if file_path.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
        print(f"Extracted {len(resume_text)} characters from PDF")
    else:
        resume_text = extract_text_from_image(file_path)
        print(f"Extracted {len(resume_text)} characters from image")
    
    # Use the get_skills function to extract skills
    final_skills = get_skills(resume_text)
    
    return {"Technical Skills": final_skills}

if __name__ == "__main__":
    # 📌 Test with Sample Resume
    resume_path = "resume.pdf"
    
    try:
        # Process the resume
        skills = process_resume(resume_path)
        
        # Print results in a formatted way
        print("\nExtracted Technical Skills:")
        print("---------------------------")
        if skills["Technical Skills"]:
            for skill in skills["Technical Skills"]:
                print(f"- {skill}")
        else:
            print("No technical skills were extracted.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your file path and ensure all dependencies are installed.")
