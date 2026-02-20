# API Reference

## Photon-NASA Complete API Documentation

---

## Table of Contents

1. [Base URL & Authentication](#base-url--authentication)
2. [Endpoints](#endpoints)
3. [Rate Limits](#rate-limits)
4. [Error Responses](#error-responses)
5. [Examples](#examples)

---

## 1. BASE URL & AUTHENTICATION

### Base URLs

```
Development: http://localhost:8000
Production:  https://api.photon-nasa.com (example)
```

### Authentication

**Optional API Key Authentication:**

```http
POST /query/
Headers:
  X-API-Key: your-api-key-here
  Content-Type: application/json
```

**To disable auth (development):**
```bash
export PHOTON_SKIP_AUTH=1
# Or in .env file:
PHOTON_SKIP_AUTH=1
```

**Generate API Key:**
```bash
python scripts/create_api_key.py
# Output: API Key: photon_abc123def456...
```

---

## 2. ENDPOINTS

### GET /health

Check API health status.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-19T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### POST /query/

Search NASA datasets using natural language.

**Request:**
```http
POST /query/
Content-Type: application/json

{
  "query": "MODIS temperature data",
  "top_k": 5
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | Natural language search query |
| `top_k` | integer | No | 5 | Number of results (1-20) |

**Response:**
```json
{
  "query": "MODIS temperature data",
  "results": [
    {
      "id": "giss-global-temp",
      "score": 0.92,
      "meta": {
        "title": "GISS Global Temperature Analysis",
        "description": "Global surface temperature anomalies from GISS",
        "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
        "format": "CSV",
        "variable": "J-D",
        "category": "climate",
        "keywords": "temperature, global warming, GISS, climate change"
      }
    },
    {
      "id": "giss-hemispheric-temp",
      "score": 0.89,
      "meta": {
        "title": "GISS Hemispheric Temperature",
        "description": "Northern and Southern hemisphere temperature anomalies",
        "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv",
        "format": "CSV",
        "variable": "J-D",
        "category": "climate"
      }
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Echo of the search query |
| `results` | array | Array of matching datasets |
| `results[].id` | string | Unique dataset identifier |
| `results[].score` | float | Similarity score (0-1, higher is better) |
| `results[].meta` | object | Dataset metadata |
| `results[].meta.title` | string | Dataset title |
| `results[].meta.dataset_url` | string | Direct download URL |
| `results[].meta.format` | string | Format (CSV, NetCDF, HDF5, JSON) |
| `results[].meta.variable` | string | Primary variable/column name |

**Status Codes:**
- `200 OK` - Search successful
- `400 Bad Request` - Invalid query or parameters
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Embedding or search failed

**Error Responses:**
```json
// 400 Bad Request
{
  "detail": "Query cannot be empty"
}

// 500 Internal Server Error
{
  "detail": "Embedding generation failed"
}
```

---

### POST /workflow/generate

Generate Jupyter notebook for dataset analysis.

**Request:**
```http
POST /workflow/generate
Content-Type: application/json

{
  "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
  "dataset_format": "csv",
  "variable": "J-D",
  "title": "GISS Global Temperature Analysis"
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_url` | string | Yes | - | URL to dataset |
| `dataset_format` | string | Yes | - | Format: `csv`, `netcdf`, `hdf5`, `json` |
| `variable` | string | Yes | - | Variable/column name to analyze |
| `title` | string | No | "Generated Workflow" | Notebook title |

**Response:**
```json
{
  "notebook": {
    "cells": [
      {
        "cell_type": "code",
        "execution_count": null,
        "id": "a1b2c3d4",
        "metadata": {},
        "outputs": [],
        "source": [
          "# GISS Global Temperature Analysis",
          "import pandas as pd",
          "import matplotlib.pyplot as plt",
          "...",
          "plt.show()"
        ]
      }
    ],
    "metadata": {
      "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
      }
    },
    "nbformat": 4,
    "nbformat_minor": 5
  },
  "preview": "# GISS Global Temperature Analysis\nimport pandas as pd\nimport matplotlib.pyplot as plt\n...",
  "format": "csv"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `notebook` | object | Complete Jupyter notebook in JSON format |
| `preview` | string | First 500 characters of code |
| `format` | string | Dataset format used |

**Generated Notebook Contains:**
- Data loading code with format-specific libraries
- Exploratory data analysis (head, describe, info)
- 3-panel visualization (time series, histogram, rolling average)
- Error handling and data validation

**Status Codes:**
- `200 OK` - Notebook generated successfully
- `400 Bad Request` - Invalid format or missing template
- `500 Internal Server Error` - Template rendering failed

**Error Responses:**
```json
// 400 Bad Request
{
  "detail": "No template for format: xyz"
}

// 500 Internal Server Error
{
  "detail": "Failed to generate workflow: Template render error"
}
```

---

### POST /execute/notebook

Execute Python code and return output. **⚠️ Experimental feature.**

**Request:**
```http
POST /execute/notebook
Content-Type: application/json

{
  "code": "import pandas as pd\ndf = pd.read_csv('https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv')\nprint(df.head())",
  "timeout": 60
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `code` | string | Yes | - | Python code to execute |
| `timeout` | integer | No | 60 | Timeout in seconds (max: 120) |

**Response:**
```json
{
  "stdout": "   Year  J-D  D-N\n0  1880 -0.16 -0.26\n1  1881 -0.07 -0.14\n...",
  "stderr": "",
  "exit_code": 0,
  "images": [
    {
      "filename": "output_fig_1.png",
      "data": "data:image/png;base64,iVBORw0KGgoAAAANS..."
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `stdout` | string | Standard output from execution |
| `stderr` | string | Standard error output |
| `exit_code` | integer | Exit code (0 = success) |
| `images` | array | Generated matplotlib figures (base64) |

**Status Codes:**
- `200 OK` - Execution completed (check exit_code)
- `408 Request Timeout` - Execution exceeded timeout
- `500 Internal Server Error` - Execution failed

**Error Responses:**
```json
// 408 Timeout
{
  "detail": "Execution timed out after 60 seconds"
}

// 500 Execution Error
{
  "detail": "Code execution failed",
  "stderr": "ModuleNotFoundError: No module named 'xarray'"
}
```

**⚠️ Security Warning:**

This endpoint is **experimental** and runs arbitrary code. For production:
- Run in isolated Docker containers
- Implement strict resource limits (CPU, memory, disk)
- Validate code before execution
- Use separate execution service
- Network isolation (no outbound connections)

---

## 3. RATE LIMITS

### Default Limits

| Tier | Requests per minute | Requests per hour |
|------|---------------------|-------------------|
| **Default** | 120 | 1000 |
| **With API Key** | Configurable | Configurable |

### Headers

Every response includes rate limit headers:

```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1705747200
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per minute |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

### 429 Response

When rate limit is exceeded:

```json
{
  "detail": "Rate limit exceeded. Try again in 32 seconds.",
  "retry_after": 32
}
```

---

## 4. ERROR RESPONSES

### Standard Error Format

All errors return JSON with a `detail` field:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid parameters, missing fields |
| `401` | Unauthorized | Invalid API key |
| `404` | Not Found | Endpoint doesn't exist |
| `408` | Request Timeout | Execution took too long |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error, embedding failed |
| `503` | Service Unavailable | Server is down |

### Common Error Messages

**Search Errors:**
```json
// Empty query
{"detail": "Query cannot be empty"}

// Embedding failed
{"detail": "Embedding generation failed"}
```

**Workflow Errors:**
```json
// Unsupported format
{"detail": "No template for format: xyz"}

// Template error
{"detail": "Failed to generate workflow: Template render error"}
```

**Execution Errors:**
```json
// Timeout
{"detail": "Execution timed out after 60 seconds"}

// Code error
{"detail": "Code execution failed", "stderr": "SyntaxError: ..."}
```

---

## 5. EXAMPLES

### Example 1: Full Search to Notebook Flow

**Step 1: Search**
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Arctic sea ice extent",
    "top_k": 3
  }'
```

**Response:**
```json
{
  "query": "Arctic sea ice extent",
  "results": [
    {
      "id": "arctic-sea-ice",
      "score": 0.94,
      "meta": {
        "title": "Arctic Sea Ice Extent Monthly",
        "dataset_url": "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/N_seaice_extent_monthly_v3.0.csv",
        "format": "CSV",
        "variable": "Extent"
      }
    }
  ]
}
```

**Step 2: Generate Notebook**
```bash
curl -X POST http://localhost:8000/workflow/generate \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_url": "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/N_seaice_extent_monthly_v3.0.csv",
    "dataset_format": "csv",
    "variable": "Extent",
    "title": "Arctic Sea Ice Analysis"
  }'
```

**Step 3: Execute (Optional)**
```bash
curl -X POST http://localhost:8000/execute/notebook \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pandas as pd\ndf = pd.read_csv(\"https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/N_seaice_extent_monthly_v3.0.csv\")\nprint(df.head())",
    "timeout": 60
  }'
```

---

### Example 2: Search with API Key

```bash
curl -X POST http://localhost:8000/query/ \
  -H "X-API-Key: photon_abc123def456..." \
  -H "Content-Type: application/json" \
  -d '{
    "query": "GISS temperature",
    "top_k": 5
  }'
```

---

### Example 3: Python Client

```python
import requests

API_BASE_URL = "http://localhost:8000"

# Search
response = requests.post(
    f"{API_BASE_URL}/query/",
    json={"query": "CO2 concentration", "top_k": 3}
)
results = response.json()["results"]

# Generate workflow
if results:
    dataset = results[0]
    response = requests.post(
        f"{API_BASE_URL}/workflow/generate",
        json={
            "dataset_url": dataset["meta"]["dataset_url"],
            "dataset_format": dataset["meta"]["format"],
            "variable": dataset["meta"]["variable"],
            "title": "CO2 Analysis"
        }
    )
    notebook = response.json()["notebook"]
    
    # Save notebook
    import json
    with open("co2_analysis.ipynb", "w") as f:
        json.dump(notebook, f, indent=2)
```

---

### Example 4: JavaScript Client

```javascript
const API_BASE_URL = "http://localhost:8000"

// Search
async function searchDatasets(query) {
  const response = await fetch(`${API_BASE_URL}/query/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: 5 })
  })
  return await response.json()
}

// Generate workflow
async function generateWorkflow(datasetUrl, format, variable, title) {
  const response = await fetch(`${API_BASE_URL}/workflow/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset_url: datasetUrl,
      dataset_format: format,
      variable,
      title
    })
  })
  return await response.json()
}

// Usage
const results = await searchDatasets("temperature data")
const notebook = await generateWorkflow(
  results.results[0].meta.dataset_url,
  results.results[0].meta.format,
  results.results[0].meta.variable,
  "Temperature Analysis"
)
```

---

*For architecture details, see [Technical Architecture Guide](01_TECHNICAL_ARCHITECTURE.md)*  
*For deployment instructions, see [Deployment Guide](03_DEPLOYMENT_GUIDE.md)*
