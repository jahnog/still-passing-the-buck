# Reproduce the full analysis from primary sources. See data/README.md for the refresh order
# and docs/IMPROVEMENT_PLAN.md for the roadmap.
#
#   make test       - offline unit tests
#   make validate   - audit every notebook input (coverage, corrections, quality flags)
#   make execute    - run the notebook headlessly, in place (tables re-render from data)
#   make generate   - rebuild every processed CSV from the committed raw files (offline)
#   make download   - refresh the raw files from their primary sources (network required)
#   make reproduce  - downloads -> generators -> validator -> notebook execution
#   make verify     - offline end-to-end check: tests + validator + execution

PY := ./.venv/bin/python
NOTEBOOK := Historical_CMPI_Extension.ipynb

.PHONY: test validate execute generate download reproduce verify

test:
	$(PY) -m pytest -m "not network" -q

validate:
	$(PY) scripts/validate_cmpi_inputs.py --target-year 2025

execute:
	$(PY) -m jupyter nbconvert --to notebook --execute --inplace $(NOTEBOOK) \
		--ExecutePreprocessor.timeout=900

download:
	for s in scripts/download_*.py; do echo "== $$s"; $(PY) "$$s" || exit 1; done

generate:
	$(PY) scripts/generate_indicators_wdi-argentina.py
	$(PY) scripts/generate_interest_wb-ids-arg.py
	$(PY) scripts/generate_exchange_parallel-cepo.py
	$(PY) scripts/generate_fiscal_bcra-quasi-fiscal.py
	$(PY) scripts/generate_fiscal_fpi-fiscal.py
	$(PY) scripts/generate_exchange_paper-devaluation.py
	$(PY) scripts/generate_historical_historical-cmpi.py
	$(PY) scripts/generate_historical_data-a-2018-excel.py
	$(PY) scripts/generate_exchange_bcra-dec-dec.py
	$(PY) scripts/generate_exchange_dec-dec-modern.py

reproduce: download generate validate test execute

verify: test validate execute
