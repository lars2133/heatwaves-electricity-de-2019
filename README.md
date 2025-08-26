# Heatwaves & Electricity (DE, Jun–Sep 2019)

Reproducible pipeline comparing **hourly load/price** on **heatwave vs. normal** days.

# Run
```bash
conda env create -f environment.yml
conda activate econ-heatwaves
make all && make check
# no make? -> python scripts/01_prepare.py && python scripts/02_analysis.py && python scripts/03_plots.py && python check.py


Data (place in raw_data/)

Temp_pop_hourly_Ger.csv (UTC) cols: time, T_pop_C

elec_data_2019_Ger.csv (UTC) cols: utc_timestamp, DE_load_actual_entsoe_transparency, DE_LU_price_day_ahead
Filenames are case-sensitive. If yours differ, edit constants at the top of scripts/01_prepare.py.

Outputs (outputs/)

Figures: plot_load_heatwave_vs_normal_DE_CI.png, plot_price_heatwave_vs_normal_DE_LU_CI.png

Tables: hourly_means_ci_load.csv, hourly_means_ci_price.csv

Meta: meta.json

Intermediate (debug): merged.csv

Notes

Heatwave = daily max temp > q-th percentile and part of ≥ min_run consecutive hot days.

UTC → Europe/Berlin before daily aggregation.

95% CIs use t-critical (falls back to 1.96 if SciPy absent).

Tunables (in scripts/01_prepare.py)

YEAR, MONTHS, Q (percentile), MIN_RUN, TZ, and input filenames/column names.