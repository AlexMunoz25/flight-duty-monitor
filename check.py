#!/usr/bin/env python3
"""Check requirement is installed and importable. Exits 1 on any failure."""
import sys
from importlib.metadata import distributions
from importlib.util import find_spec
from pathlib import Path
from re import match

# distribution name -> import name, where they differ
ALIASES = {
    "pyyaml": "yaml",
    "python-dotenv": "dotenv",
    "python-multipart": "multipart",
    "python-dateutil": "dateutil",
    "python-calamine": "python_calamine",
    "email-validator": "email_validator",
    "fastapi-mail": "fastapi_mail",
    "dash-bootstrap-components": "dash_bootstrap_components",
    "dash-ag-grid": "dash_ag_grid",
    "dash-extensions": "dash_extensions",
    "pydantic-settings": "pydantic_settings",
    "pytest-asyncio": "pytest_asyncio",
    "pytest-cov": "pytest_cov",
    "pre-commit": "pre_commit",
}
NO_IMPORT = {"pandas-stubs", "types-pyyaml", "ruff"}  # stubs / CLI-only

installed = {dist.name.lower(): dist.version for dist in distributions()}
required = [
    match(r"[A-Za-z0-9._-]+", spec).group().lower()
    for line in (Path(__file__).parent / "requirements.txt").read_text().splitlines()
    if (spec := line.split("#")[0].strip())
]


def status(name: str) -> str:
    module = ALIASES.get(name, name.replace("-", "_"))
    return (
        "MISSING" if name not in installed
        else "ok" if name in NO_IMPORT or find_spec(module)
        else "FAIL"
    )


results = {name: status(name) for name in required}
width = max(map(len, required))
print("\n".join(
    f"{state:7}  {name:{width}}  {installed.get(name, '')}"
    for name, state in results.items()
))

ok = sum(state == "ok" for state in results.values())
print(f"\n{ok}/{len(results)} ok")
sys.exit(ok != len(results))
