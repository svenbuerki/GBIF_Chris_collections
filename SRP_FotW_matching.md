Matching SRP specimens with Flora of the World
================
Sven Buerki - Boise State University
2026-04-09

- [Overview](#overview)
- [Step 1 — Load and inspect source
  data](#step-1--load-and-inspect-source-data)
- [Step 2 — Prepare SRP matching keys and image
  URLs](#step-2--prepare-srp-matching-keys-and-image-urls)
- [Step 3 — Four-step matching
  strategy](#step-3--four-step-matching-strategy)
- [Step 4 — Results](#step-4--results)
- [Step 5 — Export](#step-5--export)
- [Image URL example](#image-url-example)

## Overview

This report documents the matching of SRP (Snake River Plain Herbarium,
Boise State University) specimens from the [Consortium of Pacific
Northwest Herbaria](https://www.pnwherbaria.org/) against occurrence
records in the Flora of the World (FotW) database.

**Data sources:**

- `Consortium_PacificNorthWest_herbaria/CPNWH_20250520-112502.csv` — PNW
  Herbaria export of Christopher Davidson collections
- `FotW_DB/occurrences.csv` — FotW occurrence database

**Goal:** Identify which SRP specimens are in FotW, link them to their
FotW occurrence ID, and build direct image URLs for each specimen.

------------------------------------------------------------------------

## Step 1 — Load and inspect source data

### FotW occurrences

``` r
FotW_data <- read.csv("FotW_DB/occurrences.csv", stringsAsFactors = FALSE)

# Extract numeric-only record number and date-only from eventDate
FotW_data$recordNumberFormatted <- gsub("[^0-9]", "", FotW_data$recordNumber)
FotW_data$eventDateFormatted    <- sapply(
  strsplit(FotW_data$eventDate, " "), `[[`, 1)

# Build composite matching key: "recordNumber_date"
FotW_data$match_key <- paste(
  FotW_data$recordNumberFormatted,
  FotW_data$eventDateFormatted,
  sep = "_")

cat("FotW records:               ", nrow(FotW_data), "\n")
```

    ## FotW records:                52264

``` r
cat("FotW unique matchable keys: ", length(unique(FotW_data$match_key[
  FotW_data$recordNumberFormatted != "" & FotW_data$eventDateFormatted != ""])), "\n")
```

    ## FotW unique matchable keys:  11958

### CPNWH — SRP specimens tagged as Flora of the World

The `Dataset` field in the CPNWH export flags records that belong to the
FotW project. We filter to `Herbarium == "SRP"` and
`Dataset == "Flora of the World"`.

``` r
# readr::read_csv handles embedded commas and complex quoting robustly
cpnwh <- read_csv(
  "Consortium_PacificNorthWest_herbaria/CPNWH_20250520-112502.csv",
  show_col_types = FALSE)
cpnwh <- as.data.frame(cpnwh)

# Overview of herbaria in the file
kable(as.data.frame(table(cpnwh$Herbarium)),
      col.names = c("Herbarium", "N records"),
      caption = "Records per herbarium in the CPNWH export.")
```

| Herbarium | N records |
|:----------|----------:|
| CIC       |        43 |
| EWU       |         1 |
| ID        |       287 |
| IDE       |         1 |
| IDS       |       101 |
| LEA       |        36 |
| MONT      |         7 |
| MONTU     |         2 |
| MORA      |         8 |
| NY        |         4 |
| OSC       |       292 |
| SRP       |      3163 |
| UBC       |      3787 |
| V         |        31 |
| WCW       |       531 |
| WS        |        52 |
| WTU       |       123 |

Records per herbarium in the CPNWH export.

``` r
srp_fotw <- cpnwh[cpnwh$Herbarium == "SRP" &
                  cpnwh$Dataset   == "Flora of the World", ]

cat("SRP records in CPNWH:               ", sum(cpnwh$Herbarium == "SRP"), "\n")
```

    ## SRP records in CPNWH:                3163

``` r
cat("SRP records tagged as FotW:         ", nrow(srp_fotw), "\n")
```

    ## SRP records tagged as FotW:          3160

``` r
cat("SRP FotW records with images (Y):   ",
    sum(srp_fotw$`Imaged?` == "Y"), "\n")
```

    ## SRP FotW records with images (Y):    NA

------------------------------------------------------------------------

## Step 2 — Prepare SRP matching keys and image URLs

``` r
# Zero-pad day and month to 2 digits, build ISO date
srp_fotw$day   <- formatC(as.integer(srp_fotw$`Day Collected`),
                           width = 2, flag = "0")
srp_fotw$month <- formatC(as.integer(srp_fotw$`Month Collected`),
                           width = 2, flag = "0")
srp_fotw$year  <- srp_fotw$`Year Collected`

srp_fotw$eventDate_SRP <- paste(srp_fotw$year, srp_fotw$month,
                                srp_fotw$day, sep = "-")

# Composite key: collector number + date
srp_fotw$match_key_SRP <- paste(srp_fotw$`Collector Number`,
                                srp_fotw$eventDate_SRP, sep = "_")

# Build PNW Herbaria image URL (accession zero-padded to 6 digits)
srp_fotw$SRP_imageURL <- paste0(
  "https://www.pnwherbaria.org/images/jpeg.php?Image=SRP",
  formatC(as.integer(srp_fotw$Accession), width = 6, flag = "0"),
  ".jpg")
```

------------------------------------------------------------------------

## Step 3 — Four-step matching strategy

Records are matched on a composite key: **numeric collector number +
collection date** (e.g., `14134_2021-06-01`). Because dates sometimes
differ slightly between databases (data entry or timezone offsets), we
apply four steps in order of decreasing confidence:

| Step | Strategy | Rationale |
|----|----|----|
| 1 | Exact key (number + date) | Highest confidence |
| 2 | Record number unique in FotW | Only one possible FotW date for that number |
| 3 | Fuzzy date match (≤3 days) | Small entry or timezone discrepancy |
| 4 | Closest date fallback | Best available match when gap \>3 days |

``` r
# ── Pre-compute FotW lookup structures ───────────────────────────────
# Exact key lookup
fotw_exact <- split(FotW_data, FotW_data$match_key)

# Record-number-only lookup
fotw_by_num <- split(FotW_data, FotW_data$recordNumberFormatted)

# ── Apply four-step matching ──────────────────────────────────────────
matched_list   <- vector("list", nrow(srp_fotw))
unmatched_list <- vector("list", nrow(srp_fotw))

for (i in seq_len(nrow(srp_fotw))) {
  row        <- srp_fotw[i, ]
  cn         <- trimws(row$`Collector Number`)
  date_srp   <- row$eventDate_SRP
  exact_key  <- row$match_key_SRP
  fotw_match <- NULL
  method     <- "unmatched"

  # Step 1 — exact key
  if (!is.null(fotw_exact[[exact_key]])) {
    fotw_match <- fotw_exact[[exact_key]]
    method     <- "exact"

  } else if (nchar(cn) > 0 && !is.null(fotw_by_num[[cn]])) {
    candidates  <- fotw_by_num[[cn]]
    fotw_dates  <- unique(candidates$eventDateFormatted)

    # Step 2 — unique record number
    if (length(fotw_dates) == 1) {
      fotw_match <- candidates
      method     <- "num_only_unique_date"

    } else if (nchar(date_srp) == 10) {
      srp_dt    <- as.Date(date_srp)
      cand_dts  <- as.Date(candidates$eventDateFormatted)
      day_diffs <- abs(as.integer(cand_dts - srp_dt))

      # Step 3 — fuzzy date ≤3 days
      close <- candidates[day_diffs <= 3, ]
      if (nrow(close) > 0) {
        fotw_match <- close
        method     <- "fuzzy_date_<=3d"
      } else {
        # Step 4 — closest date
        fotw_match <- candidates[which.min(day_diffs), ]
        method     <- "closest_date"
      }
    }
  }

  if (!is.null(fotw_match) && nrow(fotw_match) > 0) {
    # One output row per FotW match
    for (j in seq_len(nrow(fotw_match))) {
      fm <- fotw_match[j, ]
      matched_list[[i]] <- rbind(matched_list[[i]], data.frame(
        SRP_occurrenceID    = row$OccurrenceID,
        SRP_accession       = row$Accession,
        SRP_imageURL        = row$SRP_imageURL,
        matchMethod         = method,
        scientificName_SRP  = row$`Accepted Name`,
        family              = row$Family,
        collectorNumber     = cn,
        eventDate_SRP       = date_srp,
        collector           = row$Collector,
        otherCollectors     = row$`Other Collectors`,
        country             = row$Country,
        stateProvince       = row$`State or Province`,
        county              = row$County,
        locality            = row$Locality,
        decimalLatitude     = row$`Decimal Latitude`,
        decimalLongitude    = row$`Decimal Longitude`,
        phenology           = row$Phenology,
        FotW_occurrenceID   = fm$occurrenceID,
        scientificName_FotW = paste(fm$genus, fm$specificEpithet),
        FotW_eventDate      = fm$eventDateFormatted,
        FotW_recordNumber   = fm$recordNumber,
        FotW_recordedBy     = fm$recordedBy,
        stringsAsFactors    = FALSE
      ))
    }
  } else {
    unmatched_list[[i]] <- data.frame(
      SRP_occurrenceID   = row$OccurrenceID,
      SRP_accession      = row$Accession,
      SRP_imageURL       = row$SRP_imageURL,
      scientificName_SRP = row$`Accepted Name`,
      family             = row$Family,
      collectorNumber    = cn,
      eventDate_SRP      = date_srp,
      collector          = row$Collector,
      otherCollectors    = row$`Other Collectors`,
      country            = row$Country,
      stateProvince      = row$`State or Province`,
      county             = row$County,
      locality           = row$Locality,
      decimalLatitude    = row$`Decimal Latitude`,
      decimalLongitude   = row$`Decimal Longitude`,
      phenology          = row$Phenology,
      note               = "collector_number_not_in_FotW_DB",
      stringsAsFactors   = FALSE
    )
  }
}

matched   <- do.call(rbind, matched_list)
unmatched <- do.call(rbind, unmatched_list)

# Remove duplicate rows (same SRP + FotW pair)
matched <- matched[!duplicated(
  paste(matched$SRP_occurrenceID, matched$FotW_occurrenceID)), ]
```

------------------------------------------------------------------------

## Step 4 — Results

### Summary

``` r
n_srp_fotw   <- nrow(srp_fotw)
n_matched    <- length(unique(matched$SRP_occurrenceID))
n_unmatched  <- nrow(unmatched)
n_output     <- nrow(matched)

method_tbl <- as.data.frame(table(matched$matchMethod))
colnames(method_tbl) <- c("Match method", "N output rows")

summary_tbl <- data.frame(
  Metric = c(
    "SRP specimens tagged as FotW (all imaged)",
    "Matched to a FotW record",
    "Not matched (collector number absent from FotW DB)",
    "Output rows (including multi-FotW links)"),
  Value = c(n_srp_fotw, n_matched, n_unmatched, n_output))

kable(summary_tbl, col.names = c("Metric", "Value"), row.names = FALSE)
```

| Metric                                             | Value |
|:---------------------------------------------------|------:|
| SRP specimens tagged as FotW (all imaged)          |  3160 |
| Matched to a FotW record                           |  1779 |
| Not matched (collector number absent from FotW DB) |  1377 |
| Output rows (including multi-FotW links)           |  1806 |

### Match method breakdown

``` r
kable(method_tbl, row.names = FALSE)
```

| Match method         | N output rows |
|:---------------------|--------------:|
| closest_date         |            24 |
| exact                |           633 |
| fuzzy_date\_\<=3d    |            86 |
| num_only_unique_date |          1063 |

### Matched specimens by family

``` r
fam_tbl <- as.data.frame(
  sort(table(matched$family), decreasing = TRUE)[1:20])
colnames(fam_tbl) <- c("Family", "N matched")
kable(fam_tbl, row.names = FALSE,
      caption = "Top 20 families in matched SRP–FotW specimens.")
```

| Family          | N matched |
|:----------------|----------:|
| Asteraceae      |       132 |
| Fabaceae        |        77 |
| Plantaginaceae  |        74 |
| Brassicaceae    |        72 |
| Rosaceae        |        58 |
| Ranunculaceae   |        56 |
| Polemoniaceae   |        54 |
| Orobanchaceae   |        48 |
| Piperaceae      |        47 |
| Polygonaceae    |        47 |
| Apiaceae        |        43 |
| Boraginaceae    |        39 |
| Ericaceae       |        36 |
| Caryophyllaceae |        34 |
| Lamiaceae       |        34 |
| Onagraceae      |        29 |
| Hydrophyllaceae |        28 |
| Orchidaceae     |        28 |
| Saxifragaceae   |        26 |
| Cyperaceae      |        23 |

Top 20 families in matched SRP–FotW specimens.

### Matched specimens by state/province

``` r
state_tbl <- as.data.frame(
  sort(table(matched$stateProvince), decreasing = TRUE))
colnames(state_tbl) <- c("State / Province", "N matched")
kable(state_tbl, row.names = FALSE,
      caption = "Matched specimens by state or province.")
```

| State / Province                         | N matched |
|:-----------------------------------------|----------:|
| Idaho                                    |       710 |
| California                               |       235 |
| Western Australia                        |        91 |
| Oregon                                   |        86 |
| Sabah                                    |        85 |
| Arizona                                  |        74 |
| Western Cape                             |        65 |
| Valais                                   |        54 |
| Southwest Province                       |        43 |
| Estuaire                                 |        41 |
| Queensland                               |        36 |
| La Selva                                 |        25 |
| Texas                                    |        25 |
| Moyen-Ogooue                             |        23 |
| Notranjska / Inner Carniola              |        23 |
| Sichuan                                  |        22 |
| Gorenjska                                |        19 |
| Ajara Autonomous Republic                |        16 |
| Vaud                                     |        15 |
| Štajerska / Styria                       |        11 |
| Bern                                     |        10 |
| Nevada                                   |        10 |
| Kakheti Region (Historical Prov. Kiziki) |         7 |
| Mtskheta-Mtianeti Region                 |         7 |
| North Carolina                           |         5 |
| Yunnan                                   |         5 |
| Kunene                                   |         4 |
| Ajar Autonomous Republic                 |         3 |
| Guria Region                             |         3 |
| Samtskhe-Javakheti Region                |         3 |
| Hawaii                                   |         2 |
| Huánuco                                  |         2 |
| Jugovzhodna Slovenija                    |         2 |
| Missouri                                 |         2 |
| Northern Cape                            |         2 |
| Podravska                                |         2 |
| Primorska / Slovenian Littoral           |         2 |
| Washington                               |         2 |
| Ajara Autonomoius Republic               |         1 |
| Ajara Autonomous Region                  |         1 |
| Ajara Autonomous Rerpublic               |         1 |
| Andalucia                                |         1 |
| Chaiyaphum                               |         1 |
| Kakheti Region                           |         1 |
| Kakheti Region (Historical Prov. Kiziki) |         1 |
| Kakheti Region (Historical Prov. Kiziki  |         1 |
| Kakheti Region (historical Prov. Kiziki) |         1 |
| Kakheti Region (Kiziki)                  |         1 |
| Khomas                                   |         1 |
| KuneneRegion                             |         1 |
| Mtshkheta-Mtianeti Region                |         1 |
| Mtskheta-Mtianeti Reion                  |         1 |
| Ngounie                                  |         1 |
| Samtske-Javakheti Region                 |         1 |
| Shaanxi                                  |         1 |

Matched specimens by state or province.

### Unmatched specimens — top families

``` r
unfam_tbl <- as.data.frame(
  sort(table(unmatched$family), decreasing = TRUE)[1:20])
colnames(unfam_tbl) <- c("Family", "N unmatched")
kable(unfam_tbl, row.names = FALSE,
      caption = "Top 20 families among unmatched SRP specimens (not yet in FotW DB).")
```

| Family          | N unmatched |
|:----------------|------------:|
| Asteraceae      |          51 |
| Brassicaceae    |          22 |
| Piperaceae      |          20 |
| Plantaginaceae  |          19 |
| Fabaceae        |          17 |
| Rosaceae        |          16 |
| Ranunculaceae   |          15 |
| Polemoniaceae   |          13 |
| Hydrophyllaceae |          12 |
| Cyperaceae      |          11 |
| Boraginaceae    |          10 |
| Lamiaceae       |          10 |
| Onagraceae      |          10 |
| Orobanchaceae   |          10 |
| Polygonaceae    |          10 |
| Apiaceae        |           9 |
| Ericaceae       |           8 |
| Saxifragaceae   |           8 |
| Asparagaceae    |           7 |
| Campanulaceae   |           7 |

Top 20 families among unmatched SRP specimens (not yet in FotW DB).

------------------------------------------------------------------------

## Step 5 — Export

``` r
write.csv(matched,
          "SRP_FotW_matched_collections.csv",
          row.names = FALSE)

write.csv(unmatched,
          "SRP_FotW_unmatched.csv",
          row.names = FALSE)

cat("Exported:\n")
```

    ## Exported:

``` r
cat("  SRP_FotW_matched_collections.csv  —", nrow(matched), "rows\n")
```

    ##   SRP_FotW_matched_collections.csv  — 1806 rows

``` r
cat("  SRP_FotW_unmatched.csv            —", nrow(unmatched), "rows\n")
```

    ##   SRP_FotW_unmatched.csv            — 1377 rows

------------------------------------------------------------------------

## Image URL example

Specimen images are retrieved from the PNW Herbaria portal using the SRP
accession number zero-padded to 6 digits:

``` r
# Pattern
paste0("https://www.pnwherbaria.org/images/jpeg.php?Image=SRP",
       formatC(ACCESSION, width = 6, flag = "0"), ".jpg")

# Example — accession 34726
# https://www.pnwherbaria.org/images/jpeg.php?Image=SRP034726.jpg
```
