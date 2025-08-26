from pathlib import Path
import json
import pandas as pd

OUT = Path("outputs")
REQ_FILES = [
    "merged.csv",
    "hourly_means_ci_load.csv",
    "hourly_means_ci_price.csv",
    "meta.json",
    "plot_load_heatwave_vs_normal_DE_CI.png",
    "plot_price_heatwave_vs_normal_DE_LU_CI.png",
]

def must_exist(p: Path):
    assert p.exists(), f"Missing: {p}"

def main():
    # existence
    for f in REQ_FILES:
        must_exist(OUT / f)

    # meta + merged schema
    meta = json.loads((OUT / "meta.json").read_text())
    load_col, price_col = meta["elec_load_col"], meta["elec_price_col"]

    merged = pd.read_csv(OUT / "merged.csv")
    need = {"date", "hour", "heatwave", load_col, price_col}
    assert need.issubset(merged.columns), f"merged.csv: missing {sorted(need - set(merged.columns))}"
    assert merged["hour"].between(0, 23).all(), "merged.csv: 'hour' outside [0,23]"
    hw_vals = set(merged["heatwave"].dropna().unique())
    assert hw_vals <= {0, 1}, f"merged.csv: heatwave has unexpected values {sorted(hw_vals - {0,1})}"

    # stats tables (minimal schema)
    for fname in ["hourly_means_ci_load.csv", "hourly_means_ci_price.csv"]:
        df = pd.read_csv(OUT / fname)
        need = {"heatwave", "hour", "mean", "lo", "hi", "n"}
        assert need.issubset(df.columns), f"{fname}: missing {sorted(need - set(df.columns))}"

    # figures are non-empty
    for fig in ["plot_load_heatwave_vs_normal_DE_CI.png", "plot_price_heatwave_vs_normal_DE_LU_CI.png"]:
        fp = OUT / fig
        assert fp.stat().st_size > 1024, f"{fig}: file suspiciously small (<1KB)"

    print("OK")

if __name__ == "__main__":
    main()
