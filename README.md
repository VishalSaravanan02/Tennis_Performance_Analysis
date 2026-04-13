# Tennis Performance Analysis

A data science project analysing player performance, progression and match outcomes
across ATP tour events from 2022–2024. Inspired by real-world workflows used at
organisations like the International Tennis Federation (ITF).

---

## Motivation

Professional tennis generates a vast amount of match data that remains largely
underutilised for performance analysis. This project explores what player rankings,
match outcomes, and workload data can tell us about how professional tennis players
actually perform — and how that performance can be tracked, predicted, and monitored
in a structured way.

The analysis covers everything from ranking group consistency and upset patterns
to fatigue monitoring and match outcome prediction, with a dedicated section on
how these methods apply to wheelchair tennis specifically.

---

## Project structure

```
Tennis_Performance_Analysis/
│
├── data/
│   ├── raw/                        # Raw ATP match data (not tracked by Git)
│   ├── processed/                  # Cleaned, analysis-ready dataset
│   │   ├── matches_cleaned.csv
│   │   └── matches_cleaned.xlsx
│   └── wheelchair/                 # ITF wheelchair tennis data
│
├── notebooks/
│   ├── 00_data_cleaning.ipynb
│   ├── 01_ranking_performance.ipynb
│   ├── 02_player_progression.ipynb
│   ├── 03_surface_tournament.ipynb
│   ├── 04_ml_match_prediction.ipynb
│   ├── 05_health_fatigue.ipynb
│   └── 06_wheelchair_tennis.ipynb
│
├── outputs/
│   └── figures/                    # Exported chart images
│
├── app/                            # Optional Streamlit dashboard
│   └── app.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Data sources

- **ATP Match Data:** Jeff Sackmann's tennis_atp dataset
  (github.com/JeffSackmann/tennis_atp)
- **Years used:** 2022, 2023, 2024
- **Why these years:** The 2020 and 2021 seasons were significantly disrupted
  by COVID-19 — Wimbledon 2020 was cancelled, travel restrictions affected player
  availability, and competitive conditions were not representative of normal tour play
- **ITF Wheelchair Tennis Rankings:** itftennis.com

---

## Notebooks

### 00 — Data cleaning & feature engineering
Prepares the raw ATP match data for analysis.

**Key decisions:**
- Dropped 24 irrelevant or high-missing columns
- Dropped 152 rows with missing ranking or surface data (<2% of dataset)
- Imputed missing match duration by surface and best_of group rather than
  global median — more accurate for fatigue monitoring
- Fixed naming inconsistencies across tournament names
- Created new tournament level 'T' for team events (ATP Cup, United Cup, Laver Cup)
  which have fundamentally different competitive dynamics
- Reshaped from match format to player format — one row per player per match,
  enabling unbiased ML modelling with a balanced 50/50 win/loss target

**Output:** 17,654 rows × 21 columns, zero missing values

---

### 01 — Ranking & performance analysis
Analyses the relationship between player rankings and match performance.

**Key findings:**

**Win % by rank group:**
- Elite players (Top 20) win 68% of their matches — nearly 7 in every 10
- Tour Regulars (21–100) win just under 50%, reflecting a highly competitive bracket
- Challengers (101–200) win 42% and Qualifiers (200+) win only 33%
- Ranking is a strong and reliable predictor of match outcomes at the top level

**Opposition variety:**
- Elite players face the most predictable range of opponents (std: 85)
- Qualifiers face an enormous range of opposition (std: 325) — from fellow
  qualifiers to top seeds if they progress

**Upset analysis (favourite's perspective):**
- Even Elite players lose as favourite 27% of the time
- Tour Regulars, Challengers and Qualifiers all lose as favourite ~40% of the time
- Only the top 20 can be reliably expected to convert favourite status into wins

**Rank points gap:**
- Points gap is a stronger and more linear predictor of outcomes than ranking position
- Players with a massive points advantage win 80% of matches
- Players with a massive points deficit win only 20% of matches

**Tournament level performance matrix:**
- Elite players peak at Grand Slams (74.4%) and Olympics (74.5%)
- Tour Regulars and Challengers perform significantly better in Davis Cup and
  team events — suggesting team formats and home advantage boost mid-ranked players
- Grand Slams are hardest for lower ranked players — best of 5 sets allows
  elite players to assert dominance more reliably

---

## Relevance to sports governing bodies

| Notebook section | ITF use case |
|---|---|
| Win % by rank group | Player ranking assessment and validation |
| Opposition variety | Tournament seeding effectiveness |
| Upset analysis | Anticipating upsets, wildcard allocation decisions |
| Rank points gap | More precise seeding metric than ranking position alone |
| Tournament level matrix | Tournament assessment data streams, player pathway planning |
| Health & fatigue (notebook 05) | Tracking player health on Tour |
| Player progression (notebook 02) | Tracking player progression data |
| Wheelchair tennis (notebook 06) | Classification digitisation, junior pathway analysis |

---

## How to run

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook

# Open notebooks in order starting with 00_data_cleaning.ipynb
```

---

## Tech stack

- Python 3.9
- pandas, numpy — data manipulation
- matplotlib, seaborn — visualisation
- scikit-learn — machine learning
- jupyter — notebook environment
- openpyxl — Excel compatibility
- streamlit — optional dashboard

---

## Author

Vishal Saravanan — postgraduate student in Data Analytics
GitHub: github.com/VishalSaravanan02