"""Copy the exact transport source closure into a workspace without unrelated V8.

No product source or dependency versions are rewritten. Retain the original
Cargo.lock, workspace dependencies, target configuration and relevant patches.
"""
from pathlib import Path
import json
import re
import shutil
import tomllib

base = Path(__file__).resolve().parent
source = base / "codex" / "codex-rs"
destination = base / "transport-source"
manifest_text = (source / "Cargo.toml").read_text(encoding="utf-8")
workspace = tomllib.loads(manifest_text)["workspace"]
queue = [source / name for name in ("codex-api", "http-client", "websocket-client")]
selected = set()
while queue:
    directory = queue.pop().resolve()
    if directory in selected:
        continue
    directory.relative_to(source)
    selected.add(directory)
    package = tomllib.loads((directory / "Cargo.toml").read_text(encoding="utf-8"))
    tables = [package, *package.get("target", {}).values()]
    for table in tables:
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            for name, dep in table.get(section, {}).items():
                if not isinstance(dep, dict):
                    continue
                anchor = directory
                if dep.get("workspace"):
                    dep = workspace["dependencies"][name]
                    anchor = source
                if isinstance(dep, dict) and "path" in dep:
                    queue.append(anchor / dep["path"])

destination.mkdir(exist_ok=True)
for directory in sorted(selected):
    shutil.copytree(directory, destination / directory.relative_to(source), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("target", ".git"))
members = "members = [\n" + "".join(
    f"    {json.dumps(directory.relative_to(source).as_posix())},\n" for directory in sorted(selected)) + "]"
manifest_text = re.sub(r"(?ms)^members = \[.*?^\]", lambda _: members, manifest_text, count=1)
manifest_text = re.sub(r'^v8 = \{ git = .*\n', '', manifest_text, flags=re.M)
(destination / "Cargo.toml").write_text(manifest_text, encoding="utf-8")
shutil.copyfile(source / "Cargo.lock", destination / "Cargo.lock")
shutil.copytree(source / ".cargo", destination / ".cargo", dirs_exist_ok=True)
for name in ("clippy.toml", "rustfmt.toml", "rust-toolchain.toml"):
    if (source / name).exists():
        shutil.copyfile(source / name, destination / name)
print(json.dumps({"source": str(source), "destination": str(destination),
                  "crates": len(selected), "members": sorted(str(p.relative_to(source)) for p in selected)}, indent=2))
