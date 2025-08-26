.PHONY: all prepare analysis plots check clean

PY := python

all: prepare analysis plots

prepare:
	$(PY) scripts/01_prepare.py

analysis:
	$(PY) scripts/02_analysis.py

plots:
	$(PY) scripts/03_plots.py

check: plots
	$(PY) check.py

clean:
	rm -rf outputs/*
