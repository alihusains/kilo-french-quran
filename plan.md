# Plan: Create Tafsir SQLite Database

## Objective
Build a `database.sqlite` file containing Quranic text, French verse translations, audio references, and per-surah tafsir content across 6 sections, sourced from the CSV and 114 DOCX files.

## Database Schema

### Table: `surahs`
| Column | Type | Source |
|---|---|---|
| `sura_id` | INTEGER PK | CSV |
| `name_ar` | TEXT | CSV |
| `name_french` | TEXT | from DOCX header |
| `type` | TEXT | CSV (Makki/Madani) |
| `ayat_count` | INTEGER | CSV |

### Table: `verses`
| Column | Type | Source |
|---|---|---|
| `ayat_id` | INTEGER PK | CSV (global ID) |
| `sura_id` | INTEGER FK | CSV |
| `ayat_no` | INTEGER | CSV (verse # in surah) |
| `juz_no` | INTEGER | CSV |
| `ayat_ar` | TEXT | CSV (Arabic text) |
| `ayat_fr` | TEXT | Extracted from DOCX Tafsir section |
| `ayat_sajda` | INTEGER | CSV |
| `audio_url` | TEXT | CSV |
| `audio_translation_french` | TEXT | CSV |
| `audio_tafsir` | TEXT | CSV |

### Table: `tafsir_sections`
6 rows defining the sections:

| `code` | `title_fr` | `title_fr_short` | `sort_order` |
|---|---|---|---|
| `themes` | Abrégé de la table thématique de la sourate | Thèmes | 1 |
| `apercu` | Aperçu du contenu de la sourate | Aperçu | 2 |
| `merites` | Bienfaits de la récitation | Mérites | 3 |
| `contexte` | Circonstances de la révélation | Contexte | 4 |
| `tafsir` | Exégèse et commentaire de la sourate | Tafsir | 5 |
| `enseignements` | Message et leçon à tirer de la sourate | Enseignements | 6 |

### Table: `tafsir_content`
| Column | Type | Source |
|---|---|---|
| `id` | INTEGER PK | auto |
| `sura_id` | INTEGER FK | from DOCX filename |
| `section_id` | INTEGER FK | mapped from section label |
| `content` | TEXT | full text from DOCX |

One row per (surah, section) combination.

## Data Extraction Pipeline

### Step 1: Create DB & Load CSV
- Parse `French Quran - Tafsir - quran (1).csv`
- Insert 114 rows into `surahs`
- Insert 6236 rows into `verses` (Arabic + metadata, `ayat_fr` left null initially)

### Step 2: Parse DOCX Files
For each of the 114 surahs, find the corresponding DOCX file across the folders:
- `sendingthesurahs/` → surahs 1–10
- `pleasefindattachedthesecond...` → surahs 11–20
- `...third...` → surahs 21–30
- `...fourth...` → surahs 31–40
- `...fifth...` → surahs 41–50
- `...sixth...` → surahs 51–60
- `...seventh...` → surahs 61–70
- `...eighth...` → surahs 71–80
- `...ninth...` → surahs 81–90
- `...tenth...` → surahs 91–114

For each DOCX file:
1. Read the XML content via `zipfile+xml.etree`
2. Extract the surah title and name_french from the header
3. Parse the 5 labeled sections (a–e) and extract their full text
4. Within section (d) "Exégèse et commentaire", detect "Circonstances de la révélation" subheadings — extract that content as a separate `contexte` section, and keep the remaining as `tafsir`
5. Within the Tafsir section, parse Arabic verse lines to extract French translations (`ayat_fr`):
   - Match pattern: Arabic text followed by a numbered French translation (`N- ...`)
   - Update the corresponding `verses.ayat_fr` in the DB

### Step 3: Populate DB
- Insert parsed tafsir content into `tafsir_content`
- Update `verses.ayat_fr` and `surahs.name_french`

## DOCX Parsing Details

The DOCX files have this general structure:
```
Line 0: Sourate <Name>                    ← surah title
Line 1: « French Name » ...               ← surah metadata + name_french
...blank...
a) Abrégé de la table thématique...       ← section a
<content paragraphs>
...blank...
b) Aperçu du contenu de la sourate        ← section b
<content paragraphs>
...blank...
c) Bienfaits de la récitation             ← section c
<content paragraphs>
...blank...
d) Exégèse et commentaire de la sourate   ← section d (contains Circonstances + Tafsir)
<Arabic verse with number>
<French translation line: "N- ...">
<commentary paragraphs>
...possibly "Circonstances de la révélation" subsections...
...blank...
e) Message et leçon à tirer de la sourate ← section e
<content paragraphs>
```

## Tools
- Python 3 with `sqlite3`, `zipfile`, `xml.etree.ElementTree`, `csv` (stdlib only — no external dependencies)
- Single script: `build_database.py`

## Verification
- Row counts: 114 surahs, 6236 verses, 6 sections, ~684 tafsir_content rows (114 × 6)
- Sample queries to verify data integrity
- Check that `ayat_fr` is populated for at least some verses in each surah
