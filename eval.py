import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

# Labeled eval set: { "Expected Category": "Expected Image Substring" }
EVAL_SET = [
    {"category": "red fox", "content": "An article about a red fox", "expected_image": "red_fox"},
    {"category": "gray wolf", "content": "An article about a gray wolf", "expected_image": "gray_wolf"},
    {"category": "brown bear", "content": "An article about a brown bear", "expected_image": "brown_bear"},
    {"category": "dog", "content": "An article about a dog in the park", "expected_image": "brown_dog"}
]

def run_eval():
    print("Running Top-1 Precision Evaluation...")
    correct_matches = 0
    total = len(EVAL_SET)
    
    with httpx.Client(base_url=BASE_URL) as client:
        # Give the server a moment if it just started
        try:
            client.get("/images")
        except:
            print("Error: Ensure the server is running on http://127.0.0.1:8000")
            sys.exit(1)
            
        for item in EVAL_SET:
            # 1. Create a post
            post_res = client.post("/posts", json={
                "content": item["content"],
                "expected_category": item["category"]
            })
            post_id = post_res.json()["id"]
            
            # 2. Get the top image suggestion
            match_res = client.get(f"/posts/{post_id}/images")
            data = match_res.json()
            
            # 3. Check if it matches expected
            if data.get("status") == "APPROVED" and item["expected_image"] in data["image"]["filename"]:
                correct_matches += 1
                print(f"✅ Pass: '{item['category']}' matched {data['image']['filename']}")
            else:
                print(f"❌ Fail: '{item['category']}' did not match correctly.")
                
    precision = (correct_matches / total) * 100
    print(f"\n--- EVALUATION RESULTS ---")
    print(f"Top-1 Precision: {precision:.0f}% ({correct_matches}/{total} correct)")
    return precision

if __name__ == "__main__":
    run_eval()
