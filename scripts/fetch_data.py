"""
Fetch Toronto Open Data via CKAN API
Downloads datasets for GeoPulse Toronto analysis
"""
import os
import requests
import json
from pathlib import Path

# CKAN API base
CKAN_BASE = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"

# Dataset package IDs from open.toronto.ca
DATASETS = {
    "neighbourhoods": "neighbourhoods",  # Neighbourhood boundaries
    "mci_crime": "police-annual-statistical-report-major-crime-indicators",
    "ttc_stops": "ttc-routes-and-schedules",  # Will need GTFS
    "service_311": "311-service-requests-customer-initiated",
    "neighbourhood_profiles": "neighbourhood-profiles"
}

def fetch_package_info(package_id):
    """Get package metadata from CKAN"""
    url = f"{CKAN_BASE}/package_show"
    response = requests.get(url, params={"id": package_id})
    response.raise_for_status()
    return response.json()["result"]

def download_resource(resource_url, output_path):
    """Download a resource file"""
    print(f"Downloading {resource_url}")
    response = requests.get(resource_url, stream=True)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved to {output_path}")

def fetch_toronto_data():
    """Main data fetching function"""
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {"datasets": {}, "timestamp": None}
    
    print("Fetching Toronto Open Data...")
    
    # 1. Neighbourhoods GeoJSON
    try:
        print("\n1. Fetching neighbourhood boundaries...")
        pkg = fetch_package_info(DATASETS["neighbourhoods"])
        for resource in pkg["resources"]:
            if resource["format"].upper() in ["GEOJSON", "JSON"]:
                url = resource["url"]
                download_resource(url, raw_dir / "neighbourhoods.geojson")
                manifest["datasets"]["neighbourhoods"] = {
                    "file": "neighbourhoods.geojson",
                    "source": url,
                    "format": "GeoJSON"
                }
                break
    except Exception as e:
        print(f"Error fetching neighbourhoods: {e}")
    
    # 2. Crime data
    try:
        print("\n2. Fetching crime data (MCI)...")
        pkg = fetch_package_info(DATASETS["mci_crime"])
        for resource in pkg["resources"]:
            if "neighbourhood" in resource["name"].lower() and resource["format"].upper() == "CSV":
                url = resource["url"]
                download_resource(url, raw_dir / "mci_crime.csv")
                manifest["datasets"]["crime"] = {
                    "file": "mci_crime.csv",
                    "source": url,
                    "format": "CSV"
                }
                break
    except Exception as e:
        print(f"Error fetching crime data: {e}")
    
    # 3. TTC GTFS (stops)
    try:
        print("\n3. Fetching TTC transit data...")
        pkg = fetch_package_info(DATASETS["ttc_stops"])
        for resource in pkg["resources"]:
            if "gtfs" in resource["name"].lower() or resource["format"].upper() == "ZIP":
                url = resource["url"]
                download_resource(url, raw_dir / "ttc_gtfs.zip")
                manifest["datasets"]["transit"] = {
                    "file": "ttc_gtfs.zip",
                    "source": url,
                    "format": "GTFS"
                }
                break
    except Exception as e:
        print(f"Error fetching transit data: {e}")
    
    # 4. 311 Service Requests
    try:
        print("\n4. Fetching 311 service requests...")
        pkg = fetch_package_info(DATASETS["service_311"])
        for resource in pkg["resources"]:
            if resource["format"].upper() == "CSV":
                url = resource["url"]
                download_resource(url, raw_dir / "service_311.csv")
                manifest["datasets"]["service_311"] = {
                    "file": "service_311.csv",
                    "source": url,
                    "format": "CSV"
                }
                break
    except Exception as e:
        print(f"Error fetching 311 data: {e}")
    
    # 5. Neighbourhood profiles (for population)
    try:
        print("\n5. Fetching neighbourhood profiles...")
        pkg = fetch_package_info(DATASETS["neighbourhood_profiles"])
        for resource in pkg["resources"]:
            if resource["format"].upper() in ["CSV", "XLSX"]:
                url = resource["url"]
                ext = resource["format"].lower()
                download_resource(url, raw_dir / f"neighbourhood_profiles.{ext}")
                manifest["datasets"]["profiles"] = {
                    "file": f"neighbourhood_profiles.{ext}",
                    "source": url,
                    "format": resource["format"]
                }
                break
    except Exception as e:
        print(f"Error fetching neighbourhood profiles: {e}")
    
    # Save manifest
    import datetime
    manifest["timestamp"] = datetime.datetime.now().isoformat()
    with open(raw_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print("\n✓ Data fetch complete. See data/raw/manifest.json for details.")

if __name__ == "__main__":
    fetch_toronto_data()
