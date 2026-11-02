.DEFAULT_GOAL := help
PYTHON ?= .venv/bin/python
REF ?= HEAD
ENGINE ?= legacy
INPUT ?= input
OUT ?=
PORT ?= 3000
ZIP ?=

.PHONY: help versions package package-check run serve check format
help:
	@printf '%s\n' \
	  'make versions                            List maintained version checkpoints' \
	  'make package [REF=tag-or-SHA] [ENGINE=legacy|coding] [ZIP=path.zip]' \
	  'make package-check [same arguments]       Package and verify hashes/Python syntax; no model' \
	  'make run OUT=../work/new-run [REF=HEAD] [ENGINE=legacy|coding] [INPUT=input] [PORT=3000]' \
	  '                                         REAL MODEL GENERATION; requires renewed authorization' \
	  'make serve OUT=../work/existing-run [PORT=3000]  Start the generated app via deploy.sh' \
	  'make check                               Offline tests, formatting and documentation checks' \
	  'make format                              Apply project formatters'
versions:
	@$(PYTHON) scripts/package_coding_agent.py --list
package:
	@$(PYTHON) scripts/package_coding_agent.py $(if $(ZIP),"$(ZIP)") --ref "$(REF)" --engine "$(ENGINE)"
package-check: package
	@$(PYTHON) scripts/package_coding_agent.py $(if $(ZIP),"$(ZIP)") --ref "$(REF)" --engine "$(ENGINE)" --check
run:
	@$(PYTHON) scripts/run_submission.py --ref "$(REF)" --engine "$(ENGINE)" --input "$(INPUT)" --output "$(OUT)" --port "$(PORT)"
serve:
	@test -n "$(OUT)" || (printf '%s\n' 'OUT is required'; exit 2)
	@PORT="$(PORT)" bash "$(OUT)/deploy.sh"
check:
	@$(PYTHON) scripts/run_checks.py --config scripts/checks.json --mode ci
	@npm run format:check
	@npm run lint:md
format:
	@ruff format .
	@npm run format
	@npm run lint:md
