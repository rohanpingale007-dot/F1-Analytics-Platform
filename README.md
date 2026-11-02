# F1 Analytics Platform

An interactive Formula 1 analytics dashboard built with **Python, Pandas, NumPy, Streamlit, and Plotly**. The application explores historical driver, constructor, race, circuit, qualifying, reliability, pit-stop, and fastest-lap performance through interactive charts, global filters, and automatically generated executive insights.

> **Project status:** Feature-rich portfolio project. Before publishing, validate the metrics, test the app end to end, and document the data source and any licensing requirements.

## Highlights

- **Historical coverage:** 1950–2026 in the included dataset. The 2026 season is partial in this snapshot; the latest included race is dated **26 July 2026**.
- **27,480 driver-race result rows**, covering **1,160 races** in the supplied cleaned master dataset.
- **Nine analysis sections** with a shared global-filter experience.
- **Interactive Plotly visualisations** inside a wide Streamlit application.
- **Executive Insights panel** that derives findings from the currently filtered data rather than relying only on fixed text.
- **Reusable structure:** shared data loading, filtering, styles, and insight-generation logic are separated from page modules.

## Analytics sections

| Section | What it explores |
|---|---|
| Overview | Overall performance KPIs, race trends, and executive insights |
| Driver Analytics | Driver results and performance comparisons |
| Constructor Analytics | Constructor performance and points |
| Season Analysis | Changes in performance across seasons |
| Qualifying vs Race | Grid position and race-result relationships |
| Circuit Analysis | Performance and outcomes by circuit |
| Reliability | Classified finishes, DNFs, and reliability patterns |
| Pit Stop Analysis | Pit-stop behaviour and comparisons |
| Fastest Lap | Fastest-lap time and speed data where available |

The sidebar provides global filters for season range, country, driver, constructor, and circuit. The selected filters affect the active analysis page and the Executive Insights panel.

## Tech stack

- **Python** — application logic
- **Streamlit** — interactive web application
- **Pandas** — data loading, filtering, grouping, and analysis
- **NumPy** — numerical calculations
- **Plotly** — interactive charts

The dashboard's `requirements.txt` lists the direct runtime dependencies. The Jupyter notebooks used for data preparation may require additional packages depending on the cells you run.

## Project structure

```text
f1_dashboard/
├── app.py                         # Streamlit entry point and navigation
├── data_utils.py                  # Data loading, shared filters, helper functions
├── insights.py                    # Dynamic executive-insight generation
├── styles.py                      # Dashboard styling and Plotly theme
├── requirements.txt               # Dashboard runtime dependencies
├── README.md
├── data/
│   └── f1_master_clean.csv        # Cleaned, feature-engineered master dataset
└── pages_lib/
    ├── __init__.py
    ├── overview.py
    ├── driver.py
    ├── constructor.py
    ├── season.py
    ├── qualifying_vs_race.py
    ├── circuit.py
    ├── reliability.py
    ├── pitstop.py
    └── fastestlap.py
```

The wider project archive also contains the source CSV files, the merged workbook, and the `cleaner.ipynb`, `merger.ipynb`, and `EDA.ipynb` notebooks used during data preparation and exploration.

## Run locally

### 1. Requirements

- Python **3.10 or newer**
- `pip`
- The project folder, including `data/f1_master_clean.csv`

### 2. Open the dashboard directory

In a terminal, navigate to the folder containing `app.py`, `requirements.txt`, and `data/`.

Windows example:

```powershell
cd path\to\f1_dashboard
```

### 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Start Streamlit

Run this command **from inside `f1_dashboard/`**:

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open that URL in your browser. Stop the server with `Ctrl+C`.

## Data dictionary

The supplied master file contains **27 columns**:

| Field | Description |
|---|---|
| `season` | Championship season year |
| `race_name` | Grand Prix name |
| `race_date` | Race date |
| `circuit_name` | Circuit name |
| `country` | Country associated with the race |
| `driver_name` | Driver name |
| `nationality` | Driver nationality |
| `constructor` | Constructor/team name |
| `grid_position` | Starting grid position; zero can represent a non-standard/ungraded start |
| `finish_position` | Recorded finishing position |
| `points` | Championship points recorded for the result |
| `fastest_lap_number` | Lap on which the fastest lap was recorded, when available |
| `pit_stops` | Recorded pit-stop count |
| `status` | Recorded finishing/status description |
| `laps` | Laps completed |
| `fastest_lap_time_sec` | Fastest-lap time converted to seconds, where available |
| `fastest_lap_speed` | Recorded fastest-lap speed, where available |
| `classified` | Derived indicator for a classified result |
| `dns` | Derived indicator for did not start |
| `dnf` | Derived indicator for did not finish |
| `win` | Derived winner indicator |
| `podium` | Derived podium indicator |
| `points_finish` | Derived indicator for a points-scoring result |
| `race_id` | Internal race identifier |
| `driver_id` | Internal driver identifier |
| `constructor_id` | Internal constructor identifier |
| `circuit_id` | Internal circuit identifier |

The identifier columns are retained to support reliable grouping and counting. They are not intended as user-facing performance measures.

## Data preparation and interpretation

The included CSV is a pre-cleaned, feature-engineered master table, so the dashboard does not need to run the notebooks every time it starts.

The preparation workflow is documented in the wider archive:

- `cleaner.ipynb` — cleaning source data
- `merger.ipynb` — combining tables
- `EDA.ipynb` — exploratory data analysis

Important interpretation notes:

- **2026 is incomplete in this snapshot.** Do not compare it directly with completed seasons without clearly labelling the difference in coverage.
- **Fastest-lap fields are not available consistently across all historical periods.** Charts should be interpreted only for the observations with recorded values.
- **Missing values are not automatically equivalent to zero.** A missing lap time, speed, or pit-stop value may mean the information was not recorded.
- **DNF and DNS definitions affect rates.** Check the denominator and the status classification when interpreting reliability metrics.
- **Points systems have changed over time.** Raw points across distant eras are not directly comparable without accounting for the championship scoring rules and season context.
- Historical results and derived features should be checked against the original source before using the dashboard for formal research or making strong claims.

## Executive Insights

The `insights.py` module generates candidate findings from the currently filtered DataFrame. Insight generators can return no result when the selected data is too limited. The dashboard ranks available findings and limits repetition across categories.

Treat these as **descriptive observations**, not causal conclusions. A pattern in the dashboard does not by itself establish why a driver, constructor, or circuit performed a certain way.

## Troubleshooting

**`streamlit` is not recognized or not installed**

Activate the project's virtual environment, then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**`ModuleNotFoundError` for `plotly`, `pandas`, or `numpy`**

Install the dependencies using the same Python interpreter that launches the app:

```bash
python -m pip install -r requirements.txt
```

**The dataset cannot be found**

Check that this file exists relative to the dashboard directory:

```text
data/f1_master_clean.csv
```

Run the command from the folder containing `app.py`. Do not move the `data` folder away from `f1_dashboard/`.

**The dashboard opens but a page shows an error**

Record the full terminal traceback, identify the affected page, and check whether the current filter selection leaves the page with empty or missing data.

## Suggested final checks before publishing

- [ ] Run the dashboard from a fresh virtual environment.
- [ ] Open all nine analysis sections.
- [ ] Test the global filters individually and in combination.
- [ ] Verify selected driver, constructor, race, win, podium, and DNF counts against known examples.
- [ ] Check how empty and missing data are handled.
- [ ] Label the 2026 season as partial and state the dataset cutoff.
- [ ] Add screenshots or a short demo GIF to this README.
- [ ] Document the dataset's original source, attribution, and applicable licence.
- [ ] Ensure no local machine paths, credentials, or unrelated files are committed.

## Future improvements

Potential improvements, after validating the current version, include automated tests for core metrics, a reproducible data-refresh pipeline, deployment instructions, and a short findings section with carefully verified examples.

## License and data attribution

No project or dataset licence has been asserted here because it was not established from the supplied project files. Before public redistribution, identify the original data provider and review its attribution and licence terms. Add a `LICENSE` file only after choosing a licence that you have the right to apply to the code and confirming that it is compatible with the included data.

---

Built as a Formula 1 data analytics portfolio project using Python and interactive visualisation.
