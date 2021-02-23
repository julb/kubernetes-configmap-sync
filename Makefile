.DEFAULT_GOAL := help

# Job parameter: src directory.
CURRENT_DIR := $(shell pwd)
SRC_DIR := $(shell basename `pwd` | sed "s|-|_|g")

.PHONY: help build test push format lint install.dependencies version.get version.set version.bump

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#install.dependencies: @ install dependencies.
install.dependencies:
	@exec >&2; \
	echo "> Installing dependencies."; \
	python3 -m venv venv; \
	. venv/bin/activate; \
	venv/bin/python3 -m pip -q install --upgrade pip; \
	venv/bin/pip -q install -r $(CURRENT_DIR)/requirements.txt

#build: @ Builds the package.
build: install.dependencies
	@exec >&2; \
	echo "> Building."; \
	venv/bin/python3 setup.py sdist

#test: @ Tests the package.
test:
	@exec >&2; \
	echo "> Testing."; \
	echo "NOOP."

#test: @ Push the package.
push:
	@exec >&2; \
	echo "> Pushing."; \
	echo "NOOP."

#format: @ Format code
format:
	@exec >&2; \
	echo "> Formatting."; \
	venv/bin/autopep8 -ir setup.py $(SRC_DIR)

#lint: @ Lint package
lint: install.dependencies
	@exec >&2; \
	echo "> Linting."; \
	echo "Running pycodestyle."; \
	venv/bin/pycodestyle setup.py $(SRC_DIR); \
	echo "Running pylint."; \
	venv/bin/pylint setup.py $(SRC_DIR)

#version.get: @ Gets the version value.
version.get: install.dependencies
	@venv/bin/bump2version --allow-dirty --dry-run --list patch | grep current_version | sed "s|^.*=||"

#version.get-released: @ Gets the released version value.
version.get-released: version.get

#version.set: @ Sets the version value.
version.set: install.dependencies
	@exec >&2; \
	echo "> Setting version $(VERSION)"; \
	venv/bin/bump2version --allow-dirty --new-version $(VERSION) patch

#version.bump: @ Bump the version value.
version.bump: install.dependencies
	@exec >&2; \
	echo "> Bumping version."; \
	venv/bin/bump2version --allow-dirty patch
