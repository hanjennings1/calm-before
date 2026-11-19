# Calm Before

Know your local disaster risks and get ready before the storm.

> 🚧 **In progress.** MVP target: December 2026. This README grows as features ship.

Calm Before is a full-stack web app. Enter a US ZIP code to see active weather alerts, your county's biggest natural hazards, its history of federal disaster declarations, and a preparedness checklist built for the risks where you live.

---

## Why I built this

In September 2024, Hurricane Helene hit Upstate South Carolina, where I was living. We weren't expecting it to be that bad. We got through it because we happened to have camping supplies that kept us fed and warm. That was luck, not planning. I built this dashboard so anyone can type in their ZIP code and see their real local risks, what's happened in their county before, and exactly how to prepare before the next storm.

---

## Features

### MVP (in progress)

- [x] Backend health check (Flask + PostgreSQL)
- [x] React client connected to the API
- [x] Database of US counties, ZIP codes and county hazard risk (FEMA National Risk Index + Census data)
- [ ] ZIP code search: ZIP → county + coordinates
- [ ] Active weather alerts from the National Weather Service, color-coded by severity
- [ ] County risk profile: top hazards from FEMA's National Risk Index
- [ ] Disaster history: chart of FEMA disaster declarations by year and type
- [ ] Preparedness checklist tailored to the county's top hazards
- [ ] Map of the county with active alert areas

### Planned

- [ ] Accounts and saved locations (home, work, family)
- [ ] Alert notifications
- [ ] Offline mode (PWA) for the checklist and household plan
- [ ] Household emergency plan builder with PDF export
- [ ] Response mode: nearby shelters, food and clinics during an active disaster (connects to a planned companion Resource Finder app)

---

## Tech stack

| Layer | Tools |
| --- | --- |
| Frontend | React (Vite) |
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS |
| Database | PostgreSQL (Neon) |
| Testing | pytest |
| Hosting | Render (planned) |

Planned additions: React Router, Leaflet (maps), Recharts (charts), GitHub Actions (CI).

---

## Data sources

All data comes from free, public US government sources:

| Source | Used for |
| --- | --- |
| [National Weather Service API](https://www.weather.gov/documentation/services-web-api) | Active weather alerts |
| [OpenFEMA](https://www.fema.gov/about/openfema/developer-resources) | Federal disaster declaration history |
| [FEMA National Risk Index](https://www.fema.gov/about/openfema/data-sets/national-risk-index-data) v1.20 (December 2025) | County-level natural hazard risk for 18 hazards |
| US Census Bureau [ZCTA-to-County Relationship File](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.html) (2020) and [Gazetteer Files](https://www.census.gov/data/data-tools/gazetteer.html) (2024) | Mapping ZIP codes to counties and coordinates |
| [Ready.gov](https://www.ready.gov) | Preparedness checklist guidance |

This product uses the Federal Emergency Management Agency's National Risk Index dataset API or downloadable datasets but is not endorsed by FEMA.

---

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 20.19+
- A PostgreSQL database (this project uses [Neon](https://neon.tech)) with two databases: one for development and one for tests

### 1. Clone the repo

```bash
git clone https://github.com/hanjennings1/calm-before.git
cd calm-before
```

### 2. Set up the backend

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `server/.env` with your own values:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Development database URL, starting with `postgresql+psycopg://` |
| `TEST_DATABASE_URL` | Test database URL, starting with `postgresql+psycopg://` |
| `NWS_USER_AGENT` | App name and contact email, required by the NWS API, e.g. `(calm-before, you@example.com)` |

Create the database tables:

```bash
flask --app app db upgrade
```

### 3. Load the data

The raw data files aren't committed to the repo (about 60 MB). Download them into `server/data/raw/`:

| File | Where to get it |
| --- | --- |
| `NRI_Table_Counties.csv` and `NRI_HazardInfo.csv` | [FEMA National Risk Index data](https://www.fema.gov/about/openfema/data-sets/national-risk-index-data): **All Counties → Table Format**, then unzip |
| `tab20_zcta520_county20_natl.txt` | [Census 2020 relationship files](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.html): **ZIP Code Tabulation Areas → ZCTA5 to County** |
| `2024_Gaz_zcta_national.txt` | [Census Gazetteer Files](https://www.census.gov/data/data-tools/gazetteer.html): **2024 → ZIP Code Tabulation Areas**, then unzip |

Then run the import scripts from `server/`, **in this order** (counties must exist before ZIPs can link to them):

```bash
python -m scripts.import_nri       # 18 hazards, 3,232 counties, 58,176 county risks
python -m scripts.import_census    # 33,791 ZIPs, 46,660 ZIP-county links
```

Both scripts clear their tables before loading, so they're safe to re-run. Re-running `import_nri` also clears the ZIP-county links, so run `import_census` again afterward.

### 4. Start the API

```bash
flask --app app run --debug
```

The API runs at `http://localhost:5000`.

### 5. Set up the frontend

In a second terminal:

```bash
cd client
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

### 6. Run the tests

From `server/`:

```bash
pytest -v
```

---

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Checks that the API and database are reachable |

More endpoints are coming: location lookup, alerts, risk profile, disaster history and checklist.

---

## Project structure

```
calm-before/
├── client/              # React (Vite) frontend
│   └── src/
│       ├── api.js       # All API calls
│       └── App.jsx
└── server/              # Flask API
    ├── app.py           # App factory and routes
    ├── config.py        # Config and TestConfig
    ├── models.py        # Database models
    ├── migrations/      # Database migrations (Flask-Migrate)
    ├── data/raw/        # Downloaded data files (not committed)
    ├── services/        # NWS and OpenFEMA clients, caching
    ├── scripts/         # Data import and seed scripts
    └── tests/           # pytest tests
```

---

## Known limitations

- **Connecticut:** Connecticut ZIP codes don't yet show county risk or disaster history. In 2022, Connecticut replaced its counties with planning regions, and the Census ZIP-to-county file still uses the old counties. Weather alerts still work, because they use ZIP coordinates.
- **ZIP codes vs. ZCTAs:** ZIP lookups use Census ZIP Code Tabulation Areas (ZCTAs), which match nearly all residential ZIP codes. PO-box-only and some business ZIP codes aren't included.

---

## License

[MIT](LICENSE)