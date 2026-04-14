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
│   ├── 03_junior_pathway.ipynb
│   ├── 04_surface_tournament.ipynb
│   ├── 05_ml_match_prediction.ipynb
│   ├── 06_health_fatigue.ipynb
│   └── 07_wheelchair_tennis.ipynb
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
- Elite players (Top 20) win 68% of matches — ranking is a strong but imperfect predictor
- Points gap is a stronger and more linear predictor than ranking position alone
- Elite players peak at Grand Slams (74.4%) — they elevate when it matters most
- Tour Regulars and Challengers perform significantly better in Davis Cup and
  team events — team formats and home advantage boost mid-ranked players
- Only the top 20 can be reliably expected to convert favourite status into wins

---

### 02 — Player progression tracking
Tracks how player rankings change over time across 237 players.

**Key findings:**
- Four distinct progression archetypes identified from data: rapid risers,
  declining players, elite consistent and breakthrough players
- Clear trade-off between speed of improvement and consistency — the fastest
  improving players are almost always the most volatile
- Two breakthrough templates exist — fast focused climbs and slow steady
  journeys both produce top 50 players
- 21 players achieved a true breakthrough (started outside top 100, ended
  inside top 50) between 2022 and 2024
- Juncheng Shang is the most dramatic breakthrough in the dataset (663 → 50)

---

### 03 — Junior pathway analysis
Analyses performance, improvement rate and volatility across three career
stages: U18, U19–21 and Senior players.

**Career stage definitions:**
- U18 — official ITF junior category (exploratory due to small sample size)
- U19–21 — transition years, primary focus of junior pathway analysis
- Senior (21+) — established professional players, benchmark group

*In progress*

---

### 04 — Surface & tournament analysis
*Coming soon*

### 05 — Match outcome prediction (ML)
*Coming soon*

### 06 — Health & fatigue monitoring
*Coming soon*

### 07 — Wheelchair tennis
*Coming soon*

---

## Relevance to sports governing bodies

| Notebook section | ITF use case |
|---|---|
| Win % by rank group | Player ranking assessment and validation |
| Opposition variety | Tournament seeding effectiveness |
| Upset analysis | Anticipating upsets, wildcard allocation decisions |
| Rank points gap | More precise seeding metric than ranking position alone |
| Tournament level matrix | Tournament assessment data streams, player pathway planning |
| Player progression (notebook 02) | Tracking player progression data |
| Junior pathway (notebook 03) | Junior pathway training and competition testing |
| Health & fatigue (notebook 06) | Tracking player health on Tour |
| Wheelchair tennis (notebook 07) | Classification digitisation, junior pathway analysis |

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