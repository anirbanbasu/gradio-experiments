#!/bin/bash
# Upgrade the dependencies including those from Git sources
uv lock -U --prerelease=allow
# Export the requirements to a requirements.txt file
uv export --no-editable --no-annotate --no-emit-workspace --no-dev --frozen --no-hashes --format requirements-txt > requirements.txt
# Run the tests and report coverage with missing values
uv run --group test pytest tests/
