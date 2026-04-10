"""
prepare_FotW_display.py
=======================
Produces FotW_website_collections.csv — a merged, display-ready table of
Christopher Davidson's collections that are in the Flora of the World (FotW)
database, drawing from two sources:

  1. GBIF occurrences matched to FotW   (GBIF_FotW_matched_collections.csv)
  2. SRP specimens matched to FotW      (SRP_FotW_matched_collections.csv)
     — includes ~1,600 SRP specimens that are in FotW but not yet on GBIF

Input files
-----------
GBIF_FotW_matched_collections.csv   -- GBIF occurrences matched to FotW (Q9)
SRP_FotW_matched_collections.csv    -- SRP specimens matched to FotW, with
                                       PNW Herbaria image URLs (Q8)

Output file
-----------
FotW_website_collections.csv        -- Selected Darwin Core fields + derived
                                       columns (primarySpecimenURL, specimenImageURL,
                                       hasImage, source)

Source column
-------------
  GBIF   — record came from the GBIF download (may also have SRP image URL)
  SRP    — record came from SRP_FotW_matched_collections only (not on GBIF)

IMPORTANT — Link stability
--------------------------
GBIF re-indexes its records periodically. The `gbifID` and `gbifURL` values are
taken from a snapshot download (May 2025) and may no longer resolve after GBIF
re-ingests the underlying datasets. Do NOT use gbifURL as a permanent link on
the website.

Use `primarySpecimenURL` instead — a derived column that selects the most stable
available link in this priority order:
  1. bibliographicCitation  — URL to the specimen record at the source institution
                              (Tropicos, iDigBio, JSTOR, etc.). Stable because it
                              is assigned by the holding herbarium.
  2. occurrenceID           — Globally unique specimen URI assigned by the source
                              institution (e.g. urn:catalog:MO:Tropicos:102569036).
                              Not a clickable URL but a persistent identifier.
  3. specimenImageURL       — For SRP-only records: PNW Herbaria image URL used
                              as the best available clickable link.
  4. gbifURL                — Fallback only. May break if GBIF re-indexes.

Coordinate note (SRP source rows)
----------------------------------
In SRP_FotW_matched_collections.csv the coordinate columns are swapped relative
to their names:
  decimalLatitude  column  → actually contains longitude in DMS
                             (e.g. "114° 23' 47.5\" W")
  decimalLongitude column  → actually contains latitude in decimal degrees
The script corrects this on import.

Darwin Core fields selected
---------------------------
Group 1 – Specimen identity & physical location
  institutionCode       Herbarium acronym (MO, SRP, P …)
  ownerInstitutionCode  Parent institution (MOBOT, …)
  catalogNumber         Specimen barcode / accession number  ← key for images
  occurrenceID          Globally unique specimen URI (stable identifier)
  basisOfRecord         Always PRESERVED_SPECIMEN here
  bibliographicCitation Direct URL to specimen record at source institution

Group 2 – Links
  primarySpecimenURL    DERIVED: most stable available link (see above)
  gbifURL               GBIF occurrence page (snapshot — may break on re-index)
  mediaType             StillImage when a digitised image exists on GBIF
  license               Reuse conditions (mostly CC BY-NC)
  rightsHolder          Institution to credit for image

Group 3 – Collection event
  recordedBy            Collector name(s)
  recordNumber          Collector field number
  eventDate             Collection date (YYYY-MM-DD)

Group 4 – Location
  countryCode           ISO 3166-1 alpha-2 country code
  stateProvince         State / province
  locality              Verbatim locality description
  decimalLatitude       WGS84 latitude
  decimalLongitude      WGS84 longitude
  elevation             Elevation in metres

Group 5 – Taxonomy & conservation
  acceptedScientificName  Accepted name with authorship
  family
  taxonRank
  taxonomicStatus         ACCEPTED or SYNONYM
  iucnRedListCategory     LC, VU, EN, CR …

Derived columns
---------------
  primarySpecimenURL  Most stable link (see priority order above)
  specimenImageURL    Image URL: multimedia.txt identifier for GBIF records (when
                      hasImage=Y), PNW Herbaria URL for SRP specimens
  hasImage            Y if mediaType == StillImage or specimenImageURL is set
  source              GBIF or SRP (origin of the record)
  FotW_occurrenceID   Link back to the FotW database record
  gbifID              GBIF numeric identifier (snapshot — may change on re-index)
"""

import csv
import glob
import os
import re
from collections import Counter

# ── Paths ──────────────────────────────────────────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))
GBIF_FOTW  = os.path.join(BASE, "GBIF_FotW_matched_collections.csv")
SRP_FOTW   = os.path.join(BASE, "SRP_FotW_matched_collections.csv")
OUTPUT     = os.path.join(BASE, "FotW_website_collections.csv")

# multimedia.txt lives inside the versioned GBIF download subdirectory
_multimedia_matches = glob.glob(os.path.join(BASE, "GBIF_data", "*", "multimedia.txt"))
MULTIMEDIA = _multimedia_matches[0] if _multimedia_matches else None

# ── Darwin Core fields to keep ─────────────────────────────────────────
DISPLAY_FIELDS = [
    # Identifiers
    "gbifID",
    "gbifURL",
    "FotW_occurrenceID",
    "occurrenceID",
    # Physical specimen location
    "institutionCode",
    "ownerInstitutionCode",
    "catalogNumber",
    "basisOfRecord",
    "bibliographicCitation",
    # Taxonomy & conservation
    "acceptedScientificName",
    "family",
    "taxonRank",
    "taxonomicStatus",
    "iucnRedListCategory",
    # Collection event
    "recordedBy",
    "recordNumber",
    "eventDate",
    # Location
    "countryCode",
    "stateProvince",
    "locality",
    "decimalLatitude",
    "decimalLongitude",
    "elevation",
    # Image & rights
    "mediaType",
    "license",
    "rightsHolder",
]

# Final column order (display fields + derived)
OUTPUT_FIELDS = DISPLAY_FIELDS + ["primarySpecimenURL", "specimenImageURL", "hasImage", "source"]

# ── Country name → ISO 3166-1 alpha-2 mapping (SRP file uses full names) ──
COUNTRY_CODES = {
    "U.S.A.":                  "US",
    "Australia":               "AU",
    "Malaysia":                "MY",
    "E. Malaysia":             "MY",
    "Switzerland":             "CH",
    "South Africa":            "ZA",
    "Gabon":                   "GA",
    "Slovenia":                "SI",
    "Cameroon":                "CM",
    "Republic of Georgia":     "GE",
    "The Republic of Georgia": "GE",
    "China":                   "CN",
    "Costa Rica":              "CR",
    "Namibia":                 "NA",
    "Belize":                  "BZ",
    "Kenya":                   "KE",
    "Uganda":                  "UG",
    "Peru":                    "PE",
    "Spain":                   "ES",
    "Thailand":                "TH",
}


def clean(value):
    """Replace GBIF null strings with empty string."""
    return "" if value.strip() in ("NA", "na", "N/A", "null", "NULL") else value.strip()


def srp_image_url(catalog_number):
    """Build PNW Herbaria image URL from SRP catalog/accession number."""
    try:
        return (
            "https://www.pnwherbaria.org/images/jpeg.php?Image=SRP"
            + str(int(catalog_number)).zfill(6)
            + ".jpg"
        )
    except (ValueError, TypeError):
        return ""


def parse_dms(dms_str):
    """
    Parse a DMS coordinate string such as '114° 23' 47.5" W' into a signed
    decimal degree float.  Returns empty string on failure.
    W and S directions produce negative values.
    """
    m = re.search(
        r"(\d+)[°\s]+(\d+)['\s]+([0-9.]+)[\"'\s]*([NSEWnsew])",
        dms_str.replace("\\'", "'"),
    )
    if not m:
        return ""
    deg, minutes, sec, direction = m.groups()
    decimal = float(deg) + float(minutes) / 60 + float(sec) / 3600
    if direction.upper() in ("W", "S"):
        decimal = -decimal
    return f"{decimal:.6f}"


def srp_coords(lat_col, lon_col):
    """
    Return (latitude, longitude) as decimal-degree strings from the SRP file.

    The SRP file has two coordinate formats depending on the row:
      - DMS format: decimalLatitude column holds longitude in DMS
                    (e.g. '114° 23' 47.5" W'), decimalLongitude holds
                    latitude in decimal degrees.  Columns are swapped.
      - Decimal format: both columns are correctly named decimal degrees.

    Detection: if '°' appears in the latitude column → DMS / swapped.
    """
    if "°" in lat_col:
        # Swapped: lon_col is actual latitude, lat_col is DMS longitude
        return lon_col.strip(), parse_dms(lat_col)
    else:
        # Both decimal and correctly named
        return lat_col.strip(), lon_col.strip()


# ── 0. Load GBIF multimedia identifiers (gbifID → image URL) ──────────
print("Loading GBIF multimedia identifiers …")
gbif_image_url = {}  # gbifID (str) → identifier URL
if MULTIMEDIA:
    with open(MULTIMEDIA, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gid = row.get("gbifID", "").strip()
            url = row.get("identifier", "").strip()
            if gid and url and gid not in gbif_image_url:
                gbif_image_url[gid] = url
    print(f"  Multimedia entries loaded: {len(gbif_image_url)}")
else:
    print("  WARNING: multimedia.txt not found — GBIF image URLs will be empty")

# ── 1. Load SRP matched records ───────────────────────────────────────
print("Loading SRP matched records …")
srp_rows = []
with open(SRP_FOTW, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        srp_rows.append(row)

print(f"  SRP rows loaded: {len(srp_rows)}")

# ── 2. Process GBIF-FotW matched records ─────────────────────────────
print("Processing GBIF-FotW matched records …")
output_rows      = []
gbif_fotw_ids    = set()   # track FotW IDs already covered by GBIF rows

with open(GBIF_FOTW, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        out = {field: clean(row.get(field, "")) for field in DISPLAY_FIELDS}

        inst    = out["institutionCode"]
        cat_num = out["catalogNumber"]
        fotw_id = out["FotW_occurrenceID"]

        # Track FotW IDs covered by GBIF
        if fotw_id:
            gbif_fotw_ids.add(fotw_id)

        # ── specimenImageURL ─────────────────────────────────────────
        if inst == "SRP" and cat_num:
            out["specimenImageURL"] = srp_image_url(cat_num)
        else:
            # 1. Check multimedia.txt for a GBIF image URL
            gbif_id = out.get("gbifID", "").strip()
            out["specimenImageURL"] = gbif_image_url.get(gbif_id, "")
            # 2. Fall back to SRP matched file via FotW ID
            if not out["specimenImageURL"]:
                for srp in srp_rows:
                    if srp.get("FotW_occurrenceID", "").strip() == fotw_id and srp.get("SRP_imageURL", "").strip():
                        out["specimenImageURL"] = srp["SRP_imageURL"].strip()
                        break

        # ── primarySpecimenURL ───────────────────────────────────────
        out["primarySpecimenURL"] = (
            out["bibliographicCitation"]
            or out["occurrenceID"]
            or out["gbifURL"]
        )

        # ── hasImage ─────────────────────────────────────────────────
        out["hasImage"] = (
            "Y" if out["mediaType"] == "StillImage" or out["specimenImageURL"]
            else "N"
        )

        out["source"] = "GBIF"
        output_rows.append(out)

print(f"  GBIF rows processed: {len(output_rows)}")
print(f"  Unique FotW IDs covered by GBIF: {len(gbif_fotw_ids)}")

# ── 3. Add SRP-only rows (FotW IDs not in GBIF set) ──────────────────
print("Adding SRP-only records …")
n_srp_added = 0

for row in srp_rows:
    fotw_id = row.get("FotW_occurrenceID", "").strip()
    if fotw_id in gbif_fotw_ids:
        continue  # already represented by a GBIF row

    # Map SRP columns to Darwin Core output fields
    lat_decimal, lon_decimal = srp_coords(
        row.get("decimalLatitude",  ""),
        row.get("decimalLongitude", ""),
    )

    # Combine collector + otherCollectors
    collector       = row.get("collector", "").strip()
    other           = row.get("otherCollectors", "").strip()
    if other and other.upper() not in ("NA", "NULL", ""):
        recorded_by = collector + " | " + other
    else:
        recorded_by = collector

    country_name = row.get("country", "").strip()
    country_code = COUNTRY_CODES.get(country_name, "")

    image_url = row.get("SRP_imageURL", "").strip()
    accession = row.get("SRP_accession", "").strip()

    out = {f: "" for f in DISPLAY_FIELDS}
    out["gbifID"]                = ""
    out["gbifURL"]               = ""
    out["FotW_occurrenceID"]     = fotw_id
    out["occurrenceID"]          = row.get("SRP_occurrenceID", "").strip()
    out["institutionCode"]       = "SRP"
    out["ownerInstitutionCode"]  = "Boise State University"
    out["catalogNumber"]         = accession
    out["basisOfRecord"]         = "PRESERVED_SPECIMEN"
    out["bibliographicCitation"] = ""
    out["acceptedScientificName"]= row.get("scientificName_SRP", "").strip()
    out["family"]                = row.get("family", "").strip()
    out["taxonRank"]             = ""
    out["taxonomicStatus"]       = ""
    out["iucnRedListCategory"]   = ""
    out["recordedBy"]            = recorded_by
    out["recordNumber"]          = row.get("collectorNumber", "").strip()
    out["eventDate"]             = row.get("eventDate_SRP", "").strip()
    out["countryCode"]           = country_code
    out["stateProvince"]         = row.get("stateProvince", "").strip()
    out["locality"]              = row.get("locality", "").strip()
    out["decimalLatitude"]       = lat_decimal
    out["decimalLongitude"]      = lon_decimal
    out["elevation"]             = ""
    out["mediaType"]             = "StillImage"
    out["license"]               = ""
    out["rightsHolder"]          = "SRP / Boise State University"
    out["specimenImageURL"]      = image_url
    out["primarySpecimenURL"]    = image_url or out["occurrenceID"]
    out["hasImage"]              = "Y"
    out["source"]                = "SRP"

    output_rows.append(out)
    gbif_fotw_ids.add(fotw_id)   # prevent duplicate FotW IDs from multiple SRP rows
    n_srp_added += 1

print(f"  SRP-only rows added: {n_srp_added}")

# ── 4. Write output ───────────────────────────────────────────────────
print("Writing output …")
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(output_rows)

# ── 5. Summary ────────────────────────────────────────────────────────
n          = len(output_rows)
n_image    = sum(1 for r in output_rows if r["hasImage"] == "Y")
n_srp_img  = sum(1 for r in output_rows if r["specimenImageURL"])
n_gbif_img = sum(1 for r in output_rows if r["mediaType"] == "StillImage" and r["source"] == "GBIF")
n_gbif_src = sum(1 for r in output_rows if r["source"] == "GBIF")
n_srp_src  = sum(1 for r in output_rows if r["source"] == "SRP")
inst_ct    = Counter(r["institutionCode"] for r in output_rows)

print()
print("=" * 50)
print("OUTPUT SUMMARY")
print("=" * 50)
print(f"Total records:              {n}")
print(f"  – from GBIF:              {n_gbif_src}")
print(f"  – SRP-only (not on GBIF): {n_srp_src}")
print(f"Records with any image:     {n_image}")
print(f"  – GBIF image (StillImage):  {n_gbif_img}")
print(f"  – SRP / PNW Herbaria URL:   {n_srp_img}")
print()
print("Records by institution:")
for inst, count in inst_ct.most_common():
    label = inst if inst else "Unknown"
    print(f"  {label:<12} {count}")
print()
print(f"Output saved to: {OUTPUT}")
