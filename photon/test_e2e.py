"""
Test end-to-end workflow with newly ingested datasets
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_search():
    """Test search endpoint with various queries"""
    print("=" * 60)
    print("TEST 1: Search for different dataset types")
    print("=" * 60)
    
    test_queries = [
        "MODIS temperature",
        "ocean salinity",
        "precipitation GPM",
        "ice sheet elevation",
        "vegetation index"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        response = requests.post(f"{BASE_URL}/query/", json={"query": query, "top_k": 3})
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"   ✅ Found {len(results)} results")
            
            for i, result in enumerate(results[:2], 1):
                title = result.get("meta", {}).get("title", "No title")[:60]
                score = result.get("score", 0)
                dataset_url = result.get("meta", {}).get("dataset_url", "N/A")
                format_type = result.get("meta", {}).get("format", "unknown")
                
                print(f"   [{i}] {title}...")
                print(f"       Score: {score:.3f} | Format: {format_type}")
                print(f"       URL: {dataset_url[:50]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")


def test_workflow_generation():
    """Test workflow generation with a real dataset"""
    print("\n" + "=" * 60)
    print("TEST 2: Generate workflow from search result")
    print("=" * 60)
    
    # First, search for GISS temperature
    print("\n🔍 Searching for 'GISS temperature'...")
    response = requests.post(f"{BASE_URL}/query/", json={"query": "GISS temperature", "top_k": 1})
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            result = results[0]
            meta = result.get("meta", {})
            
            print(f"   ✅ Found: {meta.get('title', 'Unknown')[:60]}")
            
            # Try to generate workflow
            dataset_url = meta.get("dataset_url") or meta.get("landing_page", "")
            format_type = meta.get("format", "csv")
            
            if not dataset_url or not dataset_url.startswith("http"):
                # Fall back to known working URL
                dataset_url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
                format_type = "csv"
                print(f"   ⚠️  Using fallback URL: {dataset_url}")
            
            print(f"\n📝 Generating workflow...")
            print(f"   URL: {dataset_url}")
            print(f"   Format: {format_type}")
            
            workflow_response = requests.post(
                f"{BASE_URL}/workflow/generate",
                json={
                    "dataset_url": dataset_url,
                    "format": format_type,
                    "variable": "J-D",
                    "title": "GISS Temperature Analysis Test"
                }
            )
            
            if workflow_response.status_code == 200:
                workflow_data = workflow_response.json()
                print(f"   ✅ Workflow generated successfully!")
                print(f"   Notebook cells: {workflow_data.get('cell_count', 'N/A')}")
                print(f"   Format: {workflow_data.get('format', 'N/A')}")
            else:
                print(f"   ❌ Workflow generation failed: {workflow_response.status_code}")
                print(f"   Error: {workflow_response.text[:200]}")
        else:
            print("   ❌ No results found")
    else:
        print(f"   ❌ Search failed: {response.status_code}")


def test_metadata_presence():
    """Test that all search results have required metadata fields"""
    print("\n" + "=" * 60)
    print("TEST 3: Verify metadata fields are present")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/query/", json={"query": "MODIS", "top_k": 5})
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        print(f"\n✅ Retrieved {len(results)} results\n")
        
        required_fields = ["title", "dataset_url", "format"]
        missing_counts = {field: 0 for field in required_fields}
        
        for i, result in enumerate(results, 1):
            meta = result.get("meta", {})
            print(f"Result {i}:")
            
            for field in required_fields:
                value = meta.get(field, "")
                status = "✅" if value else "❌"
                print(f"  {status} {field}: {str(value)[:40]}")
                if not value:
                    missing_counts[field] += 1
            print()
        
        print("Summary:")
        for field, count in missing_counts.items():
            if count > 0:
                print(f"  ⚠️  {field} missing in {count}/{len(results)} results")
            else:
                print(f"  ✅ {field} present in all results")
    else:
        print(f"❌ Failed: {response.status_code}")


if __name__ == "__main__":
    print("\n🚀 Testing Photon NASA Application")
    print("=" * 60)
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy\n")
        else:
            print("❌ Backend health check failed\n")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}\n")
        print("Please make sure the backend is running on http://localhost:8000")
        exit(1)
    
    # Run tests
    test_search()
    test_workflow_generation()
    test_metadata_presence()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
