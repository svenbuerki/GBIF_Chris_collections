# Christopher Davidson's Collections on GBIF and Flora of the World

**Author:** Sven Buerki — Boise State University
**Date:** April 2026
**GBIF download:** [0000210-250515123054153](https://www.gbif.org/occurrence/download/0000210-250515123054153) (May 15, 2025)
**Citation:** GBIF.Org User (2025). Occurrence Download. https://doi.org/10.15468/DL.Q7X2GP

---

## Overview

This project investigates Christopher Davidson's plant collections available on
the [Global Biodiversity Information Facility (GBIF)](https://www.gbif.org/) and
determines which of those collections are also documented in the
[Flora of the World (FotW)](https://www.floraoftheworld.org/) database. The goals
are to curate FotW data, locate physical voucher specimens, link FotW occurrence
records to digitized herbarium data on GBIF, and retrieve specimen images from
the [PNW Herbaria portal](https://www.pnwherbaria.org/).

---

## Scripts

### 1. `FotW_on_GBIF.Rmd` — Full analysis (R)

The primary analysis document answering nine questions about Christopher Davidson's
GBIF occurrences and their overlap with FotW.

| | |
|---|---|
| **Run** | `rmarkdown::render("FotW_on_GBIF.Rmd")` |
| **Output** | `FotW_on_GBIF.html` |

**Inputs:**

| File | Description |
|---|---|
| `GBIF_data/0000210-250515123054153/occurrence.txt` | GBIF Darwin Core occurrences |
| `GBIF_data/0000210-250515123054153/multimedia.txt` | GBIF specimen image links |
| `GBIF_data/datasets_download_usage_0000210-250515123054153.tsv` | Dataset metadata |
| `FotW_DB/occurrences.csv` | FotW occurrence database |
| `Data_report/biodiveristy_terms_definitions.csv` | Vocabulary reference |
| `Data_report/occurrence_vs_voucher.csv` | Occurrence vs. voucher comparison |
| `Data_report/darwin_core_classes.csv` | Darwin Core class definitions |
| `Data_report/darwin_core_terms.csv` | Darwin Core term definitions |
| `Data_report/multimedia_extension_terms.csv` | Multimedia extension terms |
| `Figures/Screenshot 2025-05-15_GBIF.png` | GBIF query screenshot |

**Questions addressed:**

| Q | Question |
|---|---|
| Q1 | How many plant occurrences contributed by Christopher Davidson are on GBIF? |
| Q2 | Which institutions supply data to GBIF? |
| Q3 | Where are physical specimens deposited? |
| Q4 | Are digital images of physical specimens available online? |
| Q5 | How many unique collections are represented? |
| Q6 | How many taxa are represented and where do they occur? |
| Q7 | Can we retrieve other information (phenology, conservation status)? |
| Q8 | How can we link FotW images with SRP specimens? |
| Q9 | What is the overlap between GBIF and FotW? |

---

### 2. `FotW_on_GBIF_summary.Rmd` — Concise summary report (R)

A streamlined version of the full analysis that goes straight to answers,
formatted as GitHub-Flavored Markdown for use on the website.

| | |
|---|---|
| **Run** | `rmarkdown::render("FotW_on_GBIF_summary.Rmd")` |
| **Outputs** | `FotW_on_GBIF_summary.md`, `FotW_on_GBIF_summary.html` |

**Inputs:**

| File | Description |
|---|---|
| `GBIF_data/0000210-250515123054153/occurrence.txt` | GBIF Darwin Core occurrences |
| `GBIF_data/0000210-250515123054153/multimedia.txt` | GBIF specimen image links |
| `GBIF_data/datasets_download_usage_0000210-250515123054153.tsv` | Dataset metadata |
| `FotW_DB/occurrences.csv` | FotW occurrence database |

**Outputs:**

| File | Description |
|---|---|
| `FotW_on_GBIF_summary.md` | Markdown report (Q1–Q9 answers with tables) |
| `FotW_on_GBIF_summary.html` | HTML preview |
| `GBIF_FotW_matched_collections.csv` | All GBIF fields for occurrences matched to FotW |

---

### 3. `SRP_FotW_matching.Rmd` — SRP specimen matching (R)

Matches SRP (Boise State) specimens from the PNW Herbaria portal against the FotW
database using a four-step strategy, builds image URLs, and exports matched and
unmatched records.

| | |
|---|---|
| **Run** | `rmarkdown::render("SRP_FotW_matching.Rmd")` |
| **Outputs** | `SRP_FotW_matching.md`, `SRP_FotW_matching.html` |

**Inputs:**

| File | Description |
|---|---|
| `Consortium_PacificNorthWest_herbaria/CPNWH_20250520-112502.csv` | PNW Herbaria export of Davidson collections |
| `FotW_DB/occurrences.csv` | FotW occurrence database |

**Outputs:**

| File | Description |
|---|---|
| `SRP_FotW_matched_collections.csv` | 1,783 SRP specimens matched to FotW, with image URLs |
| `SRP_FotW_unmatched.csv` | 491 SRP FotW-flagged specimens with no FotW DB entry |
| `SRP_FotW_matching.md` | Markdown report with full code and results |
| `SRP_FotW_matching.html` | HTML preview |

---

### 4. `prepare_FotW_display.py` — Website display table (Python)

Produces a filtered, display-ready CSV for the FotW website. Selects the
highest-coverage Darwin Core fields, replaces GBIF null strings, adds a
`specimenImageURL` (PNW Herbaria URL for SRP specimens) and a `hasImage` flag.

| | |
|---|---|
| **Run** | `python3 prepare_FotW_display.py` |
| **Requires** | Python 3 (standard library only) |

**Inputs:**

| File | Description |
|---|---|
| `GBIF_FotW_matched_collections.csv` | Full GBIF fields for FotW-matched occurrences |
| `SRP_FotW_matched_collections.csv` | SRP specimens with PNW Herbaria image URLs |

**Output:**

| File | Description |
|---|---|
| `FotW_website_collections.csv` | 874 records, 29 display-ready columns (see below) |

**Columns in `FotW_website_collections.csv`:**

| Column | Darwin Core field | Coverage | Description |
|---|---|---|---|
| `gbifID` | `gbifID` | 100% | GBIF numeric identifier (snapshot — may change on re-index) |
| `gbifURL` | — | 100% | GBIF occurrence page (snapshot — may break on re-index) |
| `FotW_occurrenceID` | — | 100% | FotW database record ID |
| `occurrenceID` | `occurrenceID` | 100% | Globally unique specimen URI assigned by source institution |
| `institutionCode` | `institutionCode` | 100% | Herbarium acronym (MO, SRP, P …) |
| `ownerInstitutionCode` | `ownerInstitutionCode` | 97.5% | Parent institution |
| `catalogNumber` | `catalogNumber` | 99.7% | Specimen barcode / accession number |
| `basisOfRecord` | `basisOfRecord` | 100% | Always `PRESERVED_SPECIMEN` |
| `bibliographicCitation` | `bibliographicCitation` | 80.8% | Direct URL to specimen record at source institution (Tropicos, iDigBio, JSTOR …) |
| `acceptedScientificName` | `acceptedScientificName` | 100% | Accepted name with authorship |
| `family` | `family` | 99.7% | Family |
| `taxonRank` | `taxonRank` | 100% | Rank of the name |
| `taxonomicStatus` | `taxonomicStatus` | 100% | `ACCEPTED` or `SYNONYM` |
| `iucnRedListCategory` | `iucnRedListCategory` | 93.2% | Conservation status (LC, VU, EN …) |
| `recordedBy` | `recordedBy` | 100% | Collector name(s) |
| `recordNumber` | `recordNumber` | 100% | Collector field number |
| `eventDate` | `eventDate` | 100% | Collection date (YYYY-MM-DD) |
| `countryCode` | `countryCode` | 100% | ISO 3166-1 alpha-2 country code |
| `stateProvince` | `stateProvince` | 91.3% | State or province |
| `locality` | `locality` | 99.2% | Verbatim locality description |
| `decimalLatitude` | `decimalLatitude` | 99.3% | WGS84 latitude |
| `decimalLongitude` | `decimalLongitude` | 99.3% | WGS84 longitude |
| `elevation` | `elevation` | 93.5% | Elevation in metres |
| `mediaType` | `mediaType` | 30.7% | `StillImage` when a GBIF image exists |
| `license` | `license` | 100% | Reuse conditions (mostly CC BY-NC) |
| `rightsHolder` | `rightsHolder` | 99.5% | Institution to credit for image |
| `primarySpecimenURL` | — | **100%** | **Most stable available link** (see note below) |
| `specimenImageURL` | — | derived | PNW Herbaria image URL (SRP specimens only) |
| `hasImage` | — | derived | `Y` if `mediaType = StillImage` or `specimenImageURL` set |

> **`primarySpecimenURL` — link stability note**
>
> GBIF re-indexes its records periodically. The `gbifID` values are taken from a
> snapshot download (May 2025) and GBIF occurrence URLs **may stop resolving** after
> GBIF re-ingests the underlying datasets. Use `primarySpecimenURL` as the link
> to display on the website — it selects the most stable available identifier in
> this priority order:
>
> 1. `bibliographicCitation` — URL assigned by the holding herbarium (Tropicos, iDigBio,
>    JSTOR, …). Stable because the source institution controls it. **Coverage: 80.8%**
> 2. `occurrenceID` — globally unique URI assigned by the source institution
>    (e.g. `urn:catalog:MO:Tropicos:102569036`). Not a clickable URL but a persistent
>    identifier. Used for the remaining 19.2% of records.
> 3. `gbifURL` — fallback only. Not needed here (all 874 records resolved via steps 1–2),
>    but retained as a safety net for future downloads.
>
> The `gbifURL` column is kept for reference but **should not be the primary link on
> the website**. Re-download the GBIF data and re-run the full pipeline approximately
> once a year to keep all links fresh.

**Summary of `FotW_website_collections.csv`:**

| Metric | Value |
|---|---|
| Total records | **874** |
| Records with any image | **442** |
| — GBIF image (StillImage) | 268 |
| — SRP / PNW Herbaria URL | 203 |
| `primarySpecimenURL` filled | **874 (100%)** |
| — via `bibliographicCitation` | 706 (80.8%) |
| — via `occurrenceID` | 168 (19.2%) |

---

## Key findings

### GBIF occurrences (Q1–Q7)

| Metric | Value |
|---|---|
| Plant occurrences on GBIF | **26,562** |
| Unique field collections | **15,774** |
| Unique scientific names | **8,965** |
| Families | **402** |
| Species | **7,145** |
| Occurrences with digital images | **15,236 (57.4%)** |

**Data supplied by 63 datasets.** Main contributors: TROPICOS (18,328 combined)
and RSA - California Botanic Garden Herbarium (2,732). SRP (Boise State)
contributes 1,004 occurrences.

**Top institutions holding physical specimens:** MO (8,898), RSA (2,853),
NY (1,345), SRP (1,345), QCNE (831).

**Geographic scope:** 6 continents, 20+ countries. Top countries: United States
(5,911), Ecuador (5,891), Peru (4,638), Bolivia (2,766).

**Phenology:** ~3,400 occurrences have a recorded reproductive condition;
flowering specimens are most common (~2,100 records).

**Digital images:** 57.4% of occurrences have images on GBIF, mostly under
Creative Commons licenses (primarily CC BY-NC-SA 3.0). C. Davidson is listed as
rights holder for 405 images. SRP specimen images are not linked to GBIF — they
are accessible via the [PNW Herbaria portal](https://www.pnwherbaria.org/).

### GBIF–FotW overlap (Q9)

Records matched on a composite key: **numeric record number + collection date**
(e.g., `12687_2014-10-04`).

| Metric | Value |
|---|---|
| GBIF occurrences also in FotW | **874** |
| Unique FotW records represented | **474** |
| Matched records with any image | **442** |

**Top institutions:** MO (253), SRP (175), P — Paris (56), QCNE (49),
QCA (37), G — Geneva (33), SUVA — Fiji (30).

**Top countries:** Ecuador (233), United States (164), New Caledonia (136),
Fiji (121), Peru (65), Switzerland (50), Madagascar (47).

### SRP–FotW matching (Q8)

Of **2,278 SRP specimens** tagged as "Flora of the World" in the PNW Herbaria
portal (all imaged), matched using a four-step strategy:

| Metric | Value |
|---|---|
| Matched to a FotW record | **1,783** |
| — exact match (record number + date) | 636 |
| — record number unique in FotW | 1,064 |
| — fuzzy date match (≤3 days) | 86 |
| — closest date fallback (>3 days) | 24 |
| Not matched (number absent from FotW DB) | **491** |

The 491 unmatched specimens are all imaged and FotW-flagged; they are candidates
for a future FotW database update.

Specimen images follow the URL pattern:
```
https://www.pnwherbaria.org/images/jpeg.php?Image=SRP<ACCESSION>.jpg
```

---

## Repository structure

```
GBIF_Chris_collections/
│
├── README.md                                   # This file
│
├── Scripts (R)
│   ├── FotW_on_GBIF.Rmd                        # Full analysis (Q1–Q9)
│   ├── FotW_on_GBIF_summary.Rmd                # Concise summary (Q1–Q9)
│   └── SRP_FotW_matching.Rmd                   # SRP–FotW specimen matching
│
├── Scripts (Python)
│   └── prepare_FotW_display.py                 # Website display table
│
├── Rendered reports
│   ├── FotW_on_GBIF.html                       # Full analysis (HTML)
│   ├── FotW_on_GBIF_summary.md                 # Summary (Markdown)
│   ├── FotW_on_GBIF_summary.html               # Summary (HTML preview)
│   ├── SRP_FotW_matching.md                    # SRP matching (Markdown)
│   └── SRP_FotW_matching.html                  # SRP matching (HTML preview)
│
├── Output data
│   ├── GBIF_FotW_matched_collections.csv       # 874 GBIF occurrences in FotW (all fields)
│   ├── FotW_website_collections.csv            # 874 records, 28 display-ready columns
│   ├── SRP_FotW_matched_collections.csv        # 1,783 SRP specimens matched to FotW
│   └── SRP_FotW_unmatched.csv                  # 491 SRP FotW-flagged, no FotW DB entry
│
├── Input data (large files excluded — see Data setup below)
│   ├── GBIF_data/
│   │   └── 0000210-250515123054153/
│   │       ├── occurrence.txt                  # excluded (36 MB)
│   │       ├── verbatim.txt                    # excluded (23 MB)
│   │       ├── multimedia.txt                  # included (4.4 MB)
│   │       ├── citations.txt / rights.txt
│   │       ├── metadata.xml / meta.xml
│   │       └── dataset/                        # 80 dataset XMLs
│   │   └── datasets_download_usage_*.tsv
│   ├── FotW_DB/
│   │   ├── occurrences.csv                     # excluded (internal)
│   │   └── postgres_schema.csv
│   ├── Consortium_PacificNorthWest_herbaria/
│   │   └── CPNWH_20250520-112502.csv           # excluded (re-downloadable)
│   └── Data_report/                            # Darwin Core reference tables
│
└── Reference
    ├── Darwin_Core_FotW_May2025.xlsx
    ├── Bibliography_FotW.bib
    ├── AmJBot.csl
    └── Figures/
```

---

## Data setup

Three data sources are excluded from this repository (`.gitignore`) and must be
obtained separately before running the R scripts.

### 1. GBIF occurrence download

```
DOI: https://doi.org/10.15468/DL.Q7X2GP
URL: https://www.gbif.org/occurrence/download/0000210-250515123054153
```

Download and unzip into `GBIF_data/`. The files `occurrence.txt` (36 MB) and
`verbatim.txt` (23 MB) are excluded from git; all other files in the archive
are included.

### 2. Flora of the World database

Request `FotW_DB/occurrences.csv` from the FotW team. Expected columns:
`occurrenceID`, `recordNumber`, `family`, `genus`, `specificEpithet`,
`eventDate`, `country`, `stateProvince`, `locality`,
`decimalLatitude`, `decimalLongitude`, `recordedBy`.

### 3. PNW Herbaria export

Download Christopher Davidson's collections from the
[Consortium of Pacific Northwest Herbaria](https://www.pnwherbaria.org/) and
place the CSV at `Consortium_PacificNorthWest_herbaria/CPNWH_20250520-112502.csv`.
If you download a newer version, update the file path in `SRP_FotW_matching.Rmd`.

> **Note:** the CPNWH CSV contains embedded commas in quoted fields;
> `readr::read_csv` is used instead of base `read.csv` for reliable parsing.

---

## Methods

All analyses use the [Darwin Core](https://dwc.tdwg.org/) standard. GBIF data
were downloaded on May 15, 2025 using the following collector name variants in
the `Recorded by` field:
*DAVIDSON, CHRISTOPHER; C. DAVIDSON; Davidson C.; CHRISTOPHER DAVIDSON*.
Records were filtered to kingdom Plantae after download.

**FotW–GBIF matching** (`FotW_on_GBIF_summary.Rmd`): composite key =
numeric digits from `recordNumber` + date from `eventDate`.

**SRP–FotW matching** (`SRP_FotW_matching.Rmd`): four-step strategy applied
to 2,278 SRP records tagged `Dataset = "Flora of the World"`:

1. Exact key — `Collector Number` + `YYYY-MM-DD` matches FotW numeric record number + date
2. Unique number — record number appears under only one date in FotW
3. Fuzzy date — record number matches and dates differ by ≤3 days
4. Closest date — record number matches; nearest FotW date used as fallback

**Website display table** (`prepare_FotW_display.py`): selects 26 Darwin Core
fields, cleans GBIF null strings, and derives three additional columns:
`primarySpecimenURL` (most stable link: `bibliographicCitation` → `occurrenceID`
→ `gbifURL`), `specimenImageURL` (PNW Herbaria URL for SRP specimens), and
`hasImage` flag. Use `primarySpecimenURL` — not `gbifURL` — as the link on
the website; GBIF numeric IDs may change when GBIF re-indexes its datasets.

---

## Dependencies

**R packages:**
```r
install.packages(c("rmarkdown", "bookdown", "knitr", "kableExtra",
                   "dplyr", "readr", "DT", "formattable",
                   "DiagrammeR", "data.tree"))
```

**Python:** standard library only (csv, os, collections) — no packages to install.
