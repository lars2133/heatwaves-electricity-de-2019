"""Step 3 — plots:
Make two PNGs with CI bands.
Uses a headless Matplotlib backend (Agg).
"""

from __future__ import annotations
from pathlib import Path
import json, numpy as np, pandas as pd

import matplotlib
matplotlib.use("Agg")             # robust, headless
import matplotlib.pyplot as plt

FIG_LOAD  = "plot_load_heatwave_vs_normal_DE_CI.png"
FIG_PRICE = "plot_price_heatwave_vs_normal_DE_LU_CI.png"

def project_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    raw, out = root / "raw_data", root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    return root, raw, out

def plot_profiles(stats: pd.DataFrame, title: str, ylab: str, outfile: Path, label: str) -> Path:
    """Plot mean±95% CI for heatwave vs. normal over hours 0–23 and save to `outfile`."""
    stats = stats.copy(); stats["hour"] = stats["hour"].astype(int)
    def s(hw, col):
        return stats.loc[stats["heatwave"]==hw, ["hour", col]].set_index("hour")[col].reindex(range(24))

    # --- FIX: use NumPy arrays for plotting/fill_between ---
    x   = np.arange(24, dtype=float)
    y0  = s(0, "mean").to_numpy(dtype=float); lo0 = s(0, "lo").to_numpy(dtype=float); hi0 = s(0, "hi").to_numpy(dtype=float)
    y1  = s(1, "mean").to_numpy(dtype=float); lo1 = s(1, "lo").to_numpy(dtype=float); hi1 = s(1, "hi").to_numpy(dtype=float)

    plt.figure(figsize=(8,5))
    plt.plot(x, y0, label="normal")
    plt.plot(x, y1, label="heatwave")
    plt.fill_between(x, lo0, hi0, alpha=0.2, label="normal 95% CI")
    plt.fill_between(x, lo1, hi1, alpha=0.2, label="heatwave 95% CI")
    # -------------------------------------------------------

    plt.title(f"{title}\n{label}"); plt.xlabel("Hour of day"); plt.ylabel(ylab)
    plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
    out_abs = Path(outfile).resolve(); plt.savefig(str(out_abs), dpi=200); plt.close()
    print(f"Saved: {out_abs} ({out_abs.stat().st_size:,} bytes)"); return out_abs

def main() -> None:
    _, _, out = project_paths()
    load_stats  = pd.read_csv(out / "hourly_means_ci_load.csv")
    price_stats = pd.read_csv(out / "hourly_means_ci_price.csv")
    meta = json.loads((out / "meta.json").read_text())
    label = (f"{meta['era_start']} to {meta['era_end']}  |  heatwave days: "
             f"{meta['heatwave_days']}/{meta['total_days']}  |  q={meta['quantile']:.2f}, "
             f"min_run={meta['min_run']}  |  thr={meta['threshold_temp_c']:.2f}°C  |  "
             f"window: Jun–Sep {meta['year']}")

    plot_profiles(load_stats,  "Germany hourly load by heatwave status", "Load (MW)",     out / FIG_LOAD,  label)
    plot_profiles(price_stats, "Germany–Luxembourg day-ahead price by heatwave status", "Price (EUR/MWh)", out / FIG_PRICE, label)

if __name__ == "__main__":
    main()
