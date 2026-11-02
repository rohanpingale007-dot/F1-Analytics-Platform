"""
insights.py
Reusable, dynamic "Executive Insights" generation. Every function here computes
its numbers directly from the currently filtered Pandas DataFrame — nothing is
hardcoded. Each generator returns either an insight dict or None (when the
current filter selection doesn't have enough data to support a reliable claim).

Insight object shape:
    {
        "category": str,
        "title": str,
        "insight": str,   # 1-2 sentences, may contain <b>...</b> for emphasis
        "metric": str,    # short highlighted number/percentage, may be ""
        "weight": float,  # internal ranking score, not rendered
    }
"""
import numpy as np
import pandas as pd

MIN_STARTS = 5          # minimum starts for a driver/constructor rate to be "reliable"
MIN_GROUP_ROWS = 8       # minimum rows in filtered_df before we attempt most insights
MIN_SEASONS_FOR_TREND = 3


def _fmt_pct(x, decimals=1):
    if x is None or pd.isna(x):
        return None
    return f"{x:.{decimals}f}%"


def _period_label(df: pd.DataFrame) -> str:
    seasons = sorted(df["season"].unique())
    if not seasons:
        return "the selected period"
    if len(seasons) == 1:
        return f"the {seasons[0]} season"
    return f"{seasons[0]}\u2013{seasons[-1]}"


# ---------------------------------------------------------------------------
# Individual insight generators
# ---------------------------------------------------------------------------

def insight_leading_driver(df: pd.DataFrame):
    if df["driver_name"].nunique() <= 1:
        return None  # trivial / redundant when the filter already isolates one driver
    starts = df[~df["dns"]]
    wins = df.groupby("driver_name")["win"].sum().sort_values(ascending=False)
    wins = wins[wins > 0]
    if wins.empty:
        return None
    top_driver, top_wins = wins.index[0], int(wins.iloc[0])
    runner_up_wins = int(wins.iloc[1]) if len(wins) > 1 else 0
    total_races = df["race_id"].nunique()
    share = top_wins / total_races * 100 if total_races else np.nan
    margin_txt = (f" — {top_wins - runner_up_wins} more than the next best driver"
                  if runner_up_wins else "")
    return {
        "category": "Driver Performance",
        "title": "Leading Driver",
        "insight": (f"<b>{top_driver}</b> recorded the most wins in {_period_label(df)} "
                    f"with <b>{top_wins}</b> win{'s' if top_wins != 1 else ''} "
                    f"from {total_races} races{margin_txt}."),
        "metric": _fmt_pct(share) if not pd.isna(share) else "",
        "weight": 10 + top_wins,
    }


def insight_leading_constructor(df: pd.DataFrame):
    if df["constructor"].nunique() <= 1:
        return None  # trivial / redundant when the filter already isolates one constructor
    wins = df.groupby("constructor")["win"].sum().sort_values(ascending=False)
    wins = wins[wins > 0]
    if wins.empty:
        return None
    top_c, top_wins = wins.index[0], int(wins.iloc[0])
    points = df.groupby("constructor")["points"].sum().sort_values(ascending=False)
    top_points_c, top_points = points.index[0], points.iloc[0]
    if top_c == top_points_c:
        text = (f"<b>{top_c}</b> leads {_period_label(df)} with <b>{top_wins}</b> wins "
                f"and {top_points:,.0f} points, the most of any constructor.")
    else:
        text = (f"<b>{top_c}</b> leads on wins ({top_wins}), but "
                f"<b>{top_points_c}</b> has scored the most points ({top_points:,.0f}) "
                f"in {_period_label(df)}.")
    return {
        "category": "Constructor Performance",
        "title": "Leading Constructor",
        "insight": text,
        "metric": f"{top_wins} wins",
        "weight": 9 + top_wins,
    }


def insight_grid_impact(df: pd.DataFrame):
    starts = df[(~df["dns"]) & (df["grid_position"] > 0)]
    if len(starts) < MIN_GROUP_ROWS:
        return None
    front = starts[starts["grid_position"] <= 3]
    rest = starts[starts["grid_position"] > 3]
    if len(front) < MIN_STARTS or len(rest) < MIN_STARTS:
        return None
    front_podium = front["podium"].mean() * 100
    rest_podium = rest["podium"].mean() * 100
    diff = front_podium - rest_podium
    if pd.isna(diff):
        return None
    return {
        "category": "Qualifying \u2192 Race",
        "title": "Grid Impact",
        "insight": (f"Drivers starting in the top 3 converted to a podium "
                    f"<b>{front_podium:.1f}%</b> of the time, versus "
                    f"<b>{rest_podium:.1f}%</b> for the rest of the grid in {_period_label(df)}."),
        "metric": f"+{diff:.1f} pp" if diff >= 0 else f"{diff:.1f} pp",
        "weight": 8 + min(abs(diff) / 3, 6),
    }


def insight_pole_win_rate(df: pd.DataFrame):
    starts = df[(~df["dns"]) & (df["grid_position"] > 0)]
    poles = starts[starts["grid_position"] == 1]
    if len(poles) < MIN_STARTS:
        return None
    win_rate = poles["win"].mean() * 100
    return {
        "category": "Qualifying \u2192 Race",
        "title": "Pole Conversion",
        "insight": (f"Pole sitters converted their starting position into a win "
                    f"<b>{win_rate:.1f}%</b> of the time across {len(poles)} pole "
                    f"positions in {_period_label(df)}."),
        "metric": _fmt_pct(win_rate),
        "weight": 7,
    }


def insight_reliability_spread(df: pd.DataFrame):
    starts = df[~df["dns"]]
    grp = starts.groupby("constructor").agg(n=("dnf", "size"), dnf=("dnf", "sum"))
    grp = grp[grp["n"] >= MIN_STARTS]
    if len(grp) < 2:
        return None
    grp["dnf_pct"] = grp["dnf"] / grp["n"] * 100
    grp = grp.sort_values("dnf_pct", ascending=False)
    worst, best = grp.iloc[0], grp.iloc[-1]
    if worst["dnf_pct"] - best["dnf_pct"] < 5:
        return None
    return {
        "category": "Reliability",
        "title": "Reliability Spread",
        "insight": (f"DNF rates ranged from <b>{best['dnf_pct']:.1f}%</b> "
                    f"({best.name}) to <b>{worst['dnf_pct']:.1f}%</b> "
                    f"({worst.name}) among constructors with at least {MIN_STARTS} "
                    f"starts in {_period_label(df)}."),
        "metric": f"{worst['dnf_pct'] - best['dnf_pct']:.1f} pt spread",
        "weight": 7 + (worst["dnf_pct"] - best["dnf_pct"]) / 5,
    }


def insight_overall_dnf_rate(df: pd.DataFrame):
    starts = df[~df["dns"]]
    if len(starts) < MIN_GROUP_ROWS:
        return None
    dnf_rate = starts["dnf"].mean() * 100
    return {
        "category": "Reliability",
        "title": "Field-Wide Reliability",
        "insight": (f"<b>{dnf_rate:.1f}%</b> of race starts ended in a DNF across "
                    f"{len(starts)} starts in {_period_label(df)}."),
        "metric": _fmt_pct(dnf_rate),
        "weight": 4,
    }


def insight_season_trend(df: pd.DataFrame):
    seasons = sorted(df["season"].unique())
    if len(seasons) < MIN_SEASONS_FOR_TREND:
        return None
    by_season = df.groupby("season")["points"].mean()
    if by_season.isna().all() or len(by_season) < MIN_SEASONS_FOR_TREND:
        return None
    x = np.array(by_season.index, dtype=float)
    y = by_season.values.astype(float)
    if np.all(y == y[0]):
        return None
    slope = np.polyfit(x, y, 1)[0]
    pct_change = (y[-1] - y[0]) / y[0] * 100 if y[0] not in (0, np.nan) else np.nan
    direction = "risen" if slope > 0 else "fallen"
    if abs(pct_change) < 3 or pd.isna(pct_change):
        return None
    return {
        "category": "Season Trends",
        "title": "Average Points Trend",
        "insight": (f"Average points scored per result has <b>{direction} "
                    f"{abs(pct_change):.1f}%</b> from {seasons[0]} to {seasons[-1]}."),
        "metric": f"{'+' if pct_change >= 0 else ''}{pct_change:.1f}%",
        "weight": 6 + min(abs(pct_change) / 10, 5),
    }


def insight_fastest_lap_trend(df: pd.DataFrame):
    seasons = sorted(df["season"].unique())
    sub = df.dropna(subset=["fastest_lap_speed"])
    if len(seasons) < MIN_SEASONS_FOR_TREND or sub.empty:
        return None
    by_season = sub.groupby("season")["fastest_lap_speed"].mean().dropna()
    if len(by_season) < MIN_SEASONS_FOR_TREND:
        return None
    x = np.array(by_season.index, dtype=float)
    y = by_season.values.astype(float)
    pct_change = (y[-1] - y[0]) / y[0] * 100 if y[0] != 0 else np.nan
    if pd.isna(pct_change) or abs(pct_change) < 1:
        return None
    direction = "increased" if pct_change > 0 else "decreased"
    return {
        "category": "Race Pace",
        "title": "Fastest-Lap Pace",
        "insight": (f"Average fastest-lap speed has <b>{direction} "
                    f"{abs(pct_change):.1f}%</b> from {int(by_season.index[0])} "
                    f"to {int(by_season.index[-1])}."),
        "metric": f"{'+' if pct_change >= 0 else ''}{pct_change:.1f}%",
        "weight": 5,
    }


def insight_pit_stop_pattern(df: pd.DataFrame):
    starts = df[(~df["dns"]) & (df["laps"] > 0)]
    if len(starts) < MIN_GROUP_ROWS:
        return None
    by_constructor = starts.groupby("constructor")["pit_stops"].mean()
    by_constructor = by_constructor[
        starts.groupby("constructor").size() >= MIN_STARTS
    ]
    if len(by_constructor) < 2:
        return None
    overall_avg = starts["pit_stops"].mean()
    most = by_constructor.idxmax()
    most_val = by_constructor.max()
    if most_val - overall_avg < 0.3:
        return None
    return {
        "category": "Pit-Stop Behaviour",
        "title": "Pit-Stop Frequency",
        "insight": (f"<b>{most}</b> averaged <b>{most_val:.2f}</b> pit stops per race "
                    f"in {_period_label(df)}, above the field average of "
                    f"{overall_avg:.2f}."),
        "metric": f"{most_val:.2f} avg",
        "weight": 4,
    }


def insight_circuit_extreme(df: pd.DataFrame):
    n_circuits = df["circuit_name"].nunique()
    if n_circuits < 3:
        return None
    starts = df[~df["dns"]]
    grp = starts.groupby("circuit_name").agg(n=("dnf", "size"), dnf=("dnf", "sum"))
    grp = grp[grp["n"] >= MIN_STARTS]
    if len(grp) < 3:
        return None
    grp["dnf_pct"] = grp["dnf"] / grp["n"] * 100
    grp = grp.sort_values("dnf_pct", ascending=False)
    top = grp.iloc[0]
    if top["dnf_pct"] < 15:
        return None
    return {
        "category": "Circuit Performance",
        "title": "Toughest Circuit",
        "insight": (f"<b>{top.name}</b> has the highest DNF rate among circuits "
                    f"with {MIN_STARTS}+ starts in {_period_label(df)}, at "
                    f"<b>{top['dnf_pct']:.1f}%</b>."),
        "metric": _fmt_pct(top["dnf_pct"]),
        "weight": 5,
    }


def insight_single_driver_focus(df: pd.DataFrame):
    """Special-cased, richer insight when exactly one driver is in scope."""
    drivers = df["driver_name"].unique()
    if len(drivers) != 1:
        return None
    driver = drivers[0]
    starts = df[~df["dns"]]
    if len(starts) < MIN_STARTS:
        return None
    win_pct = starts["win"].mean() * 100
    podium_pct = starts["podium"].mean() * 100
    avg_gain = None
    graded = starts[starts["grid_position"] > 0]
    if len(graded) >= MIN_STARTS:
        avg_gain = (graded["grid_position"] - graded["finish_position"]).mean()
    gain_txt = ""
    if avg_gain is not None and not pd.isna(avg_gain):
        verb = "gained" if avg_gain >= 0 else "lost"
        gain_txt = f" On average, {driver} has {verb} {abs(avg_gain):.1f} positions per race from grid to flag."
    return {
        "category": "Driver Performance",
        "title": f"{driver} Snapshot",
        "insight": (f"Across {len(starts)} starts in {_period_label(df)}, {driver} "
                    f"has a <b>{win_pct:.1f}%</b> win rate and a "
                    f"<b>{podium_pct:.1f}%</b> podium rate.{gain_txt}"),
        "metric": _fmt_pct(podium_pct),
        "weight": 11,
    }


def insight_single_constructor_focus(df: pd.DataFrame):
    constructors = df["constructor"].unique()
    if len(constructors) != 1:
        return None
    constructor = constructors[0]
    starts = df[~df["dns"]]
    if len(starts) < MIN_STARTS:
        return None
    dnf_pct = starts["dnf"].mean() * 100
    points = df["points"].sum()
    top_driver = df.groupby("driver_name")["points"].sum().sort_values(ascending=False)
    lead = ""
    if not top_driver.empty and points > 0:
        share = top_driver.iloc[0] / points * 100
        lead = (f" {top_driver.index[0]} contributed <b>{share:.1f}%</b> of the "
                f"team's points in this period.")
    return {
        "category": "Constructor Performance",
        "title": f"{constructor} Snapshot",
        "insight": (f"{constructor} scored <b>{points:,.0f}</b> points in "
                    f"{_period_label(df)} with a <b>{dnf_pct:.1f}%</b> DNF rate "
                    f"across {len(starts)} starts.{lead}"),
        "metric": f"{points:,.0f} pts",
        "weight": 11,
    }


GENERATORS = [
    insight_single_driver_focus,
    insight_single_constructor_focus,
    insight_leading_driver,
    insight_leading_constructor,
    insight_grid_impact,
    insight_pole_win_rate,
    insight_reliability_spread,
    insight_season_trend,
    insight_fastest_lap_trend,
    insight_pit_stop_pattern,
    insight_circuit_extreme,
    insight_overall_dnf_rate,
]


def generate_executive_insights(filtered_df: pd.DataFrame, max_insights: int = 5):
    """
    Run every insight generator against filtered_df, drop generators that
    returned None (insufficient data), rank by weight/magnitude, de-duplicate
    by category so the panel doesn't show five variations of the same idea,
    and return the top `max_insights` insight objects.
    """
    if filtered_df is None or filtered_df.empty or len(filtered_df) < MIN_GROUP_ROWS:
        return [{
            "category": "Data",
            "title": "Insufficient Data",
            "insight": "Insufficient data to generate a reliable insight for this selection.",
            "metric": "",
            "weight": 0,
        }]

    candidates = []
    for fn in GENERATORS:
        try:
            result = fn(filtered_df)
        except Exception:
            result = None
        if result:
            candidates.append(result)

    if not candidates:
        return [{
            "category": "Data",
            "title": "Insufficient Data",
            "insight": "Insufficient data to generate a reliable insight for this selection.",
            "metric": "",
            "weight": 0,
        }]

    candidates.sort(key=lambda d: d["weight"], reverse=True)

    selected = []
    seen_categories = set()
    for c in candidates:
        if c["category"] in seen_categories:
            continue
        selected.append(c)
        seen_categories.add(c["category"])
        if len(selected) >= max_insights:
            break

    # top up with remaining highest-weight candidates (allow category repeat)
    # if we couldn't reach max_insights with unique categories only
    if len(selected) < min(max_insights, 3):
        for c in candidates:
            if c not in selected:
                selected.append(c)
            if len(selected) >= max_insights:
                break

    return selected[:max_insights]
