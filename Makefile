# Reproduce the full analysis from primary sources. See data/README.md for the refresh order.
#
#   make test       - offline unit tests
#   make validate   - audit every notebook input (coverage, corrections, quality flags)
#   make validate-provenance - audit correction taxonomy and curated fiscal provenance
#   make checksums  - verify processed-data checksum regression lock
#   make execute    - run the notebook headlessly, in place (tables re-render from data)
#   make generate   - rebuild every processed CSV from the committed raw files (offline)
#   make manifest   - write SHA256 manifest for committed inputs and generated paper artifacts
#   make verify-manifest - verify SHA256 manifest without rewriting it
#   make download-data   - refresh statistical raw files (network required)
#   make download-assets - refresh president/minister portraits (network required)
#   make download   - download-data + download-assets
#   make cleanup-raw     - keep only the last two copies of each rotated raw download
#   make upload     - sync the notebook's inputs to the public S3 mirror (needs AWS keyring creds)
#   make reproduce  - downloads -> generators -> validator -> notebook execution
#   make verify     - offline end-to-end check: tests + validators + checksum regression + execution
#   make paper      - build the manuscript PDF from paper/paper.md (needs pandoc + xelatex)
#   make bump VERSION=x.y.z - rewrite pyproject.toml + CITATION.cff, then uv.lock + paper_resolved.md + manifest
#
# Override the analysis horizon: make validate TARGET_YEAR=2026

TARGET_YEAR ?= 2025
export CMPI_TARGET_YEAR := $(TARGET_YEAR)

UV := uv
RUN := $(UV) run
NOTEBOOK := Historical_CMPI_Extension.ipynb
JUPYTER_ENV := JUPYTER_CONFIG_DIR=/tmp/stpb-jupyter-config JUPYTER_RUNTIME_DIR=/tmp/stpb-jupyter-runtime

DOWNLOAD_DATA_SCRIPTS := $(filter-out scripts/download_presidency_portraits.py,$(wildcard scripts/download_*.py))

.PHONY: test validate validate-provenance checksums execute generate manifest verify-manifest download download-data download-assets cleanup-raw upload reproduce verify paper bump

test:
	$(RUN) pytest -m "not network" -q

validate:
	$(RUN) python scripts/validate_data_a_1999.py
	$(RUN) python scripts/validate_cmpi_inputs.py --target-year $(TARGET_YEAR)

checksums:
	$(RUN) python scripts/check_processed_checksums.py

validate-provenance:
	$(RUN) python scripts/validate_provenance.py

execute:
	$(RUN) python scripts/repair_notebook_outputs.py $(NOTEBOOK)
	env $(JUPYTER_ENV) $(RUN) python -m nbconvert --to notebook --inplace $(NOTEBOOK) \
		--ClearOutputPreprocessor.enabled=True \
		--NotebookExporter.optimistic_validation=True
	env $(JUPYTER_ENV) $(RUN) python -m nbconvert --to notebook --execute --inplace $(NOTEBOOK) \
		--ExecutePreprocessor.timeout=900 \
		--ExecutePreprocessor.record_timing=False

download-data:
	for s in $(DOWNLOAD_DATA_SCRIPTS); do echo "== $$s"; $(RUN) python "$$s" || exit 1; done
	$(MAKE) cleanup-raw

download-assets:
	$(RUN) python scripts/download_presidency_portraits.py

download: download-data download-assets

cleanup-raw:
	$(RUN) python scripts/cleanup_raw_downloads.py

upload:
	$(UV) run $(if $(wildcard .env),--env-file .env) python scripts/upload_s3_notebook-data.py

generate:
	$(RUN) python scripts/generate_indicators_wdi-argentina.py
	$(RUN) python scripts/generate_interest_wb-ids-arg.py
	$(RUN) python scripts/generate_interest_us-real-yield-10y.py
	$(RUN) python scripts/generate_exchange_parallel-cepo.py
	$(RUN) python scripts/generate_inflation_bcra-monthly.py
	$(RUN) python scripts/generate_inflation_official-provincial-cpi.py
	$(RUN) python scripts/generate_fiscal_bcra-importer-debt-bopreal.py
	$(RUN) python scripts/generate_fiscal_bcra-quasi-fiscal.py
	$(RUN) python scripts/generate_fiscal_official-corrections.py
	$(RUN) python scripts/generate_fiscal_fpi-fiscal.py
	$(RUN) python scripts/generate_exchange_paper-devaluation.py
	$(RUN) python scripts/generate_historical_historical-cmpi.py
	$(RUN) python scripts/generate_historical_data-a-1999-excel.py
	$(RUN) python scripts/generate_exchange_dec-dec-modern.py
	$(RUN) python scripts/generate_fiscal_denominator-neutral.py
	$(RUN) python scripts/generate_official_provenance-registry.py

manifest:
	$(RUN) python scripts/write_data_manifest.py

verify-manifest:
	$(RUN) python scripts/verify_data_manifest.py

reproduce: download generate validate validate-provenance test execute

verify: test validate validate-provenance checksums execute

paper:
	$(RUN) python scripts/build_paper.py

bump:
	@if [ -z "$(VERSION)" ]; then echo "VERSION is required, e.g. make bump VERSION=1.3.3" >&2; exit 1; fi
	$(RUN) python scripts/bump_project_version.py $(VERSION)
