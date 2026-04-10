"""
prepare_FotW_display.py
=======================
Produces FotW_website_collections.csv — a filtered, display-ready table of
Christopher Davidson's GBIF occurrences that are also in the Flora of the World
(FotW) database.

Input files
-----------
GBIF_FotW_matched_collections.csv   -- GBIF occurrences matched to FotW (Q9)
SRP_FotW_matched_collections.csv    -- SRP specimens matched to FotW, with
                                       PNW Herbaria image URLs (Q8)

Output file
-----------
FotW_website_collections.csv        -- Selected Darwin Core fields + derived
                                       specimenImageURL and hasImage columns

Darwin Core fields selected
---------------------------
Group 1 – Specimen identity & physical location
  institutionCode       Herbarium acronym (MO, SRP, P …)
  ownerInstitutionCode  Parent institution (MOBOT, …)
  catalogNumber         Specimen barcode / accession number  ← key for images
  occurrenceID          Globally unique specimen URI
  basisOfRecord         Always PRESERVED_SPECIMEN here
  bibliographicCitation Direct URL to specimen record at source institution

Group 2 – GBIF link
  gbifURL               Direct link to the GBIF occurrence page
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
  specimenImageURL  PNW Herbaria image URL for SRP specimens; empty otherwise
  hasImage          Y if mediaType == StillImage or specimenImageURL is set
  FotW_occurrenceID Link back to the FotW database record
  gbifID            GBIF numeric identifier
"""

import csv
import os
from collections import defaultdict

# ── Paths ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
GBIF_FOTW  = os.path.join(BASE, "GBIF_FotW_matched_collections.csv")
SRP_FOTW   = os.path.join(BASE, "SRP_FotW_matched_collections.csv")
OUTPUT     = os.path.join(BASE, "FotW_website_collections.csv")

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
OUTPUT_FIELDS = DISPLAY_FIELDS + ["specimenImageURL", "hasImage"]


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


# ── 1. Build SRP image-URL lookup from SRP_FotW_matched_collections ───
# Index by FotW_occurrenceID (take first image URL per FotW record)
print("Loading SRP image URLs …")
srp_image_map = {}
with open(SRP_FOTW, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fid = row.get("FotW_occurrenceID", "").strip()
        url = row.get("SRP_imageURL", "").strip()
        if fid and url and fid not in srp_image_map:
            srp_image_map[fid] = url

print(f"  SRP image URLs indexed: {len(srp_image_map)}")

# ── 2. Process GBIF-FotW matched records ─────────────────────────────
print("Processing GBIF-FotW matched records …")
output_rows = []

with open(GBIF_FOTW, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        out = {field: clean(row.get(field, "")) for field in DISPLAY_FIELDS}

        inst     = out["institutionCode"]
        cat_num  = out["catalogNumber"]
        fotw_id  = out["FotW_occurrenceID"]

        # ── Derive specimenImageURL ──────────────────────────────────
        if inst == "SRP" and cat_num:
            # Build directly from GBIF catalog number
            out["specimenImageURL"] = srp_image_url(cat_num)
        elif fotw_id in srp_image_map:
            # Fallback: use SRP file match on FotW_occurrenceID
            out["specimenImageURL"] = srp_image_map[fotw_id]
        else:
            out["specimenImageURL"] = ""

        # ── hasImage flag ────────────────────────────────────────────
        out["hasImage"] = (
            "Y" if out["mediaType"] == "StillImage" or out["specimenImageURL"]
            else "N"
        )

        output_rows.append(out)

# ── 3. Write output ───────────────────────────────────────────────────
print("Writing output …")
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(output_rows)

# ── 4. Summary ────────────────────────────────────────────────────────
n = len(output_rows)
n_image      = sum(1 for r in output_rows if r["hasImage"] == "Y")
n_srp_img    = sum(1 for r in output_rows if r["specimenImageURL"])
n_gbif_img   = sum(1 for r in output_rows if r["mediaType"] == "StillImage")

from collections import Counter
inst_ct = Counter(r["institutionCode"] for r in output_rows)

print()
print("=" * 50)
print("OUTPUT SUMMARY")
print("=" * 50)
print(f"Total records:              {n}")
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
