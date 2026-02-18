import json

def analyze_balance():
    try:
        with open("account_balance.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print("=== Analysis of Account Balance (Fields > 0) ===\n")
        
        # Analyze output1 (Individual rows)
        print("--- Individual Item Groups (output1) ---")
        for i, item in enumerate(data.get("output1", [])):
            nonzero_fields = {k: v for k, v in item.items() if float(v or 0) > 0}
            if nonzero_fields:
                print(f"Index {i}:")
                for k, v in nonzero_fields.items():
                    print(f"  {k}: {v}")
                print()

        # Analyze output2 (Totals)
        print("--- Total Account Summary (output2) ---")
        output2 = data.get("output2", {})
        for k, v in output2.items():
            try:
                if float(v or 0) > 0:
                    print(f"  {k}: {v}")
            except ValueError:
                continue
                
    except Exception as e:
        print(f"Error analyzing balance: {e}")

if __name__ == "__main__":
    analyze_balance()
