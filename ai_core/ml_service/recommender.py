# D:\cognito_ai_assistant\ai_core\ml_service\recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from pathlib import Path

# Define the base path for relative file finding
BASE_DIR = Path(__file__).resolve().parent

def train_and_recommend(task_description: str, top_n: int = 5):
    """
    Simple Content-Based Recommender.
    Uses TF-IDF on task descriptions to find similar tasks.
    """
    try:
        # 1. Data Ingestion (Local ETL - will be replaced by AWS Lambda/RDS)
        data_path = BASE_DIR / 'tasks.csv'
        tasks_df = pd.read_csv(data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

    # Combine title and description for better features
    tasks_df['features'] = tasks_df['title'] + " " + tasks_df['description']

    # 2. Model Training (Vectorization)
    # TF-IDF: Transforms text into a matrix of token counts
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(tasks_df['features'])

    # 3. Model Prediction (Similarity Calculation)
    # Linear Kernel: Computes the cosine similarity between all tasks
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # --- Recommendation Logic for the INPUT task ---

    # Vectorize the input task description
    input_vector = tfidf.transform([task_description])

    # Calculate similarity between the input and all existing tasks
    input_sim_scores = linear_kernel(input_vector, tfidf_matrix).flatten()

    # Get the indices of the most similar tasks
    # np.argsort returns the indices that would sort an array
    sim_indices = input_sim_scores.argsort()[:-top_n-1:-1]

    # Get the titles of the top recommendations
    recommendations = tasks_df.iloc[sim_indices][['title', 'description', 'category']].to_dict('records')

    # Filter out the initial task itself if it was in the dataset (not applicable here, but good practice)
    return recommendations

# Simple test run (you can run this directly in PowerShell after training is complete)
if __name__ == '__main__':
    test_query = "I need to practice setting up CI/CD pipelines and deploying containers."
    recs = train_and_recommend(test_query)
    print(f"Recommendations for '{test_query}':")
    for rec in recs:
        print(f"- {rec['title']} ({rec['category']}): {rec['description']}")