from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Consistent names for constraints (primary kets, foreign keys, etc)
# so Flask-Migrate can find and change them in later migrations:
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class County(db.Model):
    __tablename__ = "counties"

    fips = db.Column(db.String(5), primary_key=True)    # e.g. "45045" (text, keeps leading zeros)
    name = db.Column(db.String(100), nullable=False)    # e.g. "Greenville County"
    state = db.Column(db.String(2), nullable=False)     # e.g. "SC"
    risk_score = db.Column(db.Float)                    # NRI overall score (can be empty)
    risk_rating = db.Column(db.String(30))              # e.g. "Relatively Moderate"

    zip_links = db.relationship("ZipCounty", back_populates="county", cascade="all, delete-orphan")
    risks = db.relationship("CountyRisk", back_populates="county", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "fips": self.fips,
            "name": self.name,
            "state": self.state,
            "risk_score": self.risk_score,
            "risk_rating": self.risk_rating,
        }

    def __repr__(self):
        return f"<County {self.fips} {self.name}, {self.state}"


class Zip(db.Model):
    __tablename__ = "zips"

    code = db.Column(db.String(5), primary_key=True)   # e.g. "02891" (text, keeps leading zeros)
    lat = db.Column(db.Float, nullable=False)          # center point latitude
    lon = db.Column(db.Float, nullable=False)          # center point longitude

    county_links = db.relationship("ZipCounty", back_populates="zip_record", cascade="all, delete-orphan")

    def primary_county(self):
        """ The county containing most of this Zip Code's land"""
        if not self.county_links:
            return None
        return max(self.county_links, key=lambda link: link.land_area).county


    def to_dict(self):
        return {
            "zip": self.code,
            "lat": self.lat,
            "lon": self.lon,
        }

    def __repr__(self):
        return f"<Zip {self.code} ({self.lat}, {self.lon})"


class ZipCounty(db.Model):
    __tablename__ = "zip_counties"

    zip_code = db.Column(db.String(5), db.ForeignKey("zips.code"), primary_key=True)
    county_fips = db.Column(db.String(5), db.ForeignKey("counties.fips"), primary_key=True, index=True)
    land_area = db.Column(db.BigInteger, nullable=False)   # square meters of this ZIP inside this county

    zip_record = db.relationship("Zip", back_populates="county_links")
    county = db.relationship("County", back_populates="zip_links")

    def __repr__(self):
        return f"<ZipCounty {self.zip_code} -> {self.county_fips} ({self.land_area} m²)>"


class Hazard(db.Model):
    __tablename__ = "hazards"

    code = db.Column(db.String(4), primary_key=True)    # e.g. "HRCN"
    name = db.Column(db.String(50), nullable=False)     # e.g. "Hurricane"

    county_risks = db.relationship("CountyRisk", back_populates="hazard")

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
        }

    def __repr__(self):
        return f"<Hazard {self.code} {self.name}>"


class CountyRisk(db.Model):
    __tablename__  = "county_risks"

    county_fips = db.Column(db.String(5), db.ForeignKey("counties.fips"), primary_key=True)
    hazard_code = db.Column(db.String(4), db.ForeignKey("hazards.code"), primary_key=True)
    score = db.Column(db.Float)                 # 0–100 (can be empty)
    rating = db.Column(db.String(30))           # e.g. "Relatively High"

    county = db.relationship("County", back_populates="risks")
    hazard = db.relationship("Hazard", back_populates="county_risks")

    def to_dict(self):
        return {
            "hazard_code": self.hazard_code,
            "hazard_name": self.hazard.name,
            "score": self.score,
            "rating": self.rating,
        }

    def __repr__(self):
        return f"<CountyRisk {self.county_fips} {self.hazard_code}: {self.rating}>"