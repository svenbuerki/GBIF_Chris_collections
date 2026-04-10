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

### 1. `FotW_on_GBIF.Rmd` — Full analysis

The primary analysis document answering nine questions about Christopher Davidson's
GBIF occurrences and their overlap with FotW.

| | |
|---|---|
| **Output** | `FotW_on_GBIF.html` |
| **Render** | `rmarkdown::render("FotW_on_GBIF.Rmd")` |

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

### 2. `FotW_on_GBIF_summary.Rmd` — Concise summary report

A streamlined version of the full analysis that goes straight to answers, formatted
as GitHub-Flavored Markdown for use on the website.

| | |
|---|---|
| **Outputs** | `FotW_on_GBIF_summary.md`, `FotW_on_GBIF_summary.html` |
| **Render** | `rmarkdown::render("FotW_on_GBIF_summary.Rmd")` |

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
| `GBIF_FotW_matched_collections.csv` | GBIF occurrences matched to FotW |

---

### 3. `SRP_FotW_matching.Rmd` — SRP specimen matching

Matches SRP (Boise State) specimens from the PNW Herbaria portal against the FotW
database, builds image URLs, and exports matched and unmatched records.

| | |
|---|---|
| **Outputs** | `SRP_FotW_matching.md`, `SRP_FotW_matching.html` |
| **Render** | `rmarkdown::render("SRP_FotW_matching.Rmd")` |

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

**Phenology:** ~3,400 occurrences have a recorded reproductive condition; flowering
specimens are most common (~2,100 records).

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
| Matched records with digital images | **270** |

**Top institutions:** MO (256), SRP (178), P — Paris (57), QCNE (49), QCA (37),
G — Geneva (33), SUVA — Fiji (31).

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

Specimen images are retrieved at:
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
├── Scripts
│   ├── FotW_on_GBIF.Rmd                        # Full analysis (Q1–Q9)
│   ├── FotW_on_GBIF_summary.Rmd                # Concise summary (Q1–Q9)
│   └── SRP_FotW_matching.Rmd                   # SRP–FotW specimen matching
│
├── Rendered reports
│   ├── FotW_on_GBIF.html                       # Full analysis (HTML)
│   ├── FotW_on_GBIF_summary.md                 # Summary (Markdown)
│   ├── FotW_on_GBIF_summary.html               # Summary (HTML preview)
│   ├── SRP_FotW_matching.md                    # SRP matching (Markdown)
│   └── SRP_FotW_matching.html                  # SRP matching (HTML preview)
│
├── Output data
│   ├── GBIF_FotW_matched_collections.csv       # 874 GBIF occurrences in FotW
│   ├── SRP_FotW_matched_collections.csv        # 1,783 SRP specimens matched to FotW
│   └── SRP_FotW_unmatched.csv                  # 491 SRP FotW-flagged, no FotW DB entry
│
├── Input data
│   ├── GBIF_data/
│   │   └── 0000210-250515123054153/
│   │       ├── occurrence.txt                  # GBIF occurrence records (36 MB)
│   │       ├── multimedia.txt                  # Specimen image links (4.4 MB)
│   │       ├── verbatim.txt                    # Raw verbatim data (23 MB)
│   │       ├── metadata.xml                    # Query metadata
│   │       ├── meta.xml                        # Field descriptions
│   │       └── dataset/                        # 80 individual dataset XMLs
│   │   └── datasets_download_usage_*.tsv       # Dataset metadata
│   ├── FotW_DB/
│   │   ├── occurrences.csv                     # FotW occurrence records (8.5 MB)
│   │   └── postgres_schema.csv                 # FotW database schema
│   ├── Consortium_PacificNorthWest_herbaria/
│   │   └── CPNWH_20250520-112502.csv           # PNW Herbaria Davidson collections
│   └── Data_report/                            # Darwin Core reference tables
│       ├── darwin_core_classes.csv
│       ├── darwin_core_terms.csv
│       ├── biodiveristy_terms_definitions.csv
│       ├── multimedia_extension_terms.csv
│       └── occurrence_vs_voucher.csv
│
├── Reference
│   ├── Darwin_Core_FotW_May2025.xlsx           # Darwin Core fields used in FotW
│   ├── Bibliography_FotW.bib                   # GBIF download citation
│   ├── AmJBot.csl                              # Citation style
│   └── Figures/
│       └── Screenshot 2025-05-15_GBIF.png      # GBIF query snapshot
│
└── GBIF_Chris_collections.Rproj               # RStudio project file
```

---

## Data setup

Three data sources are excluded from this repository (`.gitignore`) and must be
obtained separately before running the scripts.

### 1. GBIF occurrence download

Download the Darwin Core archive from GBIF and extract it into `GBIF_data/`:

```
DOI:  https://doi.org/10.15468/DL.Q7X2GP
URL:  https://www.gbif.org/occurrence/download/0000210-250515123054153
```

After downloading and unzipping, the directory should contain:

```
GBIF_data/
├── 0000210-250515123054153.zip          ← excluded (.gitignore)
└── 0000210-250515123054153/
    ├── occurrence.txt                   ← excluded (36 MB)
    ├── verbatim.txt                     ← excluded (23 MB)
    ├── multimedia.txt                   ← included (4.4 MB)
    ├── citations.txt
    ├── rights.txt
    ├── metadata.xml
    ├── meta.xml
    └── dataset/
└── datasets_download_usage_0000210-250515123054153.tsv
```

> `occurrence.txt` and `verbatim.txt` are excluded because they exceed GitHub's
> recommended file size. All other files in the archive are included.

### 2. Flora of the World database

Request `FotW_DB/occurrences.csv` from the FotW team. Place it at:

```
FotW_DB/occurrences.csv
```

Expected columns: `occurrenceID`, `recordNumber`, `family`, `genus`,
`specificEpithet`, `infraspecificEpithet`, `scientificNameAuthorship`,
`eventDate`, `country`, `stateProvince`, `county`, `municipality`, `locality`,
`decimalLatitude`, `decimalLongitude`, `recordedBy`.

### 3. PNW Herbaria export

Download Christopher Davidson's collections from the
[Consortium of Pacific Northwest Herbaria](https://www.pnwherbaria.org/) and
place the CSV at:

```
Consortium_PacificNorthWest_herbaria/CPNWH_20250520-112502.csv
```

The filename encodes the download date (`YYYYMMDD`). If you download a newer
version, update the file path in `SRP_FotW_matching.Rmd`.

---

## Methods

All analyses use the [Darwin Core](https://dwc.tdwg.org/) standard. GBIF data
were downloaded on May 15, 2025
([DOI: 10.15468/DL.Q7X2GP](https://doi.org/10.15468/DL.Q7X2GP)) using the
following collector name variants in the `Recorded by` field:
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

Note: the CPNWH CSV contains embedded commas in quoted fields; `readr::read_csv`
is used in place of base `read.csv` for reliable parsing.

---

## R packages required

```r
install.packages(c("rmarkdown", "bookdown", "knitr", "kableExtra",
                   "dplyr", "readr", "DT", "formattable",
                   "DiagrammeR", "data.tree"))
```
