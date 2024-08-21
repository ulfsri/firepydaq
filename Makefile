##########
# Poetry #
##########
POETRY_OPTS ?=
POETRY ?= poetry $(POETRY_OPTS)
RUN_PYPKG_BIN = $(POETRY) run

##@ Testing
.PHONY: test
test: ## Runs tests
	$(RUN_PYPKG_BIN) pytest -v \
		tests/*.py

##@ Building and Publishing

.PHONY: build
build: ## Runs a build
	$(POETRY) build
	$(POETRY) lock
	$(POETRY) install

############
# Coverage #
############
COV_OPTS ?=
COVERAGE ?= coverage $(COV_OPTS)
RUN_COV = $(COVERAGE) run --source=firepydaq --omit=*NIConfig*,*app*,*Echo*,*NISYS*
COV_BADGE = coverage-badge

.PHONY: coverage
coverage:
	$(RUN_COV) -m pytest -x tests
	$(COVERAGE) report
	$(COV_BADGE) -o tests/coverage.svg -f

