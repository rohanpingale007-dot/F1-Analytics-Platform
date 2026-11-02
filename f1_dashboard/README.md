# F1 Analytics Platform

A dark, motorsport-inspired Formula 1 analytics dashboard built with
**Streamlit + Plotly + Pandas**. Built as a portfolio piece — the goal is an
analytics *product*, not a one-off script of charts.

## Quick start

```bash
cd f1_dashboard
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. No external API keys or network
access are required — the cleaned dataset ships inside `data/`.

## Project structure

```
f1_dashboard/
├── app.py                  # Entry point: sidebar, global filters, page router
├── data_utils.py            # Cached data loading + shared aggregation helpers
├── insights.py               # Executive Insights engine (dynamic, no hardcoded text)
├── styles.py                 # Dark theme CSS + shared Plotly template
├── data/
│   └── f1_master_clean.csv   # Cleaned, feature-engineered results table
├── pages_lib/
│   ├── overview.py
│   ├── driver.py
│   ├── constructor.py
│   ├── season.py
│   ├── qualifying_vs_race.py
│   ├── circuit.py
│   ├── reliability.py
│   ├── pitstop.py
│   └── fastestlap.py
└── requirements.txt
```

## Data notes

The source file (`masterfile.xlsx`) is a race-results table spanning
**1950–2026** (27,480 driver-race results). During cleaning:

- Mangled UTF-8 text (e.g. driver/circuit names with accents) was repaired.
- `Grid Position` was coerced to numeric; `0` denotes a driver who did not
  start from a graded grid slot (pit-lane start, or did-not-qualify/pre-qualify).
- `Status` was used to derive three mutually exclusive race outcomes:
  - **Classified** — `Finished`, or lapped (`+1 Lap`, `+2 Laps`, …)
  - **DNF** — started but did not finish (accident, mechanical failure, disqualification, etc.)
  - **DNS** — did not start (`Did not qualify`, `Did not prequalify`)
- `fastestLapSpeed` and `fastestLapTime` are missing for a large share of
  older seasons (speed/time trap data wasn't recorded consistently before the
  2000s); every fastest-lap chart in the app states its data coverage rather
  than silently averaging over gaps.
- Raw database IDs (`resultId`, `raceId`, `driverId`, …) are retained
  internally for accurate grouping/counting but are never shown in the UI.

## Executive Insights

`insights.py` exposes `generate_executive_insights(filtered_df)`, which runs
a set of independent, pure-Pandas insight generators (leading driver/
constructor, grid-to-podium conversion, reliability spread, season/pace
trends, pit-stop patterns, circuit extremes, and richer single-driver /
single-constructor snapshots when the filters isolate one). Each generator:

- returns `None` when the current selection doesn't have enough data to
  support a reliable claim (thresholds are defined at the top of the file),
- computes every number directly from the DataFrame it's given — nothing is
  hardcoded,
- is ranked by a magnitude-aware weight and de-duplicated by category so the
  panel shows a diverse top 3–5 rather than five versions of the same finding.

If every generator returns `None`, the panel shows "Insufficient data to
generate a reliable insight for this selection" rather than fabricating one.

## Design notes

- Dark, Bloomberg/broadcast-style theme (see `styles.py`) — no gradients,
  logos, or 3D charts.
- All charts share one Plotly template for visual consistency.
- The sidebar filters (Season range, Country, Driver, Constructor, Circuit)
  are global: they narrow the dataset that every page and the Executive
  Insights panel work from. Each page's own selector (e.g. "select a driver"
  on Driver Analytics) operates within whatever the sidebar has already
  scoped.
