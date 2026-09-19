"""Analyze a two-variant purchase conversion experiment without inventing data."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest


REQUIRED_COLUMNS = {"variant", "visitors", "purchases"}


def analyze(path: Path, alpha: float = 0.05) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    data = data[data["variant"].isin(["A", "B"])].copy().set_index("variant").loc[["A", "B"]]
    if (data["visitors"] <= 0).any() or (data["purchases"] < 0).any() or (data["purchases"] > data["visitors"]).any():
        raise ValueError("Counts must satisfy 0 <= purchases <= visitors and visitors > 0")

    rates = data["purchases"] / data["visitors"]
    z_stat, p_value = proportions_ztest(data["purchases"], data["visitors"], alternative="two-sided")
    lift = rates["B"] - rates["A"]
    se = ((rates["A"] * (1-rates["A"])/data.loc["A", "visitors"]) + (rates["B"] * (1-rates["B"])/data.loc["B", "visitors"])) ** 0.5
    critical = norm.ppf(1-alpha/2)
    return pd.DataFrame({
        "control_rate": [rates["A"]], "treatment_rate": [rates["B"]],
        "absolute_lift": [lift], "relative_lift": [lift/rates["A"] if rates["A"] else float("nan")],
        "ci_low": [lift-critical*se], "ci_high": [lift+critical*se],
        "z_statistic": [z_stat], "p_value": [p_value], "alpha": [alpha],
        "statistically_significant": [p_value < alpha]
    })


def sample_size_per_variant(baseline: float, mde: float, alpha: float = 0.05, power: float = 0.80) -> int:
    treatment = baseline + mde
    if not 0 < baseline < 1 or not 0 < treatment < 1:
        raise ValueError("baseline and baseline + mde must be between 0 and 1")
    effect = 2 * (abs(__import__("math").asin(treatment**0.5) - __import__("math").asin(baseline**0.5)))
    return int(__import__("math").ceil(NormalIndPower().solve_power(effect, power=power, alpha=alpha, ratio=1)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Aggregate CSV with variant, visitors, purchases")
    args = parser.parse_args()
    print(analyze(args.csv).to_string(index=False))
