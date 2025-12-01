# Input Data Sources

This directory contains the source datasets used for allocator analysis and demonstrations.

## 📊 Available Datasets

### Delhi Road Network (`delhi-roads-1k.csv`)
- **Source:** OpenStreetMap  
- **Location:** Delhi, India
- **Coverage:** 1,000 road segments
- **Geographic Bounds:** 28.414°-28.880°N, 76.870°-77.329°E
- **Road Types:** Primary, secondary, tertiary, trunk roads
- **Notable Roads:** Mahatma Gandhi Road, Outer Circle, Windsor Place, Grand Trunk Road

### Chonburi Road Network (`chonburi-roads-1k.csv`)
- **Source:** OpenStreetMap
- **Location:** Chonburi Province, Thailand  
- **Coverage:** 1,000 road segments
- **Geographic Bounds:** 12.623°-13.578°N, 100.867°-101.648°E
- **Road Types:** Primary, secondary, tertiary, trunk roads
- **Notable Roads:** Sukhumvit Road (ถนนสุขุมวิท), major highways and local roads

## 📋 Data Format

Both datasets follow this structure:

```csv
segment_id,osm_id,osm_name,osm_type,start_lat,start_long,end_lat,end_long
1,5873630,Mahatma Gandhi Road,primary,28.674,77.230,28.679,77.229
...
```

### Column Descriptions
- `segment_id`: Unique identifier for road segment
- `osm_id`: OpenStreetMap way ID
- `osm_name`: Road name (may be empty for unnamed roads)
- `osm_type`: Road classification (primary, secondary, tertiary, trunk)
- `start_lat`, `start_long`: Starting coordinates (WGS84)
- `end_lat`, `end_long`: Ending coordinates (WGS84)

## 🎯 Usage in Scripts

Scripts typically convert this road segment data into point datasets:

```python
import pandas as pd

# Load road data
roads = pd.read_csv('inputs/delhi-roads-1k.csv')

# Convert to analysis points (using start coordinates)
points = pd.DataFrame({
    'longitude': roads['start_long'],
    'latitude': roads['start_lat'],
    'segment_id': roads['segment_id'],
    'road_name': roads['osm_name'].fillna('Unnamed Road'),
    'road_type': roads['osm_type']
})
```

## 🌍 Real-World Applications

These datasets enable realistic analysis for:

- **Urban planning:** Road maintenance zone creation
- **Logistics:** Delivery route optimization  
- **Emergency services:** Response territory planning
- **Infrastructure:** Inspection scheduling
- **Transportation:** Public transit route design

## 📈 Data Quality

- **Completeness:** Both datasets provide comprehensive coverage of major urban areas
- **Accuracy:** Coordinates accurate to ~1 meter (OpenStreetMap quality)
- **Currency:** Data extracted from current OpenStreetMap database
- **Diversity:** Mix of road types from major highways to local streets

## 🔗 Source Attribution

Data sourced from [OpenStreetMap](https://www.openstreetmap.org/) under the [Open Database License](https://opendatacommons.org/licenses/odbl/).

© OpenStreetMap contributors