"""Import FEMA National Risk Index data: hazards, counties and county risks.

Run from server/:  python -m scripts.import_nri
"""

import csv
from pathlib import Path

from app import create_app
from models import db, County, Hazard, CountyRisk, ZipCounty

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
HAZARD_FILE = RAW_DIR / "NRI_HazardInfo.csv"
COUNTY_FILE = RAW_DIR / "NRI_Table_Counties.csv"

def to_float(value):
    """NRI leaves some scores blank; store as 'None' """
    value = (value or "").strip()
    return float(value) if value else None

def to_text(value):
    value = (value or "").strip()
    return value or None

def clear_tables():
    """Deletes in child-to-parent order so foreign keys don't block it."""
    ZipCounty.query.delete()
    CountyRisk.query.delete()
    County.query.delete()
    Hazard.query.delete()

def import_hazards():
    hazards = []
    with open(HAZARD_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            hazards.append(Hazard(code=row["Prefix"].strip(), name=row["Hazard"].strip()))
    db.session.add_all(hazards)
    return [h.code for h in hazards]

def import_counties_and_risks(hazard_codes):
    county_count = risk_count = 0
    with open(COUNTY_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            fips = row["STCOFIPS"].strip()
            db.session.add(County(
                fips=fips,
                name=f'{row["COUNTY"].strip()} {row["COUNTYTYPE"].strip()}'.strip(),
                state=row["STATEABBRV"].strip(),
                risk_score=to_float(row["RISK_SCORE"]),
                risk_rating=to_text(row["RISK_RATNG"]),
            ))
            county_count += 1

            for code in hazard_codes:
                db.session.add(CountyRisk(
                    county_fips=fips,
                    hazard_code=code,
                    score=to_float(row[f"{code}_RISKS"]),
                    rating=to_text(row[f"{code}_RISKR"]),
                ))
                risk_count += 1
    return county_count, risk_count

def main ():
    app =create_app()
    with app.app_context():
        clear_tables()
        hazard_codes = import_hazards()
        db.session.flush()  # hazards must exist before county_risks reference them
        county_count, risk_count = import_counties_and_risks(hazard_codes)
        db.session.commit()
        print(f"Imported {len(hazard_codes)} hazards, {county_count} counties, {risk_count} county risks.")

if __name__ == "__main__":
    main()