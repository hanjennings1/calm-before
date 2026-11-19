"""Import Census ZIP data: ZIP center points and ZIP-to-county links.

Run from server/ AFTER scripts.import_nri (counties must exist first):
    python -m scripts.import_census
"""

import csv
from collections import Counter
from pathlib import Path

from app import create_app
from models import db, County, Zip, ZipCounty

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
GAZETTEER_FILE = RAW_DIR / "2024_Gaz_zcta_national.txt"
RELATIONSHIP_FILE = RAW_DIR / "tab20_zcta520_county20_natl.txt"


def read_rows(path, delimiter):
    """Yield each row as a dict, with whitespace stripped from headers and values."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for row in reader:
            yield {key: (value or "").strip() for key, value in row.items()}


def import_zips():
    zips = []
    for row in read_rows(GAZETTEER_FILE, "\t"):
        if not row.get("GEOID"):
            continue    # skip blank lines
        zips.append(Zip(
            code=row["GEOID"],
            lat=float(row["INTPTLAT"]),
            lon=float(row["INTPTLONG"]),
        ))
    db.session.add_all(zips)
    return {z.code for z in zips}


def import_zip_counties(zip_codes):
    county_fips = {fips for (fips,) in db.session.query(County.fips)}
    links = []
    skipped = Counter()

    for row in read_rows(RELATIONSHIP_FILE, "|"):
        zip_code = row["GEOID_ZCTA5_20"]
        fips = row["GEOID_COUNTY_20"]

        if not zip_code:
            continue        # part of a county that isn't in any ZIP (lakes, forests)
        if zip_code not in zip_codes:
            skipped["ZIP not in gazetteer"] += 1
            continue
        if fips not in county_fips:
            skipped[f"county not in NRI (state {fips[:2]})"] += 1
            continue

        links.append(ZipCounty(
            zip_code=zip_code,
            county_fips=fips,
            land_area=int(row["AREALAND_PART"] or 0),
        ))

    db.session.add_all(links)
    return len(links), skipped


def main():
    app = create_app()
    with app.app_context():
        ZipCounty.query.delete()
        Zip.query.delete()
        zip_codes = import_zips()
        db.session.flush()  # ZIPs must exist before links reference them
        link_count, skipped = import_zip_counties(zip_codes)
        db.session.commit()

        print(f"Imported {len(zip_codes)} ZIPs and {link_count} ZIP-county links.")
        for reason, count in skipped.most_common():
            print(f" skipped {count}: {reason}")


if __name__ == "__main__":
    main()