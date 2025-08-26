from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

# ---- minimal config ----
YEAR = 2019
MONTHS = (6, 7, 8, 9)
TZ = "Europe/Berlin"
Q = 0.90              # heatwave quantile
MIN_RUN = 3           # consecutive hot days
TEMP_CSV = "Temp_pop_hourly_Ger.csv"
TEMP_TIME = "time"
TEMP_VAL = "T_pop_C"
ELEC_CSV = "elec_data_2019_Ger.csv"
ELEC_TIME = "utc_timestamp"
ELEC_LOAD = "DE_load_actual_entsoe_transparency"
ELEC_PRICE = "DE_LU_price_day_ahead"

# ---- paths (assumes this file is in scripts/) ----
def project_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    raw, out = root / "raw_data", root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    return root, raw, out

# ---- small helpers ----
def to_local_naive_utc(s: pd.Series, tz: str) -> pd.Series:
    return pd.to_datetime(s, utc=True, errors="raise").dt.tz_convert(ZoneInfo(tz)).dt.tz_localize(None)

def flag_heatwaves(daily_max: pd.Series, q: float, min_run: int) -> pd.DataFrame:
    if daily_max.empty: raise ValueError("daily_max empty")
    thr = float(daily_max.quantile(q))
    hot = (daily_max > thr).astype(int)
    is_start = (hot.ne(hot.shift(fill_value=0)) & hot.eq(1))
    run_id = is_start.cumsum() * hot
    run_len = run_id.replace(0, np.nan).map(run_id.value_counts()).fillna(0).astype(int)
    hw = (hot.eq(1) & (run_len >= min_run)).astype(int)
    return pd.DataFrame({"date": daily_max.index, "heatwave": hw.values}), thr

# ---- main ----
def main() -> None:
    _, raw, out = project_paths()

    tpath, epath = raw / TEMP_CSV, raw / ELEC_CSV
    if not tpath.exists(): raise FileNotFoundError(f"Missing {tpath}")
    if not epath.exists(): raise FileNotFoundError(f"Missing {epath}")

    # Temperature → daily max → heatwave days
    tdf = pd.read_csv(tpath)
    need = {TEMP_TIME, TEMP_VAL}
    if not need.issubset(tdf.columns): raise ValueError(f"{TEMP_CSV} missing {sorted(need - set(tdf.columns))}")
    tdf[TEMP_TIME] = to_local_naive_utc(tdf[TEMP_TIME], TZ)
    tdf = (tdf.rename(columns={TEMP_VAL: "temp_c"})
              .assign(year=lambda d: d[TEMP_TIME].dt.year,
                      month=lambda d: d[TEMP_TIME].dt.month))
    tdf = tdf[(tdf["year"] == YEAR) & (tdf["month"].isin(MONTHS))].copy()
    if tdf.empty: raise ValueError("No temperature rows in Jun–Sep of target year")
    tdf["date"] = tdf[TEMP_TIME].dt.floor("D")
    daily_max = tdf.groupby("date")["temp_c"].max()
    hw_days, thr = flag_heatwaves(daily_max, Q, MIN_RUN)
    era_start, era_end = hw_days["date"].min(), hw_days["date"].max()

    # Electricity → restrict window → date/hour
    edf = pd.read_csv(epath)
    need = {ELEC_TIME, ELEC_LOAD, ELEC_PRICE}
    if not need.issubset(edf.columns): raise ValueError(f"{ELEC_CSV} missing {sorted(need - set(edf.columns))}")
    edf[ELEC_TIME] = to_local_naive_utc(edf[ELEC_TIME], TZ)
    edf = (edf.assign(year=lambda d: d[ELEC_TIME].dt.year,
                      month=lambda d: d[ELEC_TIME].dt.month)
              .loc[lambda d: (d["year"] == YEAR) & (d["month"].isin(MONTHS)),
                   [ELEC_TIME, ELEC_LOAD, ELEC_PRICE]]
              .rename(columns={ELEC_TIME: "ts"}))
    if edf.empty: raise ValueError("No electricity rows in Jun–Sep of target year")
    edf["date"] = pd.to_datetime(edf["ts"]).dt.floor("D")
    edf["hour"] = pd.to_datetime(edf["ts"]).dt.hour

    # Merge + persist
    merged = edf.merge(hw_days, on="date", how="left", validate="many_to_one", indicator=True)
    miss = int((merged["_merge"] != "both").sum())
    if miss: raise ValueError(f"Missing heatwave flag for {miss} row(s); check coverage/alignment")
    merged = merged.drop(columns="_merge")
    merged.to_csv(out / "merged.csv", index=False)

    meta = {
        "era_start": str(era_start.date()), "era_end": str(era_end.date()),
        "heatwave_days": int(hw_days["heatwave"].sum()), "total_days": int(len(hw_days)),
        "threshold_temp_c": thr, "quantile": Q, "min_run": MIN_RUN, "year": YEAR,
        "elec_load_col": ELEC_LOAD, "elec_price_col": ELEC_PRICE,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote {out / 'merged.csv'} and {out / 'meta.json'}")

if __name__ == "__main__":
    main()
