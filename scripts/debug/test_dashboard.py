import requests
import json

def test_dashboard():
    try:
        url = "http://127.0.0.1:8000/api/dashboard/summary"
        print(f"Requesting {url}...")
        res = requests.get(url)
        
        if res.status_code == 200:
            data = res.json()
            print("\n[Dashboard Summary]")
            print(json.dumps(data["summary"], indent=2, ensure_ascii=False))
            
            print("\n[Overseas Holdings Sample]")
            for item in data["holdings"]["overseas"][:3]: # Show first 3
                print(item)
                
            print("\n[Domestic Holdings Sample]")
            for item in data["holdings"]["domestic"][:3]:
                print(item)
        else:
            print(f"Failed: {res.status_code} {res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard()
