import re
import pytesseract
from PIL import Image
import pdf2image
from transformers import pipeline

# Update the path below to the location of tesseract.exe on your system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    images = pdf2image.convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    return text

# Initialize Hugging Face's text2text-generation pipeline using a Flan-T5 model.
generator = pipeline("text2text-generation", model="google/flan-t5-small")

def extract_skills_hf(resume_text):
    """
    Extracts skills from resume text using the Hugging Face model.
    
    Args:
        resume_text (str): The raw resume text
    
    Returns:
        str: Extracted skills output
    """
    # Filter out non-relevant sections before passing to the model
    cleaned_text = re.sub(r'\b(?:education|experience|projects|work|summary|contact|phone|email|linkedin|github)\b', '', resume_text, flags=re.IGNORECASE)
    print("Cleaned Text:", cleaned_text)
    
    # Improved prompt to focus only on technical skills
    prompt = f"""
Extract a list of **technical skills** from the following resume text.

Provide output in this format:
Technical Skills: skill1, skill2, skill3, ...

Do NOT include anything else in the output.

Resume text:
{cleaned_text}
"""

    try:
        output = generator(
            prompt,
            max_length=1024,
            num_beams=5,
            do_sample=False  # Ensures a more deterministic output
        )
        return output[0]['generated_text']
    except Exception as e:
        print(f"Error in model inference: {str(e)}")
        return ""

def clean_skills(skills_text):
    """
    Clean the extracted skills text and extract only technical skills.
    """
    print("Skills Output:", skills_text)
    skills_dict = {"Technical Skills": []}
    
    if "comma-separated values" in skills_text.lower():
        print("Warning: Model failed to extract actual skills.")
        return skills_dict  # Return empty list if model output is faulty

    # Match only the Technical Skills
    tech_match = re.search(r"Technical Skills:\s*(.*)", skills_text, re.IGNORECASE)

    if tech_match:
        skills_dict["Technical Skills"] = [skill.strip() for skill in tech_match.group(1).split(",")]

    return skills_dict

def main():
    try:
        # Update the file path to your resume (PDF or image)
        file_path = "./DHairyash_s_Resume.pdf"
        
        # Extract text from PDF or image
        if file_path.lower().endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
        else:
            resume_text = extract_text_from_image(file_path)
        
        print("Resume Text:", resume_text)
        
        # Extract and clean technical skills
        skills_output = extract_skills_hf(resume_text)
        skills = clean_skills(skills_output)
        
        # Print results in a formatted way
        print("\nExtracted Technical Skills:")
        print("---------------------------")
        for skill in skills["Technical Skills"]:
            print(f"- {skill}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your file path and ensure all dependencies are installed.")


if __name__ == "__main__":
    main()