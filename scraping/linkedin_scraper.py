import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def get_unique_skills_from_dataset():
    """Extract unique skills from job descriptions dataset"""
    try:
        # Path to the job descriptions CSV file
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "data", "job_descriptions.csv")
        
        if not os.path.exists(csv_path):
            print(f"Warning: Job descriptions file not found at {csv_path}")
            return []
            
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Check if the dataset has a skills column
        skills_column = None
        possible_columns = ['Skills', 'skills', 'Required Skills', 'required_skills', 'job_skills']
        
        for col in possible_columns:
            if col in df.columns:
                skills_column = col
                break
        
        if not skills_column:
            print("No skills column found in the dataset")
            return []
            
        # Extract all skills and create a unique list
        all_skills = []
        for skills_text in df[skills_column].dropna():
            if isinstance(skills_text, str):
                # Split by common delimiters
                skills = [s.strip() for s in skills_text.replace(';', ',').split(',')]
                all_skills.extend([s for s in skills if s])
        
        # Get unique skills and sort
        unique_skills = sorted(list(set(all_skills)))
        print(f"Extracted {len(unique_skills)} unique skills from dataset")
        return unique_skills
        
    except Exception as e:
        print(f"Error extracting skills from dataset: {str(e)}")
        return []

def scrape_linkedin_jobs(job_titles, location="India"):
    """Scrapes LinkedIn job listings for the predicted job titles."""
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    if not os.path.exists(data_dir):
        print(f"Creating data directory at: {data_dir}")
        os.makedirs(data_dir)
    
    # Get unique skills from dataset
    dataset_skills = get_unique_skills_from_dataset()
    
    # Fallback to common skills if dataset skills are not available
    if not dataset_skills:
        dataset_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "SQL", "NoSQL",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", 
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", 
            "Machine Learning", "Deep Learning", "AI", "Data Science", "Data Analysis",
            "HTML", "CSS", "REST API", "GraphQL", "Agile", "Scrum"
        ]
    
    # 📌 Setup Selenium WebDriver with improved options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    
    # Add user agent to avoid detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    job_listings = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized successfully")
        
        for job_title in job_titles:
            print(f"Searching for: {job_title} in {location}")
            # Updated search URL to include location parameter for India
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            
            try:
                driver.get(search_url)
                print(f"Navigated to: {search_url}")
                
                # Wait for job listings to load with increased timeout
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "base-card"))
                    )
                    print("Job listings loaded successfully")
                except TimeoutException:
                    print(f"Timeout waiting for job listings for {job_title}. Moving to next job title.")
                    continue
                
                # Extract job listings
                soup = BeautifulSoup(driver.page_source, "html.parser")
                jobs = soup.find_all("div", class_="base-card")
                
                print(f"Found {len(jobs)} job listings for {job_title} in {location}")
                
                for job in jobs[:5]:  # Limit to first 5 jobs per job title
                    try:
                        title_elem = job.find("h3", class_="base-search-card__title")
                        company_elem = job.find("h4", class_="base-search-card__subtitle")
                        location_elem = job.find("span", class_="job-search-card__location")
                        
                        # Extract job link
                        job_link = None
                        link_elem = job.find("a", class_="base-card__full-link")
                        if link_elem and 'href' in link_elem.attrs:
                            job_link = link_elem['href']
                        
                        if title_elem and company_elem and location_elem:
                            title = title_elem.text.strip()
                            company = company_elem.text.strip()
                            location = location_elem.text.strip()
                            
                            # Extract skills by visiting the job detail page if we have a link
                            job_skills = "Not available"
                            if job_link:
                                try:
                                    # Visit the job detail page
                                    driver.get(job_link)
                                    # Wait for job details to load
                                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "show-more-less-html__markup")))
                                    
                                    # Get job description
                                    job_detail_soup = BeautifulSoup(driver.page_source, "html.parser")
                                    job_description_elem = job_detail_soup.find("div", class_="show-more-less-html__markup")
                                    
                                    if job_description_elem:
                                        job_description = job_description_elem.text.strip()
                                        
                                        # Extract skills from job description using dataset skills
                                        found_skills = []
                                        for skill in dataset_skills:
                                            if skill.lower() in job_description.lower():
                                                found_skills.append(skill)
                                        
                                        if found_skills:
                                            job_skills = ", ".join(found_skills)
                                        
                                    # Go back to search results
                                    driver.back()
                                    # Wait for search results to reload
                                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "base-card")))
                                except Exception as e:
                                    print(f"Error extracting job details: {str(e)}")
                                    # Try to go back to search results
                                    driver.get(search_url)
                                    time.sleep(2)
                            
                            job_listings.append({
                                "job_title_short": title.split(" ")[0],
                                "job_title": title,
                                "job_location": location,
                                "job_via": "LinkedIn",
                                "job_schedule_type": "Full-Time",  # Placeholder
                                "job_work_from_home": "No",  # Placeholder
                                "search_location": location,
                                "job_posted_date": "Recently Posted",  # Placeholder
                                "job_no_degree_mention": "Unknown",  # Placeholder
                                "job_health_insurance": "Unknown",  # Placeholder
                                "job_country": "India",
                                "salary_rate": "Not Provided",
                                "salary_year_avg": "Not Provided",
                                "salary_hour_avg": "Not Provided",
                                "company_name": company,
                                "job_skills": job_skills,  # Now using extracted skills from dataset
                                "job_type_skills": "Software, Data Science",  # Placeholder
                                "job_link": job_link or "Not available"  # Adding job link
                            })
                            print(f"Added job: {title} at {company} in {location}")
                    except Exception as e:
                        print(f"Error processing job listing: {str(e)}")
            
            except Exception as e:
                print(f"Error searching for {job_title}: {str(e)}")
        
        # Save job listings to CSV
        if job_listings:
            output_path = os.path.join(data_dir, "linkedin_jobs_india.csv")
            df = pd.DataFrame(job_listings)
            df.to_csv(output_path, index=False)
            print(f"✅ Saved {len(job_listings)} job listings to {output_path}")
        else:
            print("❌ No job listings found")
        
    except Exception as e:
        print(f"Error in scraping process: {str(e)}")
    
    finally:
        # Close the browser
        try:
            driver.quit()
            print("Browser closed successfully")
        except:
            print("Error closing browser")
    
    return job_listings

if __name__ == "__main__":
    # You can specify more job titles here
    scrape_linkedin_jobs(["Blockchain Developer", "Software Developer", "AI Engineer"])
