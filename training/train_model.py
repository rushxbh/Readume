import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import time

# Start timing
start_time = time.time()
print("Starting model training process...")

# Load dataset from local CSV file
try:
    df = pd.read_csv("../data/job_descriptions.csv")
    print(f"✅ Successfully loaded data_jobs.csv - {len(df)} rows")
    
    # Print column names to debug
    print("Available columns:", df.columns.tolist())
except FileNotFoundError:
    print("❌ Error: data_jobs.csv file not found in the data directory")
    print("Please ensure the file exists at: ../data/job_descriptions.csv")
    exit(1)
except Exception as e:
    print(f"❌ Error loading data_jobs.csv: {str(e)}")
    exit(1)

# Rename columns based on actual column names in the CSV
df = df.rename(columns={
    "Job Title": "JobTitle", 
    "skills": "JobSkills",
    "Company": "Company",
    "job_location": "Location"
})

# Print renamed columns to verify
print("Columns after renaming:", df.columns.tolist())

# Check if JobSkills column exists after renaming
if "JobSkills" not in df.columns:
    # If JobSkills still doesn't exist, try to identify the skills column
    potential_skill_columns = [col for col in df.columns if 'skill' in col.lower()]
    if potential_skill_columns:
        print(f"Found potential skills column: {potential_skill_columns[0]}")
        df = df.rename(columns={potential_skill_columns[0]: "JobSkills"})
    else:
        print("❌ Error: Could not find a skills column in the dataset")
        print("Available columns:", df.columns.tolist())
        exit(1)

# 🛠️ Fix: Convert lists to strings, handle missing values
df["JobSkills"] = df["JobSkills"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))

# Make sure JobTitle is also cleaned and has no NaN values
df["JobTitle"] = df["JobTitle"].fillna("Unknown").astype(str)

# ✅ Remove empty JobSkills rows and rows with empty JobTitle
df = df[df["JobSkills"].str.strip() != ""]
df = df[df["JobTitle"].str.strip() != ""]
df = df.dropna(subset=["JobSkills", "JobTitle"])

# Check if we have enough data after cleaning
if len(df) == 0:
    print("❌ Error: No valid data remains after cleaning")
    exit(1)

print(f"✅ Dataset prepared with {len(df)} valid entries")

# Reduce dataset size to prevent memory issues
sample_size = min(1200000, len(df))
df = df.sample(n=sample_size, random_state=42)
print(f"⚡ Using {sample_size} samples for training")

# Train/Test Split
train_df = df.sample(frac=0.8, random_state=42)
test_df = df.drop(train_df.index)

# Print some statistics to verify data quality
print(f"Number of unique job titles: {train_df['JobTitle'].nunique()}")
print(f"Number of unique skill combinations: {train_df['JobSkills'].nunique()}")

# ML Pipeline: TF-IDF + Logistic Regression
model_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        min_df=2,           
        max_df=0.6,         
        max_features=4000,  
        ngram_range=(1, 3)  
    )),
    ("classifier", LogisticRegression(
        max_iter=500,       
        solver='saga',      
        C=0.8,              
        n_jobs=-1,          
        multi_class='ovr'
    ))
])

# 🚀 Train the Model
print("Training model...")
training_start = time.time()
model_pipeline.fit(train_df["JobSkills"], train_df["JobTitle"])
training_end = time.time()
print(f"✅ Model training completed in {training_end - training_start:.2f} seconds")

# Evaluate Model Performance
print("\n🔍 Evaluating model performance...")
evaluation_start = time.time()

# Make predictions on test set
y_pred = model_pipeline.predict(test_df["JobSkills"])
y_true = test_df["JobTitle"]

# Calculate accuracy
accuracy = accuracy_score(y_true, y_pred)
print(f"✅ Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Generate a more detailed classification report
print("\n📊 Detailed Classification Report:")
report = classification_report(y_true, y_pred, output_dict=False)
print(report)

# Find the top 5 most frequent job titles in the test set
top_jobs = test_df["JobTitle"].value_counts().head(5).index.tolist()
print("\n🔝 Performance on Top 5 Most Common Job Titles:")
for job in top_jobs:
    job_indices = test_df[test_df["JobTitle"] == job].index
    job_accuracy = accuracy_score(
        y_true.iloc[test_df.index.get_indexer(job_indices)], 
        y_pred[test_df.index.get_indexer(job_indices)]
    )
    count = len(job_indices)
    print(f"  - {job}: {job_accuracy:.4f} ({count} samples)")

evaluation_end = time.time()
print(f"✅ Evaluation completed in {evaluation_end - evaluation_start:.2f} seconds")

# Save the Model
joblib.dump(model_pipeline, "../models/job_recommender.pkl")

# Total time
end_time = time.time()
print(f"✅ Model trained, evaluated, and saved successfully! Total time: {end_time - start_time:.2f} seconds")