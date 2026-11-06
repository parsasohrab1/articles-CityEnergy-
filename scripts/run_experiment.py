"""Write results/results.json from the meter file and refresh the marked doc blocks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cityenergy.experiment import replace_results_block, results_block, run  # noqa: E402


def main() -> None:
    payload = run()
    results_path = ROOT / "results" / "results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    block = results_block(payload)
    for relative in ("README.md", "docs/TRL.md", "docs/JOURNAL_FIT.md", "article/abstract.md"):
        path = ROOT / relative
        updated = replace_results_block(path.read_text(encoding="utf-8"), block)
        path.write_text(updated, encoding="utf-8")
    print(results_path)


if __name__ == "__main__":
    main()
