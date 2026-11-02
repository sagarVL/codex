"""Reject dependency source/version drift from the captured upstream Cargo.lock."""
import sys
import tomllib
from pathlib import Path


def identities(path):
    with Path(path).open("rb") as stream:
        manifest = tomllib.load(stream)
    return {
        (entry["name"], entry["version"], entry.get("source"), entry.get("checksum"))
        for entry in manifest["package"]
    }


unexpected = identities(sys.argv[2]) - identities(sys.argv[1])
if unexpected:
    raise SystemExit(f"Focused dependency resolution introduced unpinned packages: {sorted(unexpected, key=str)}")
print("Focused dependency identities and checksums match the captured upstream lockfile.")
