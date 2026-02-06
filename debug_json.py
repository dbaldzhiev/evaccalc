import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, "regulations.json")

print(f"Checking {json_path}")
if not os.path.exists(json_path):
    print("File does not exist!")
else:
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("JSON Loaded Successfully")
            print(f"Keys: {list(data.keys())}")
            if "table_11_flow_params" in data:
                t11 = data["table_11_flow_params"]
                print(f"Table 11 Keys: {list(t11.keys())}")
                if "data" in t11:
                    print(f"Table 11 Data Length: {len(t11['data'])}")
                else:
                    print("Table 11 has no 'data' key")
            else:
                print("No 'table_11_flow_params' key")
    except Exception as e:
        print(f"JSON Load Error: {e}")
