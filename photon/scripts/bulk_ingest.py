"""
Bulk ingestion script for NASA datasets from CMR API.

Automatically populates the vector database with 50-100 diverse NASA datasets
covering atmosphere, land, ocean, cryosphere, and climate science.

Usage:
    python -m scripts.bulk_ingest --limit 100
    python -m scripts.bulk_ingest --categories atmosphere land ocean
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import argparse
from typing import List, Dict
import requests
from app.services.hf_api import get_embedding
from app.services.vector_store import get_vector_store

# Curated list of high-value NASA dataset collections
DATASET_CATEGORIES = {
    "atmosphere": [
        "AIRS",           # Atmospheric Infrared Sounder
        "MOPITT",         # CO measurements
        "OMI",            # Ozone Monitoring Instrument
        "TROPOMI",        # Air quality
        "CALIPSO",        # Cloud-Aerosol Lidar
    ],
    "land": [
        "MOD13Q1",        # MODIS Vegetation Indices
        "MOD11A1",        # MODIS Land Surface Temperature
        "MCD43A4",        # MODIS BRDF-Adjusted Reflectance
        "SMAP",           # Soil Moisture Active Passive
        "Landsat",        # Landsat series
        "VNP09GA",        # VIIRS Surface Reflectance
    ],
    "ocean": [
        "MODIS_A-JPL-L2P-v2019.0",  # MODIS SST
        "GHRSST",         # Sea Surface Temperature
        "Jason-3",        # Sea level altimetry
        "AQUARIUS",       # Ocean salinity
        "SeaWiFS",        # Ocean color
    ],
    "cryosphere": [
        "ICESat-2",       # Ice elevation
        "GRACE",          # Gravity and ice mass
        "NSIDC",          # Sea ice concentration
        "MEaSUREs",       # Glacier velocity
    ],
    "climate": [
        "GISS",           # Temperature analysis
        "MERRA-2",        # Reanalysis
        "GPM",            # Precipitation
        "TRMM",           # Tropical rainfall
    ],
    "cross_cutting": [
        "MODIS",          # General MODIS products
        "VIIRS",          # Visible Infrared Imaging
        "AVHRR",          # Historical climate data
    ]
}

class BulkIngestionManager:
    """Manages bulk ingestion of NASA datasets."""
    
    def __init__(self, vector_store_path: str = "data/vectors.json"):
        self.vector_store = get_vector_store(vector_store_path)
        self.ingested_count = 0
        self.failed_count = 0
        
    def fetch_datasets_for_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Fetch datasets from NASA CMR for a given keyword."""
        print(f"  🔍 Searching for '{keyword}'...")
        
        try:
            # Use CMR API to search for datasets
            url = "https://cmr.earthdata.nasa.gov/search/collections.json"
            params = {
                "keyword": keyword,
                "page_size": limit,
                "has_granules": "true",  # Only datasets with actual data
                "sort_key": "-usage_score",  # Most popular first
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            entries = data.get("feed", {}).get("entry", [])
            
            datasets = []
            for entry in entries:
                # Extract data format
                format_type = "unknown"
                if entry.get("links"):
                    for link in entry["links"]:
                        if "data" in link.get("rel", "").lower():
                            href = link.get("href", "")
                            if ".nc" in href or "netcdf" in href.lower():
                                format_type = "NetCDF"
                            elif ".hdf" in href or "hdf" in href.lower():
                                format_type = "HDF5"
                            elif ".csv" in href or "csv" in href.lower():
                                format_type = "CSV"
                            break
                
                # Get data access URL
                data_url = entry.get("id", "")
                if entry.get("links"):
                    for link in entry["links"]:
                        if link.get("rel") == "http://esipfed.org/ns/fedsearch/1.1/data#":
                            data_url = link.get("href", data_url)
                            break
                
                dataset = {
                    "id": entry.get("id", ""),
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "landing_page": data_url,
                    "dataset_url": data_url,
                    "format": format_type,
                    "keywords": keyword,
                }
                datasets.append(dataset)
            
            print(f"    ✅ Found {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            print(f"    ❌ Error fetching '{keyword}': {e}")
            return []
    
    async def ingest_dataset(self, dataset: Dict) -> bool:
        """Ingest a single dataset into the vector store."""
        try:
            # Create summary text for embedding
            summary_text = f"{dataset['title']}. {dataset['summary']}"
            
            # Generate embedding (synchronous call)
            embedding = get_embedding(summary_text)
            
            # Prepare metadata
            meta = {
                "title": dataset["title"],
                "summary": dataset["summary"],
                "landing_page": dataset["landing_page"],
                "dataset_url": dataset["dataset_url"],
                "format": dataset["format"],
                "keywords": dataset["keywords"],
            }
            
            # Add to vector store
            self.vector_store.add(dataset["id"], meta, embedding)
            
            return True
            
        except Exception as e:
            print(f"    ❌ Failed to ingest '{dataset['title'][:50]}...': {e}")
            return False
    
    async def ingest_category(self, category: str, keywords: List[str], limit_per_keyword: int):
        """Ingest all datasets for a category."""
        print(f"\n📂 Category: {category.upper()}")
        print(f"   Keywords: {', '.join(keywords)}")
        
        all_datasets = []
        seen_ids = set()
        
        # Fetch datasets for each keyword
        for keyword in keywords:
            datasets = self.fetch_datasets_for_keyword(keyword, limit_per_keyword)
            
            # Deduplicate by ID
            for ds in datasets:
                if ds["id"] not in seen_ids:
                    all_datasets.append(ds)
                    seen_ids.add(ds["id"])
        
        print(f"   📊 Total unique datasets: {len(all_datasets)}")
        
        # Ingest datasets
        for i, dataset in enumerate(all_datasets, 1):
            print(f"   [{i}/{len(all_datasets)}] Ingesting: {dataset['title'][:60]}...")
            success = await self.ingest_dataset(dataset)
            
            if success:
                self.ingested_count += 1
            else:
                self.failed_count += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
    
    async def run(self, categories: List[str] = None, limit_per_keyword: int = 5):
        """Run bulk ingestion for specified categories."""
        print("🚀 NASA Bulk Dataset Ingestion")
        print("=" * 60)
        
        # Default to all categories if none specified
        if not categories:
            categories = list(DATASET_CATEGORIES.keys())
        
        print(f"📋 Categories to ingest: {', '.join(categories)}")
        print(f"📊 Limit per keyword: {limit_per_keyword}")
        print()
        
        # Ingest each category
        for category in categories:
            if category not in DATASET_CATEGORIES:
                print(f"⚠️  Unknown category: {category}")
                continue
            
            keywords = DATASET_CATEGORIES[category]
            await self.ingest_category(category, keywords, limit_per_keyword)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"✅ Ingestion Complete!")
        print(f"   Total ingested: {self.ingested_count}")
        print(f"   Total failed: {self.failed_count}")
        if self.ingested_count + self.failed_count > 0:
            print(f"   Success rate: {self.ingested_count / (self.ingested_count + self.failed_count) * 100:.1f}%")
        print(f"   Vector store: {self.vector_store.store_path}")


async def main():
    parser = argparse.ArgumentParser(description="Bulk ingest NASA datasets")
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=list(DATASET_CATEGORIES.keys()) + ["all"],
        default=["all"],
        help="Categories to ingest (default: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit per keyword (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Handle "all" category
    categories = None if "all" in args.categories else args.categories
    
    # Run ingestion
    manager = BulkIngestionManager()
    await manager.run(categories=categories, limit_per_keyword=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
