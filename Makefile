.PHONY: all help clean

SHELL=/usr/bin/env bash -eo pipefail

.SECONDARY:

.SUFFIXES:

all:
	./run_all.sh

clean: ## Clean
	git clean -fxd
