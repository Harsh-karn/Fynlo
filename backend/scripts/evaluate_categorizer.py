import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_categorizer import AICategorizerService

def evaluate():
    eval_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'eval_set.json')
    
    with open(eval_file, 'r') as f:
        dataset = json.load(f)
        
    correct = 0
    total = len(dataset)
    results = []
    
    for item in dataset:
        description = item['description']
        expected = item['expected_category']
        
        # Test rule-based categorizer
        actual = AICategorizerService.keyword_categorize(description)
        
        is_correct = (actual == expected)
        if is_correct:
            correct += 1
            
        results.append({
            "description": description,
            "expected": expected,
            "actual": actual,
            "correct": is_correct
        })
        
    accuracy = (correct / total) * 100
    
    print("=== AI Categorizer Evaluation ===")
    print(f"Total Transactions Tested: {total}")
    print(f"Correctly Categorized: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("\n--- Failures ---")
    
    for r in results:
        if not r["correct"]:
            print(f"DESC: {r['description']:<30} | EXPECTED: {r['expected']:<15} | ACTUAL: {r['actual']}")
            
    # Save results over time (append to a log)
    log_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'eval_accuracy_log.txt')
    from datetime import datetime, timezone
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] Total: {total}, Correct: {correct}, Accuracy: {accuracy:.2f}%\n")
        
if __name__ == "__main__":
    evaluate()
