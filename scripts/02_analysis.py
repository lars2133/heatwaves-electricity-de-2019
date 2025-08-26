from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd

CSV_LOAD = "hourly_means_ci_load.csv"
CSV_PRICE = "hourly_means_ci_price.csv"

def project_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    raw, out = root / "raw_data", root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    return root, raw, out

# SciPy optional; normal fallback
try:
    from scipy import stats as _scipy_stats  # type: ignore
except Exception:  # pragma: no cover
    _scipy_stats = None

def _tcrit(n: pd.Series | np.ndarray) -> np.ndarray:
    n = np.asarray(n, float); df = np.maximum(n - 1.0, 1.0)
    return _scipy_stats.t.ppf(0.975, df) if _scipy_stats is not None else np.full_like(df, 1.96)

def hourly_means_ci(df: pd.DataFrame, col: str) -> pd.DataFrame:
    # average within day-hour cells, then compute hour-by-hour stats by heatwave
    dayhour = (df.groupby(["heatwave","hour","date"], as_index=False)[col]
                 .mean().rename(columns={col: "value"}))
    s = (dayhour.groupby(["heatwave","hour"])["value"]
                .agg(mean="mean", std="std", n="count").reset_index())
    for g in (0,1):
        got = set(s.loc[s["heatwave"]==g, "hour"]); miss = set(range(24))-got
        if miss: raise ValueError(f"Missing hours for heatwave={g}: {sorted(miss)}")
    s["se"] = s["std"] / np.sqrt(s["n"].clip(lower=1))
    s["tcrit"] = _tcrit(s["n"]); s["ci"] = s["tcrit"] * s["se"]
    s["lo"], s["hi"] = s["mean"] - s["ci"], s["mean"] + s["ci"]
    return s

def main() -> None:
    _, _, out = project_paths()
    merged = out / "merged.csv"
    if not merged.exists(): raise FileNotFoundError("Run scripts/01_prepare.py first.")
    df = pd.read_csv(merged, parse_dates=["date"])

    import json
    meta = json.loads((out / "meta.json").read_text())
    load_col, price_col = meta["elec_load_col"], meta["elec_price_col"]

    hourly_means_ci(df, load_col).to_csv(out / CSV_LOAD, index=False)
    hourly_means_ci(df, price_col).to_csv(out / CSV_PRICE, index=False)
    print(f"Wrote {out / CSV_LOAD} and {out / CSV_PRICE}")

if __name__ == "__main__":
    main()
