"""
Generate sample Toronto neighbourhood data for GeoPulse demo
Creates synthetic but realistic GeoJSON with all required features
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from pathlib import Path
import json

# Toronto bounding box (approximate)
LAT_MIN, LAT_MAX = 43.58, 43.85
LON_MIN, LON_MAX = -79.64, -79.12

# Sample neighbourhood names (real Toronto neighbourhoods)
NEIGHBOURHOODS = [
    "Agincourt North", "Agincourt South-Malvern West", "Alderwood", "Annex",
    "Banbury-Don Mills", "Bathurst Manor", "Bay Street Corridor", "Bayview Village",
    "Bayview Woods-Steeles", "Bedford Park-Nortown", "Beechborough-Greenbrook",
    "Bendale", "Birchcliffe-Cliffside", "Black Creek", "Blake-Jones",
    "Briar Hill-Belgravia", "Bridle Path-Sunnybrook-York Mills", "Broadview North",
    "Brookhaven-Amesbury", "Cabbagetown-South St.James Town", "Caledonia-Fairbank",
    "Casa Loma", "Centennial Scarborough", "Church-Yonge Corridor", "Clairlea-Birchmount",
    "Clanton Park", "Cliffcrest", "Corso Italia-Davenport", "Danforth",
    "Danforth East York", "Don Valley Village", "Dorset Park", "Dovercourt-Wallace Emerson-Junction",
    "Downsview-Roding-CFB", "Dufferin Grove", "East End-Danforth", "Edenbridge-Humber Valley",
    "Eglinton East", "Elms-Old Rexdale", "Englemount-Lawrence", "Eringate-Centennial-West Deane",
    "Etobicoke West Mall", "Flemingdon Park", "Forest Hill North", "Forest Hill South",
    "Glenfield-Jane Heights", "Greenwood-Coxwell", "Guildwood", "Henry Farm",
    "High Park North", "High Park-Swansea", "Highland Creek", "Hillcrest Village",
    "Humber Bay Shores", "Humber Heights-Westmount", "Humber Summit", "Humbermede",
    "Humewood-Cedarvale", "Ionview", "Islington-City Centre West", "Junction Area",
    "Keelesdale-Eglinton West", "Kennedy Park", "Kensington-Chinatown", "Kingsview Village-The Westway",
    "Kingsway South", "L'Amoreaux", "Lambton Baby Point", "Lansing-Westgate",
    "Lawrence Park North", "Lawrence Park South", "Leaside-Bennington", "Little Portugal",
    "Long Branch", "Malvern", "Maple Leaf", "Markland Wood",
    "Mimico (includes Humber Bay Shores)", "Morningside", "Moss Park", "Mount Dennis",
    "Mount Olive-Silverstone-Jamestown", "Mount Pleasant East", "Mount Pleasant West",
    "New Toronto", "Newtonbrook East", "Newtonbrook West", "Niagara",
    "North Riverdale", "North St.James Town", "O'Connor-Parkview", "Oakridge",
    "Oakwood Village", "Old East York", "Palmerston-Little Italy", "Parkwoods-Donalda",
    "Pelmo Park-Humberlea", "Playter Estates-Danforth", "Pleasant View", "Princess-Rosethorn",
    "Regent Park", "Rexdale-Kipling", "Rockcliffe-Smythe", "Roncesvalles",
    "Rosedale-Moore Park", "Rouge", "Runnymede-Bloor West Village", "Rustic",
    "Scarborough Village", "South Parkdale", "South Riverdale", "St.Andrew-Windfields",
    "Steeles", "Stonegate-Queensway", "Tam O'Shanter-Sullivan", "Taylor-Massey",
    "The Beaches", "Thistletown-Beaumond Heights", "Thorncliffe Park", "Trinity-Bellwoods",
    "University", "Victoria Village", "Waterfront Communities-The Island", "West Hill",
    "West Humber-Clairville", "Westminster-Branson", "Weston", "Weston-Pelham Park",
    "Wexford/Maryvale", "Willowdale East", "Willowdale West", "Willowridge-Martingrove-Richview",
    "Woburn", "Woodbine Corridor", "Woodbine-Lumsden", "Wychwood",
    "Yonge-Eglinton", "Yonge-St.Clair", "York University Heights", "Yorkdale-Glen Park"
]

def create_grid_polygons(num_neighbourhoods):
    """Create grid of polygons covering Toronto"""
    np.random.seed(42)
    
    # Create a grid
    cols = int(np.sqrt(num_neighbourhoods))
    rows = (num_neighbourhoods + cols - 1) // cols
    
    lat_step = (LAT_MAX - LAT_MIN) / rows
    lon_step = (LON_MAX - LON_MIN) / cols
    
    polygons = []
    names = NEIGHBOURHOODS[:num_neighbourhoods]
    
    for i in range(num_neighbourhoods):
        row = i // cols
        col = i % cols
        
        # Base coordinates
        lat_base = LAT_MIN + row * lat_step
        lon_base = LON_MIN + col * lon_step
        
        # Add some randomness to make it look more natural
        jitter = 0.003
        lat_j = np.random.uniform(-jitter, jitter, 4)
        lon_j = np.random.uniform(-jitter, jitter, 4)
        
        # Create polygon
        coords = [
            (lon_base + lon_j[0], lat_base + lat_j[0]),
            (lon_base + lon_step + lon_j[1], lat_base + lat_j[1]),
            (lon_base + lon_step + lon_j[2], lat_base + lat_step + lat_j[2]),
            (lon_base + lon_j[3], lat_base + lat_step + lat_j[3]),
            (lon_base + lon_j[0], lat_base + lat_j[0])  # Close polygon
        ]
        
        polygons.append(Polygon(coords))
    
    return polygons, names

def generate_sample_data():
    """Generate complete sample dataset"""
    print("Generating sample neighbourhood data...")
    
    num_hoods = min(len(NEIGHBOURHOODS), 140)
    
    # Create geometries
    polygons, names = create_grid_polygons(num_hoods)
    
    # Create base GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'neighbourhood': names,
        'geometry': polygons
    }, crs="EPSG:4326")
    
    # Convert to UTM for area calculation
    gdf_utm = gdf.to_crs(epsg=26917)
    gdf['area_sqkm'] = gdf_utm.geometry.area / 1_000_000
    
    # Generate realistic features with correlations
    np.random.seed(42)
    
    # Population (5k to 50k)
    gdf['population'] = np.random.randint(5000, 50000, num_hoods)
    
    # Crime rate (per 1k) - higher in some areas
    base_crime = np.random.uniform(3, 25, num_hoods)
    gdf['crime_rate'] = base_crime
    
    # Transit access - inversely correlated with distance from center
    center_lat, center_lon = 43.65, -79.38
    gdf['dist_from_center'] = np.sqrt(
        (gdf.geometry.centroid.y - center_lat)**2 + 
        (gdf.geometry.centroid.x - center_lon)**2
    )
    
    # Stop density - higher near center, with noise
    max_dist = gdf['dist_from_center'].max()
    gdf['stop_density'] = (1 - gdf['dist_from_center'] / max_dist) * 12 + np.random.uniform(0, 3, num_hoods)
    gdf['stop_density'] = gdf['stop_density'].clip(0.5, 15)
    
    # Median distance to stop - inversely related to density
    gdf['median_stop_dist'] = 800 - (gdf['stop_density'] * 50) + np.random.uniform(-100, 100, num_hoods)
    gdf['median_stop_dist'] = gdf['median_stop_dist'].clip(100, 1000)
    
    # Stop count
    gdf['stop_count'] = (gdf['stop_density'] * gdf['area_sqkm']).astype(int)
    
    # Housing pressure (60-95%)
    housing_base = np.random.uniform(0.6, 0.95, num_hoods)
    # Slightly higher near center
    gdf['housing_pressure'] = housing_base + (1 - gdf['dist_from_center'] / max_dist) * 0.1
    gdf['housing_pressure'] = gdf['housing_pressure'].clip(0.6, 0.98)
    
    # 311 requests - correlated with population and crime
    gdf['request_count'] = (
        gdf['population'] * 0.08 + 
        gdf['crime_rate'] * 100 + 
        np.random.randint(-500, 500, num_hoods)
    ).astype(int)
    gdf['request_count'] = gdf['request_count'].clip(200, 8000)
    
    # Request rate per 1k
    gdf['request_rate'] = (gdf['request_count'] / gdf['population']) * 1000
    
    # Calculate attention score (from process_data.py logic)
    from scipy import stats
    
    gdf['crime_zscore'] = stats.zscore(gdf['crime_rate'])
    gdf['transit_access_zscore'] = -stats.zscore(gdf['stop_density'])
    gdf['transit_dist_zscore'] = stats.zscore(gdf['median_stop_dist'])
    gdf['housing_zscore'] = stats.zscore(gdf['housing_pressure'])
    gdf['demand_zscore'] = stats.zscore(gdf['request_rate'])
    
    weights = {
        'transit': 0.30,
        'housing': 0.25,
        'crime': 0.25,
        'demand': 0.20
    }
    
    gdf['attention_score'] = (
        weights['transit'] * (gdf['transit_access_zscore'] + gdf['transit_dist_zscore']) / 2 +
        weights['housing'] * gdf['housing_zscore'] +
        weights['crime'] * gdf['crime_zscore'] +
        weights['demand'] * gdf['demand_zscore']
    )
    
    # Normalize to 0-100
    min_score = gdf['attention_score'].min()
    max_score = gdf['attention_score'].max()
    gdf['attention_score_normalized'] = ((gdf['attention_score'] - min_score) / (max_score - min_score)) * 100
    
    # Remove helper columns
    gdf = gdf.drop(['dist_from_center'], axis=1)
    
    return gdf

def main():
    """Generate and save sample data"""
    # Generate data
    gdf = generate_sample_data()
    
    print(f"Generated {len(gdf)} neighbourhoods with complete features")
    
    # Save processed data
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gdf.to_file(output_dir / "neighbourhoods_analysis.geojson", driver="GeoJSON")
    
    # Save to public for Next.js
    public_dir = Path("public/data")
    public_dir.mkdir(parents=True, exist_ok=True)
    gdf.to_file(public_dir / "neighbourhoods_analysis.geojson", driver="GeoJSON")
    
    # Summary stats
    summary = {
        "total_neighbourhoods": len(gdf),
        "data_source": "Sample data (demo)",
        "data_quality": {
            "crime_coverage": 100.0,
            "transit_coverage": 100.0,
            "housing_coverage": 100.0,
            "service_coverage": 100.0
        },
        "top_attention_neighbourhoods": gdf.nlargest(10, 'attention_score_normalized')[
            ['neighbourhood', 'attention_score_normalized', 'crime_rate', 'stop_density', 
             'housing_pressure', 'request_rate']
        ].to_dict('records')
    }
    
    with open(output_dir / "summary_stats.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Sample data generated successfully!")
    print(f"  Output: {output_dir}/neighbourhoods_analysis.geojson")
    print(f"  Web data: {public_dir}/neighbourhoods_analysis.geojson")
    print(f"  Summary: {output_dir}/summary_stats.json")
    
    # Print top 10
    print("\nTop 10 Neighbourhoods by Attention Score:")
    top_10 = gdf.nlargest(10, 'attention_score_normalized')
    for idx, row in top_10.iterrows():
        print(f"  {row['neighbourhood']}: {row['attention_score_normalized']:.1f}")

if __name__ == "__main__":
    main()
