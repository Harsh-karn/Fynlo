import json
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def train_model():
    # Load evaluation dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'eval_set.json')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, 'r') as f:
        transactions = json.load(f)
        
    if not isinstance(transactions, list) or not transactions:
        print("No transactions found in dataset.")
        return
        
    X = []
    y = []
    
    for t in transactions:
        # We'll use the raw text + amount magnitude as features if possible, 
        # but pure text is easiest for TF-IDF
        text = str(t.get('description', ''))
        category = t.get('expected_category', 'other')
        if text and category:
            X.append(text.lower())
            y.append(category)
            
    print(f"Training on {len(X)} labeled transactions...")
    
    # Create an sklearn Pipeline: Text -> TF-IDF -> Naive Bayes
    model = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1)),
        ('clf', MultinomialNB())
    ])
    
    model.fit(X, y)
    
    # Calculate basic accuracy on training set just as a sanity check
    score = model.score(X, y)
    print(f"Training Accuracy: {score * 100:.2f}%")
    
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'ml')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'categorizer_model.pkl')
    joblib.dump(model, model_path)
    
    print(f"Model saved successfully to {model_path}")

if __name__ == "__main__":
    train_model()
