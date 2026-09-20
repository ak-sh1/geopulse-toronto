# GeoPulse Toronto 🗺️

**Toronto neighbourhood analysis platform** — combines transit access, housing pressure, 311 service demand, and crime data to identify underserved areas using spatial data science.

**Live Demo:** [Deployed on Vercel] | **Author:** Akash Gupta (York University CS)

---

## 🎯 Decision Question

**Which Toronto neighbourhoods look underserved on transit access + housing pressure relative to 311 demand and reported crime — and where should a city analyst look first?**

This portfolio project delivers:
- ✅ **Python GeoPandas pipeline** (spatial joins + feature engineering)
- ✅ **Jupyter notebook** with full analysis
- ✅ **Decision memo** with top 10 priorities + caveats
- ✅ **Next.js interactive map** (5 choropleth layers, tooltips, ranking)
- ✅ **Vercel-ready deployment** (`npm run build` static export)

---

## 🚀 2-Minute Quick Start

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- Git

### Installation & Demo

```bash
# 1. Clone and setup Python environment
git clone https://github.com/ak-sh1/geopulse-toronto.git
cd geopulse-toronto
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Fetch Toronto Open Data and process
python scripts/fetch_data.py       # Downloads to data/raw/
python scripts/process_data.py     # Outputs to data/processed/ + public/data/

# 3. Launch web application
npm install
npm run dev

# Open http://localhost:3000
```

**What you'll see:**
- Interactive Leaflet map centered on Toronto (140 neighbourhoods)
- 5 switchable choropleth layers (attention score, crime, transit, housing, 311)
- Hover tooltips with neighbourhood details
- Real-time ranking table (top 10 per layer)
- Responsive legend

---

## 📊 Project Structure

```
geopulse-toronto/
├── app/                      # Next.js App Router
│   ├── page.tsx             # Main map interface
│   ├── layout.tsx           # App layout
│   └── globals.css          # Tailwind + Leaflet styles
├── components/
│   └── Map.tsx              # React Leaflet map component
├── data/
│   ├── raw/                 # Gitignored (download via fetch_data.py)
│   └── processed/           # Committed GeoJSON for demo
├── docs/
│   ├── decision_memo.md     # Top 10 neighbourhoods + caveats
│   └── top_neighbourhoods.json  # Exported from notebook
├── notebooks/
│   ├── geopulse_analysis.ipynb  # Full analysis workflow
│   └── *.png                # Generated visualizations
├── public/
│   └── data/                # Web-accessible GeoJSON
├── scripts/
│   ├── fetch_data.py        # Toronto Open Data CKAN fetcher
│   └── process_data.py      # GeoPandas spatial pipeline
├── package.json             # Node dependencies
├── requirements.txt         # Python dependencies
├── next.config.js           # Vercel static export config
└── README.md
```

---

## 🔬 Methodology

### Data Sources (City of Toronto Open Data)

| Dataset | Source | Use |
|---------|--------|-----|
| **Neighbourhoods** | Boundaries GeoJSON (140 polygons) | Base geography |
| **Crime** | TPS Major Crime Indicators | Rates per 1k residents |
| **Transit** | TTC GTFS (stops.txt) | Stop density + median distance |
| **Housing** | Neighbourhood profiles | Pressure indicators |
| **311** | Service requests CSV | Request rates per 1k |
| **Population** | Neighbourhood profiles | Rate normalization |

### Attention Score Calculation

**Composite weighted z-scores:**

```python
attention_score = (
    0.30 × (transit_access_zscore + transit_dist_zscore) / 2 +
    0.25 × housing_pressure_zscore +
    0.25 × crime_rate_zscore +
    0.20 × demand_rate_zscore
)
```

- **Higher score** → greater service need
- Normalized to 0-100 scale
- Z-scores ensure comparable units across indicators

### Spatial Processing
- All distances calculated in **EPSG:26917 (UTM Zone 17N)** for accuracy
- Spatial joins: `gpd.sjoin()` with `within` predicate
- Web display in **EPSG:4326 (WGS84)** for Leaflet compatibility
- Join coverage reported per layer (see `data/processed/summary_stats.json`)

---

## 🗺️ Web Application Features

### Interactive Map
- **5 Choropleth Layers:**
  1. 🎯 Attention Score (composite)
  2. 🚨 Crime Rate (per 1k)
  3. 🚇 Transit Stop Density (per km²)
  4. 🏠 Housing Pressure (%)
  5. 📞 311 Request Rate (per 1k)

### UI Components
- **Layer Selector:** Dropdown to switch views
- **Color Legend:** Dynamic scale per layer
- **Tooltips:** Hover for neighbourhood details
- **Ranking Table:** Top 10 list (updates with layer)
- **Responsive Design:** Works on desktop + mobile

### Tech Stack
- **Frontend:** Next.js 14 (App Router), React 18, TypeScript
- **Mapping:** React Leaflet 4.2, OpenStreetMap tiles
- **Styling:** Tailwind CSS
- **Deployment:** Vercel static export (`output: 'export'`)

---

## 📈 Analysis Outputs

### 1. Jupyter Notebook (`notebooks/geopulse_analysis.ipynb`)
- Data quality assessment
- Exploratory visualizations (distributions, correlations, maps)
- Top 10 priority neighbourhoods
- Methodological notes (MAUP, confounders, caveats)

### 2. Decision Memo (`docs/decision_memo.md`)
- Executive summary for city planners
- Tiered recommendations (Critical / High / Moderate attention)
- Key findings + spatial patterns
- Limitations (no causality, ecological fallacy, MAUP)
- Recommended actions (immediate + medium-term)

### 3. Processed Data (`data/processed/`)
- `neighbourhoods_analysis.geojson` — Full feature dataset
- `summary_stats.json` — Coverage + top neighbourhoods

---

## ⚠️ Caveats & Limitations

### Methodological
1. **MAUP (Modifiable Areal Unit Problem):** Results sensitive to neighbourhood boundaries
2. **Ecological Fallacy:** Aggregate patterns ≠ individual experiences
3. **Confounders:** Socioeconomic status, development history not controlled
4. **No Causality:** Descriptive analysis only, not predictive
5. **Temporal Mismatch:** Data sources reflect different periods

### Data Quality
- **Join Coverage:** Reported per layer (varies by dataset availability)
- **Missing Values:** Handled via median imputation
- **Sample Data:** If Toronto Open Data fetch fails, scripts generate labeled fallback data for demo purposes

### Appropriate Use
✅ **Good for:** Exploratory analysis, priority setting, hypothesis generation  
❌ **Not for:** Causal inference, policy evaluation, "best/worst" rankings

---

## 🛠️ Development Commands

```bash
# Python Environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Data Pipeline
python scripts/fetch_data.py       # Fetch Toronto Open Data
python scripts/process_data.py     # Process + spatial joins

# Jupyter Notebook
jupyter notebook notebooks/geopulse_analysis.ipynb

# Next.js Development
npm install
npm run dev                        # Dev server (http://localhost:3000)
npm run build                      # Production build (static export)
npm run start                      # Serve production build

# Deployment (Vercel)
vercel deploy --prod
```

---

## 📦 Deployment (Vercel)

This project is configured for **static export** (no server-side rendering required).

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ak-sh1/geopulse-toronto)

### Manual Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Vercel auto-detects Next.js and runs:
# - npm run build (generates static files in out/)
# - Serves from out/ directory
```

### Build Requirements
- **Build Command:** `npm run build`
- **Output Directory:** `out/`
- **Node Version:** 18.x or later
- **Environment Variables:** None required (static data)

---

## 🎓 Portfolio Highlights

### Technical Skills Demonstrated
- **Spatial Data Science:** GeoPandas, Shapely, CRS transformations
- **Data Engineering:** API integration (CKAN), ETL pipeline, GeoJSON processing
- **Statistical Analysis:** Z-score normalization, weighted composites, correlation analysis
- **Full-Stack Development:** Next.js 14 (App Router), TypeScript, React Leaflet
- **UI/UX Design:** Responsive layouts, interactive visualizations, accessible controls
- **Deployment:** Vercel static exports, GitHub Pages ready
- **Documentation:** Jupyter notebooks, decision memos, technical READMEs

### Project Management
- **Clear Decision Question:** Scoped to city planning use case
- **Reproducible Workflow:** 2-minute setup from clone to demo
- **Production-Ready:** Vercel deployment, error handling, data validation
- **Professional Standards:** Gitignore best practices, code organization, caveats documented

---

## 📚 Data Attributions

All data sourced from **City of Toronto Open Data Portal**:
- [Neighbourhoods](https://open.toronto.ca/dataset/neighbourhoods/)
- [Police Crime Statistics](https://open.toronto.ca/dataset/police-annual-statistical-report-major-crime-indicators/)
- [TTC Routes and Schedules](https://open.toronto.ca/dataset/ttc-routes-and-schedules/)
- [311 Service Requests](https://open.toronto.ca/dataset/311-service-requests-customer-initiated/)
- [Neighbourhood Profiles](https://open.toronto.ca/dataset/neighbourhood-profiles/)

**License:** City of Toronto data is available under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-license/).

---

## 🤝 Contributing

This is a portfolio project, but feedback is welcome!

- **Bug Reports:** Open an issue on GitHub
- **Feature Requests:** Suggest improvements via issues
- **Pull Requests:** Code contributions accepted for bug fixes

---

## 📧 Contact

**Akash Gupta**  
York University — Computer Science  
📧 [Email](mailto:akash@example.com)  
🔗 [GitHub](https://github.com/ak-sh1)  
🔗 [Portfolio](https://akashgupta.dev)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **City of Toronto Open Data Team** — for comprehensive public datasets
- **York University CS Department** — academic support
- **Open Source Community** — GeoPandas, Leaflet, Next.js contributors

---

## 🔮 Future Enhancements

Potential extensions for V2:
- [ ] Real-time 311 data sync via CKAN API polling
- [ ] Historical trend analysis (year-over-year comparison)
- [ ] Socioeconomic control variables (income, education)
- [ ] Machine learning for service demand prediction
- [ ] Mobile-first PWA with offline maps
- [ ] Multi-city support (Montreal, Vancouver)
- [ ] User-submitted service gap reports
- [ ] Integration with City dashboards

---

**Built with ❤️ in Toronto**
