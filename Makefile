# Reproduce the full analysis from primary sources. See data/README.md for the refresh order
# and docs/IMPROVEMENT_PLAN.md for the roadmap.
#
#   make test       - offline unit tests
#   make validate   - audit every notebook input (coverage, corrections, quality flags)
#   make execute    - run the notebook headlessly, in place (tables re-render from data)
#   make generate   - rebuild every processed CSV from the committed raw files (offline)
#   make download   - refresh the raw files from their primary sources (network required)
#   make upload     - sync the notebook's inputs to the public S3 mirror (needs AWS keyring creds)
#   make reproduce  - downloads -> generators -> validator -> notebook execution
#   make verify     - offline end-to-end check: tests + validator + execution
#   make paper      - build the manuscript PDF from paper/paper.md (needs pandoc + xelatex)

UV := uv
RUN := $(UV) run
NOTEBOOK := Historical_CMPI_Extension.ipynb

.PHONY: test validate execute generate download upload reproduce verify paper

test:
	$(RUN) pytest -m "not network" -q

validate:
	$(RUN) python scripts/validate_cmpi_inputs.py --target-year 2025

execute:
	$(RUN) jupyter nbconvert --to notebook --execute --inplace $(NOTEBOOK) \
		--ExecutePreprocessor.timeout=900

download:
	for s in scripts/download_*.py; do echo "== $$s"; $(RUN) python "$$s" || exit 1; done

upload:
	$(UV) run $(if $(wildcard .env),--env-file .env) python scripts/upload_s3_notebook-data.py

generate:
	$(RUN) python scripts/generate_indicators_wdi-argentina.py
	$(RUN) python scripts/generate_interest_wb-ids-arg.py
	$(RUN) python scripts/generate_exchange_parallel-cepo.py
	$(RUN) python scripts/generate_inflation_bcra-monthly.py
	$(RUN) python scripts/generate_fiscal_bcra-quasi-fiscal.py
	$(RUN) python scripts/generate_fiscal_fpi-fiscal.py
	$(RUN) python scripts/generate_exchange_paper-devaluation.py
	$(RUN) python scripts/generate_historical_historical-cmpi.py
	$(RUN) python scripts/generate_historical_data-a-2018-excel.py
	$(RUN) python scripts/generate_exchange_bcra-dec-dec.py
	$(RUN) python scripts/generate_exchange_dec-dec-modern.py

reproduce: download generate validate test execute

verify: test validate execute

paper:
	$(RUN) python scripts/build_paper.py
