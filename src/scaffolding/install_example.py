"""Install a bundled demo target into the user's workbench.

The plugin ships pedagogical example targets under `${CLAUDE_PLUGIN_ROOT}/examples/<name>/`.
Each example has:

- `paper.md` — a short self-authored spec for onboarding
- `target.yaml` — a preset with `target:` sub-dict to merge into the user's
  `workbench/current_target.yaml`
- `README.md` — labelling, not copied

`install_example` copies the paper into `corpus/papers/` and sets the target
so that running `crypto-intake` immediately sees a source to classify.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from workbench.target import save_target

MODULE = "scaffolding.install_example"

# Plugin-root relative location of bundled examples.
EXAMPLES_DIRNAME = "examples"


def _plugin_root() -> Path:
    """Path to the plugin root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]


def list_examples(plugin_root: str | Path | None = None) -> list[str]:
    """List available demo target names under examples/."""
    root = Path(plugin_root) if plugin_root else _plugin_root()
    examples_dir = root / EXAMPLES_DIRNAME
    if not examples_dir.exists():
        return []
    return sorted(
        p.name for p in examples_dir.iterdir()
        if p.is_dir() and (p / "target.yaml").exists()
    )


def install_example(
    workbench_root: str | Path,
    name: str,
    *,
    plugin_root: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Install the named demo target into an initialized workbench.

    Raises `FileNotFoundError` if the example does not exist or the
    workbench root is not a Crypto Workbench directory (`workbench/`
    subdir missing).
    """
    root = Path(plugin_root) if plugin_root else _plugin_root()
    src_dir = root / EXAMPLES_DIRNAME / name
    if not src_dir.is_dir():
        raise FileNotFoundError(f"bundled example not found: {name!r}")

    preset_path = src_dir / "target.yaml"
    if not preset_path.exists():
        raise FileNotFoundError(f"example {name!r} missing target.yaml")

    wb_root = Path(workbench_root)
    if not (wb_root / "workbench").is_dir():
        raise FileNotFoundError(
            f"workbench_root {wb_root!r} is not initialized; run crypto-init first"
        )

    # Copy paper into corpus/papers/, preserving filename.
    papers_dir = wb_root / "corpus" / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    for candidate in src_dir.iterdir():
        if candidate.name in {"target.yaml", "README.md"}:
            continue
        if not candidate.is_file():
            continue
        dest_name = f"{name}{candidate.suffix}" if candidate.stem == "paper" else candidate.name
        dest = papers_dir / dest_name
        if dest.exists() and not overwrite:
            continue
        shutil.copy2(candidate, dest)
        copied_files.append(str(dest))

    # Merge preset target into current_target.yaml.
    preset = yaml.safe_load(preset_path.read_text(encoding="utf-8")) or {}
    target = preset.get("target", {}) if isinstance(preset, dict) else {}
    if not isinstance(target, dict):
        target = {}

    # Rewrite primary_sources paths relative to workbench root so they
    # match the actual copied filenames. Store as forward-slash POSIX form
    # so the YAML is portable across Windows / POSIX.
    resolved_sources: list[str] = []
    for src in target.get("primary_sources", []) or []:
        p = Path(src)
        if p.stem == "paper":
            resolved = f"corpus/papers/{name}{p.suffix}"
        else:
            resolved = p.as_posix()
        resolved_sources.append(resolved)
    if resolved_sources:
        target["primary_sources"] = resolved_sources

    saved_path = save_target(wb_root, target)

    return {
        "module": MODULE,
        "status": "installed",
        "name": name,
        "workbench_root": str(wb_root),
        "copied_files": copied_files,
        "target_file": str(saved_path),
        "target": target,
    }


def run(**context: Any) -> dict[str, Any]:
    """Install an example from workflow context."""
    name = context["name"]
    workbench_root = context.get("workbench_root", ".cryptoworkbench")
    plugin_root = context.get("plugin_root")
    overwrite = bool(context.get("overwrite", False))
    result = install_example(
        workbench_root, name, plugin_root=plugin_root, overwrite=overwrite
    )
    result["context"] = context
    return result
