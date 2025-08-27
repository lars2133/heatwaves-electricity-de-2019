# Heatwaves & Electricity (DE, Jun–Sep 2019)

Reproducible pipeline comparing hourly load/price on heatwave vs. normal days.

## Run
    conda env create -f environment.yml
    conda activate econ-heatwaves
    make all && make check
    # no make?
    python scripts/01_prepare.py && python scripts/02_analysis.py && python scripts/03_plots.py && python check.py

## Data (place in `raw_data/`)
- temp_pop_hourly_Ger.csv (UTC) — columns: time, T_pop_C
- elec_data_2019_Ger.csv (UTC) — columns: utc_timestamp, DE_load_actual_entsoe_transparency, DE_LU_price_day_ahead
(Filenames are case-sensitive; adjust constants in `scripts/01_prepare.py` if yours differ.)

## Outputs (`outputs/`)
- Figures: plot_load_heatwave_vs_normal_DE_CI.png, plot_price_heatwave_vs_normal_DE_LU_CI.png
- Tables:  hourly_means_ci_load.csv, hourly_means_ci_price.csv
- Meta:    meta.json
- Intermediate (debug): merged.csv

## Notes
- Heatwave = daily max temp > q-th percentile and part of ≥ min_run consecutive hot days.
- Convert UTC → Europe/Berlin before daily aggregation.
- 95% CIs: t-critical (fallback 1.96 if SciPy absent).

## Tunables (in `scripts/01_prepare.py`)
YEAR, MONTHS, Q, MIN_RUN, TZ, and input filenames/columns.

## Data sources
- Open Power System Data — Time series v2020-10-06 (**CC BY 4.0**), accessed 2025-07-15.
- Deutscher Wetterdienst (DWD) — Climate Data Center (**DL-DE/BY-2.0**), accessed 2025-07-15.
