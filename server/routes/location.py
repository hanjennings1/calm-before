import re

from flask import Blueprint, jsonify

from models import db, Zip

location_bp = Blueprint("location", __name__)

ZIP_PATTERN = re.compile(r"^\d{5}$")        # exactly five digits, nothing else


@location_bp.get("/location/<zip_code>")
def get_location(zip_code):

    # 400: not a valid format:
    if not ZIP_PATTERN.match(zip_code):
        return jsonify(error="ZIP Code must be exactly 5 digits."), 400

    # 404: valid format, but not in the data
    zip_record = db.session.get(Zip, zip_code)
    if zip_record is None:
        return jsonify(error=f"ZIP Code {zip_code} not found."), 404

    # 200/OK: Counties (largest share of the Zip's land listed first)
    links = sorted(zip_record.county_links, key=lambda link: link.land_area, reverse=True)
    total_land = sum(link.land_area for link in links)

    counties = [
        {
            **link.county.to_dict(),
            "land_share": round(link.land_area / total_land, 3) if total_land else None,
        }
        for link in links
    ]

    return jsonify(
        zip=zip_record.code,
        lat=zip_record.lat,
        lon=zip_record.lon,
        primary_county=counties[0] if counties else None,
        counties=counties,
    ), 200
