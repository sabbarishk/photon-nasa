import requests
import json

# Test the execute endpoint
url = "http://localhost:8000/execute/notebook"

# Simple test code
test_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create sample data
data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}
df = pd.DataFrame(data)

# Create a simple plot
plt.figure(figsize=(8, 6))
plt.plot(df['x'], df['y'], marker='o')
plt.title('Test Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

print("Data summary:")
print(df.describe())
"""

payload = {
    "code": test_code,
    "timeout": 30
}

try:
    print("Sending request to execute endpoint...")
    response = requests.post(url, json=payload, timeout=35)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Execution successful!")
        print(f"\nStdout:\n{result.get('stdout', 'No output')}")
        print(f"\nStderr:\n{result.get('stderr', 'No errors')}")
        print(f"\nExit Code: {result.get('exit_code', 'N/A')}")
        print(f"\nNumber of images: {len(result.get('images', []))}")
        
        if result.get('images'):
            for i, img in enumerate(result['images']):
                print(f"  - {img['filename']}")
    else:
        print(f"\n❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Is it running on port 8000?")
except Exception as e:
    print(f"❌ Error: {str(e)}")
