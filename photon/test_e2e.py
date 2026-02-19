"""End-to-end test: search + workflow generate + execute"""
import requests
import json
import time

BASE = "http://localhost:8001"

def test_health():
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print(f"✅ Health check OK")

def test_search():
    queries = [
        "sea surface temperature",
        "MODIS vegetation index",
        "Arctic ice thickness",
        "precipitation climate",
        "CO2 atmosphere carbon"
    ]
    for q in queries:
        start = time.time()
        r = requests.post(f"{BASE}/query/", json={"query": q, "top_k": 3}, timeout=30)
        elapsed = time.time() - start
        assert r.status_code == 200, f"Search failed for '{q}': {r.status_code} {r.text[:200]}"
        data = r.json()
        results = data.get("results", [])
        assert len(results) > 0, f"No results for '{q}'"
        top = results[0]
        print(f"✅ '{q}' -> {len(results)} results in {elapsed*1000:.0f}ms")
        print(f"   Top: {top['meta'].get('title','?')[:60]} ({top['score']:.3f})")

def test_workflow():
    payload = {
        "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
        "dataset_format": "csv",
        "variable": "J-D",
        "title": "GISS Global Temperature Analysis"
    }
    start = time.time()
    r = requests.post(f"{BASE}/workflow/generate", json=payload, timeout=30)
    elapsed = time.time() - start
    assert r.status_code == 200, f"Workflow generation failed: {r.status_code} {r.text[:300]}"
    data = r.json()
    assert "notebook" in data, "No 'notebook' in response"
    nb = json.loads(data["notebook"])
    assert len(nb["cells"]) > 0, "Notebook has no cells"
    # cell source can be a list or string in nbformat
    cell = nb["cells"][0]
    source = cell["source"]
    code_str = ''.join(source) if isinstance(source, list) else source
    assert "pd.read_csv" in code_str, f"Template not rendered. Code starts with: {code_str[:100]}"
    assert "GLB.Ts+dSST.csv" in code_str, "Dataset URL not substituted"
    assert "J-D" in code_str, "Variable not substituted"
    print(f"✅ Workflow generated in {elapsed*1000:.0f}ms, {len(nb['cells'])} cells, code len={len(code_str)}")

def test_execute():
    code = """
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
df = pd.read_csv(url, skiprows=1)
df.columns = [str(c).strip() for c in df.columns]
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
if 'J-D' in df.columns:
    df['J-D'] = pd.to_numeric(df['J-D'], errors='coerce')
    df = df.dropna(subset=['Year', 'J-D'])
    print(f"Loaded {len(df)} rows")
    print(f"Mean temp anomaly: {df['J-D'].mean():.4f}")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Year'], df['J-D'], color='#2E86AB')
    ax.set_title('GISS Global Temperature Anomaly')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature Anomaly (C)')
    plt.tight_layout()
    plt.show()
    print("Plot generated")
else:
    print(f"Columns: {list(df.columns)[:10]}")
"""
    start = time.time()
    r = requests.post(f"{BASE}/execute/notebook", json={"code": code, "timeout": 60}, timeout=90)
    elapsed = time.time() - start
    assert r.status_code == 200, f"Execute failed: {r.status_code} {r.text[:300]}"
    data = r.json()
    print(f"✅ Execute in {elapsed:.1f}s, exit_code={data['exit_code']}")
    print(f"   Stdout: {data['stdout'][:300]}")
    if data['stderr']:
        print(f"   Stderr (first 200): {data['stderr'][:200]}")
    if data.get('images'):
        print(f"   Images: {len(data['images'])} generated")

if __name__ == "__main__":
    print("=== Photon End-to-End Test ===\n")
    
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check: {e}")
        print("Make sure backend is running: cd photon && .\\scripts\\run_server.ps1 -SkipAuth")
        exit(1)
    
    print()
    print("--- Search Tests ---")
    try:
        test_search()
    except Exception as e:
        print(f"❌ Search: {e}")
    
    print()
    print("--- Workflow Generation ---")
    try:
        test_workflow()
    except Exception as e:
        print(f"❌ Workflow: {e}")
    
    print()
    print("--- Execute Notebook ---")
    try:
        test_execute()
    except Exception as e:
        print(f"❌ Execute: {e}")
    
    print("\n=== Test Complete ===")
