# Calm Before

Know your local disaster risks and get ready before the storm.

> 🚧 **In progress.** MVP target: December 2026. This README grows as features ship.

**Calm Before is a full-stack web app. Enter a US ZIP code to see active weather alerts, your county's biggest natural hazards, its history of federal disaster declarations, and a preparedness checklist built for the risks where you live.**

---

## Why I built this

In September 2024, Hurricane Helene hit Upstate South Carolina, where I was living. We weren't expecting it to be that bad; we got through it because we happened to have camping supplies that kept us fed and warm. *That was luck, not planning.*
<br> I built this dashboard so anyone can type in their ZIP code and see their real local risks, what's happened in their county before, and exactly how to prepare before the next storm.

---

## Features

### MVP (in progress)

- [x] Backend health check (Flask + PostgreSQL)
- [x] React client connected to the API
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
| [FEMA National Risk Index](https://hazards.fema.gov/nri/data-resources) | County-level natural hazard risk |
| US Census Bureau [ZCTA-to-County Relationship File](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.html) and [Gazetteer Files](https://www.census.gov/data/data-tools/gazetteer.html) | Mapping ZIP codes to counties and coordinates || [Ready.gov](https://www.ready.gov) | Preparedness checklist guidance |
| [Ready.gov](https://www.ready.gov) | Preparedness checklist guidance |

*This product uses the Federal Emergency Management Agency's National Risk Index dataset API or downloadable datasets but is not endorsed by FEMA.*

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

Start the API:

```bash
flask --app app run --debug
```

The API runs at `http://localhost:5000`.

### 3. Set up the frontend

In a second terminal:

```bash
cd client
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

### 4. Run the tests

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
    ├── services/        # NWS and OpenFEMA clients, caching
    ├── scripts/         # Data import and seed scripts
    └── tests/           # pytest tests
```

---

## License

[MIT](LICENSE)