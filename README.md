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
stages using match-level age classification.

**Career stages:**
- Junior (U18) — official ITF junior category (48 matches, 16 players — exploratory)
- Next Gen (19–21) — transition years (1,408 matches, 107 players)
- Senior (21+) — established professionals (16,198 matches, 500 players)

**Key findings:**
- Breaking into the ATP tour at U18 is extremely rare — most U18 players
  won zero matches
- Joao Fonseca is an exceptional outlier — 46.67% win rate across 15 ATP
  matches at age 17
- Next Gen players show the steepest improvement trajectory — median relative
  improvement of 46.96% vs 2.91% for Seniors
- 81.4% of Next Gen players improved their ranking vs 52.3% of Seniors
- Next Gen win rate strongly predicts Senior success (r=0.718, p<0.001)
- Speed of ranking improvement does NOT predict Senior success (r=0.130,
  p=0.546) — consistency matters more than trajectory

---

### 04 — Match outcome prediction (ML)
*Coming soon*

---

### 05 — Health & fatigue monitoring
Investigates the relationship between competitive load and player performance,
and develops a personalised anomaly detection system for tour-level health monitoring.

**⚠️ Important data limitation discovered during analysis:**
The `tourney_date` column records tournament start dates rather than individual
match dates — meaning all matches within a tournament share the same date.
This affects the precision of all load metrics in this notebook. Rather than
abandoning the analysis, the methodology was adjusted:
- Match load metrics are treated as **competitive density proxies** rather
  than precise day-level workload measures
- All findings are presented as directional rather than statistically precise
- This limitation is documented transparently throughout the notebook

This discovery also produced a concrete recommendation for ITF data
infrastructure: collecting individual match dates would enable full
Acute:Chronic Workload Ratio (ACWR) implementation — the gold standard
approach in sports science literature.

**Key findings:**
- Competitive density is not a simple linear predictor of win rate —
  the relationship is statistically significant (F=5.04, p=0.0005) but non-linear
- Elite players show the strongest load-performance relationship — win rate
  drops from 77.6% when fresh to 54.0% at very high competitive density
- The fatigue effect is rank-dependent — Elite players are paradoxically
  most affected by high load despite being best equipped to handle it
- Personalised thresholds outperform fixed thresholds — players must be
  evaluated against their own baseline, not the population average
- 21% of active players were flagged at US Open 2024 (18 High, 14 Medium
  risk out of 152 active players)

**Prototype:** A tour-level personalised anomaly detection system is developed
using each player's historical load distribution. The system is directly
applicable to wheelchair tennis where physical demands make load monitoring
even more critical.

---

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