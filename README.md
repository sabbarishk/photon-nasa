# Photon - NASA Data Portal

**Natural language query layer and automated workflow generator for NASA open data**

Photon is an AI-powered platform that transforms how researchers interact with NASA's vast open data repositories. Using natural language search and automated Jupyter notebook generation, it eliminates the traditional barriers of dataset discovery, format parsing, and visualization coding.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61dafb.svg)](https://reactjs.org/)

---

## 🚀 Features

### Natural Language Search
- **Semantic search** powered by Sentence Transformers (`all-MiniLM-L6-v2`)
- **34 verified NASA datasets** with direct-download URLs
- Search climate data, astronomy catalogs, Earth observation datasets
- Sub-50ms query response with in-memory vector caching

### Automated Workflow Generation
- **One-click Jupyter notebook creation** from dataset metadata
- **Intelligent CSV parsing** with 5-strategy fallback system
- **Auto-variable detection** and time-axis inference
- **3-panel visualizations**: time series + trend, histogram, rolling mean

### End-to-End Execution
- **In-browser execution** with backend code runner
- **Automatic figure capture** and base64 encoding
- **Real-time output streaming** (stdout/stderr/images)
- **No Jupyter installation required** on user machine

---

## 📦 Installation

### Prerequisites
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Git** for version control

### Backend Setup

```powershell
# Clone repository
git clone https://github.com/sabbarishk/photon-nasa.git
cd photon-nasa/photon

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend (development mode, no auth)
.\scripts\run_server.ps1 -SkipAuth
```

**Backend runs on:** `http://0.0.0.0:8000`

### Frontend Setup

```powershell
# Navigate to frontend directory
cd ..\frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend runs on:** `http://localhost:5173`

---

## Running locally

```bash
# 1. Copy the example env file and fill in your keys
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# 2. Create a virtual environment and install dependencies
cd photon
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# 3. Start the API server
cd ..
uvicorn app.main:app --reload --app-dir photon
```

The API is now at **http://localhost:8000**.

To test the full pipeline (question in, real executed result out):

```bash
curl -s -X POST http://localhost:8000/workflow/generate \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the trend over time?",
       "source": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"}'
```

> **Note:** `PHOTON_SKIP_AUTH=1` in your `.env` disables API key authentication for local development. Remove it before deploying to production.

---

## 🎯 Quick Start

### 1. Search for Datasets
Open `http://localhost:5173` and search using natural language:

```
"GISS temperature"
"Arctic sea ice"
"CO2 Mauna Loa"
"exoplanet"
```

### 2. Generate Workflow
Click **"Generate Workflow"** on any search result. The form auto-populates with:
- Dataset URL (direct CSV download)
- Format (CSV/NetCDF/HDF - currently CSV only)
- Variable to analyze (e.g., `J-D`, `Glob`, `Extent`)

### 3. Execute & Visualize
Click **"Generate Notebook"** → **"Run & Visualize"**

**Output:**
- ✅ Parsed data summary
- ✅ 3 interactive charts (time series, histogram, trend)
- ✅ Statistical insights
- ✅ Downloadable `.ipynb` file

---

## 📊 Supported Datasets

### Climate & Temperature (CSV)
| Dataset | Search Keywords | Variable |
|---------|----------------|----------|
| GISS Global Temperature | `GISS temperature`, `global warming` | `J-D`, `Glob` |
| GISS Zonal Temperature | `zonal temperature`, `latitude bands` | `Glob`, `NHem`, `SHem` |
| Mauna Loa CO2 | `CO2 Mauna Loa`, `carbon dioxide` | `average` |
| Global Methane | `methane`, `CH4` | `average` |

### Sea Ice (CSV)
| Dataset | Search Keywords | Variable |
|---------|----------------|----------|
| Arctic Sea Ice Extent | `Arctic sea ice`, `NSIDC` | `Extent` |
| Antarctic Sea Ice Extent | `Antarctic ice`, `sea ice extent` | `Extent` |

### Astronomy (CSV)
| Dataset | Search Keywords | Variable |
|---------|----------------|----------|
| NASA Exoplanet Archive | `exoplanet`, `confirmed planets` | `pl_rade`, `pl_masse` |
| Near-Earth Objects | `asteroid`, `NEO`, `close approaches` | `dist_min` |

### Ice Mass (TXT/CSV)
| Dataset | Search Keywords | Variable |
|---------|----------------|----------|
| GRACE Greenland Ice Mass | `Greenland ice`, `ice mass loss` | `ice_mass` |
| GRACE Antarctica Ice Mass | `Antarctica ice`, `ice sheet` | `ice_mass` |

**Total:** 34 verified datasets with direct-download URLs

---

## 🏗️ Architecture

```
photon-nasa/
├── photon/                    # Backend (FastAPI)
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── routes/
│   │   │   ├── workflow.py   # Notebook generation
│   │   │   ├── execute.py    # Code execution engine
│   │   │   └── query.py      # Vector search
│   │   └── templates/
│   │       └── csv.txt       # CSV analysis template
│   ├── scripts/
│   │   ├── run_server.ps1    # Backend launcher
│   │   └── bulk_ingest.py    # Dataset ingestion
│   └── data/
│       └── vectors.json      # Vector store (34 datasets)
│
└── frontend/                  # Frontend (React + Vite)
    ├── src/
    │   ├── components/
    │   │   ├── Search.jsx    # Search interface
    │   │   └── WorkflowGenerator.jsx  # Notebook UI
    │   ├── services/
    │   │   └── api.js        # Backend API client
    │   └── context/
    │       └── DatasetContext.jsx  # Dataset state
    └── package.json
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`photon/.env`):
```bash
PHOTON_SKIP_AUTH=1          # Skip authentication (dev only)
HF_MODEL=all-MiniLM-L6-v2   # Embedding model
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_URL=http://localhost:8000
```

### Port Configuration

**Backend:** Port `8000` (Windows Hyper-V reserves 8001+, use 8000)

**Frontend:** Port `5173` (Vite default)

---

## 🛠️ Development

### Adding New Datasets

Edit `photon/scripts/bulk_ingest.py`:

```python
VERIFIED_DATASETS = [
    {
        "id": "my-dataset",
        "meta": {
            "title": "My NASA Dataset",
            "summary": "Description for semantic search",
            "dataset_url": "https://direct-download-url.csv",  # Must be direct download!
            "format": "CSV",
            "variable": "target_column_name",
            "category": "climate",
            "keywords": "search, keywords, comma, separated"
        }
    }
]
```

Run ingestion:
```powershell
python -m scripts.bulk_ingest --clear
```

### Creating Templates for Other Formats

**NetCDF Template** (`photon/app/templates/netcdf.txt`):
```python
import xarray as xr
ds = xr.open_dataset("{{ dataset_url }}")
var = ds["{{ variable }}"]
var.plot()
```

**HDF5 Template** (`photon/app/templates/hdf5.txt`):
```python
import h5py
import pandas as pd
with h5py.File("{{ dataset_url }}", 'r') as f:
    data = f["{{ variable }}"][:]
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

**Embedding model not loading:**
```powershell
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Frontend Issues

**CORS errors:**
- Ensure backend is running on `0.0.0.0:8000` (not `127.0.0.1`)
- Check `frontend/.env` has correct `VITE_API_URL`

**Blank visualizations:**
- Refresh browser after backend restart
- Check browser console (F12) for JavaScript errors
- Verify dataset URL returns CSV (not HTML landing page)

### Execution Errors

**Syntax errors in generated code:**
- Ensure you pulled latest commits (BOM fix: `8466f74`)
- Regenerate notebook after template updates

**No figures appearing:**
- Backend must be restarted after `execute.py` changes
- Check Output section shows `[SAVED]` message
- Verify PNG files created in temp directory

---

## 📈 Performance

- **Search latency:** 28-55ms (in-memory vector cache + NumPy vectorization)
- **Notebook generation:** <500ms (Jinja2 template rendering)
- **Code execution:** 2-5s (CSV fetch + parse + visualize)
- **Vector store size:** 34 datasets, ~2MB embeddings

---

## 🔒 Security Notes

- **Development mode** (`-SkipAuth`) disables authentication - **DO NOT use in production**
- **Code execution** runs arbitrary Python - isolate in containerized environment for production
- **API rate limiting** not implemented - add in production deployment

---

## 🚢 Production Deployment

### Docker Deployment

```dockerfile
# Backend
FROM python:3.11-slim
WORKDIR /app
COPY photon/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
- Use **PostgreSQL** for vector store (not JSON file)
- Enable **authentication** (remove `-SkipAuth`)
- Add **rate limiting** (nginx/Cloudflare)
- Use **Redis** for session caching
- Deploy **frontend** to Vercel/Netlify
- Deploy **backend** to AWS ECS/GCP Cloud Run

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **NASA Open Data Portal** for dataset APIs
- **Sentence Transformers** for embedding models
- **FastAPI** for backend framework
- **React** and **Vite** for frontend tooling
- **Matplotlib** for visualization engine

---

## 📧 Contact

**Sabbarish Khanna Subramanian**  
GitHub: [@sabbarishk](https://github.com/sabbarishk)  
Repository: [photon-nasa](https://github.com/sabbarishk/photon-nasa)

---

## 🗺️ Roadmap

- [ ] Add NetCDF/HDF5 template support
- [ ] Implement NASA Earthdata authentication
- [ ] Add real-time data streaming visualization
- [ ] Integrate with Jupyter Hub for remote execution
- [ ] Add dataset recommendation engine
- [ ] Support for multi-variable analysis
- [ ] Export workflows to Python scripts
- [ ] Add unit tests and CI/CD pipeline

---

**Built with ❤️ for researchers, by researchers**
