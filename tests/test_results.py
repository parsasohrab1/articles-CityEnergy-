from __future__ import annotations

import json
import re
from pathlib import Path

from research.loader import DATA_LICENSE, DATASET_DOI, METADATA_SHA256, PAPER_DOI

from cityenergy.experiment import manuscript_text, replace_results_block, results_block, run
from cityenergy.submission import (
    COPYRIGHT_FORM_URL,
    PORTAL_URL,
    TRACK,
    package_problems,
    portal_sheet,
)

ROOT = Path(__file__).resolve().parents[1]


def test_license_record_names_cc_by_and_not_the_kaggle_dump():
    text = (ROOT / "research" / "DATA.md").read_text(encoding="utf-8")
    assert DATA_LICENSE == "CC-BY-4.0"
    assert "CC BY 4.0" in text
    assert DATASET_DOI in text
    assert PAPER_DOI in text
    assert METADATA_SHA256 in text
    assert "Kaggle packaging" in text
    assert "was not downloaded" in text


def test_committed_results_match_a_fresh_run():
    path = ROOT / "results" / "results.json"
    committed = json.loads(path.read_text(encoding="utf-8"))
    assert committed == run()
    assert committed["dataset"]["license"] == "CC-BY-4.0"
    metrics = committed["metrics"]
    hours = metrics["n_test_hours"]
    assert hours > 0
    assert committed["selection"]["n_test_buildings"] > 0
    assert committed["dataset"]["n_previous_year_timestamps"] == 8784
    assert committed["dataset"]["n_test_year_timestamps"] == 8760
    assert metrics["n_covered"] / hours >= committed["protocol"]["nominal_coverage"]
    assert metrics["mae_kwh"] < metrics["mean_test_load_kwh"]
    assert metrics["mae_kwh"] < metrics["transfer_mae_kwh"]
    assert metrics["mean_interval_width_kwh"] < 2.0 * metrics["mean_test_load_kwh"]


def test_readme_and_trl_quote_the_results_file():
    payload = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    block = results_block(payload)
    quoted = ("README.md", "docs/TRL.md", "docs/JOURNAL_FIT.md", "article/abstract.md")
    for relative in quoted:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert block in text
        assert text == replace_results_block(text, block)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    trl = (ROOT / "docs" / "TRL.md").read_text(encoding="utf-8")
    assert "synthetic-data performance number" in readme
    assert "synthetic-data performance number" in trl


def test_aiei_gate_names_the_call_and_does_not_submit():
    gate = (ROOT / "docs" / "JOURNAL_FIT.md").read_text(encoding="utf-8")
    assert "https://www.aiei2027.org/cfp.html" in gate
    assert "15 February 2027" in gate
    assert "The manuscript reports this next-year forecast." in gate
    assert "Nothing has been uploaded." in gate
    assert "Intelligent energy forecasting" in gate
    banned = []
    watched = (
        "README.md",
        "docs/BRS.md",
        "docs/TRL.md",
        "docs/JOURNAL_FIT.md",
        "article/abstract.md",
    )
    for relative in watched:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        if "patent" in text or "counsel" in text:
            banned.append(relative)
    assert banned == []


def test_manuscript_is_anonymous_and_quotes_the_results():
    payload = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
    text = (ROOT / "article" / "manuscript.txt").read_text(encoding="utf-8")
    assert text == manuscript_text(payload)
    portal = (ROOT / "article" / "PORTAL.txt").read_text(encoding="utf-8")
    assert portal == portal_sheet(text)
    pdf = (ROOT / "article" / "manuscript.pdf").read_bytes()
    assert package_problems(text, portal, pdf) == []
    found = re.search(br"/Count (\d+)", pdf)
    assert found is not None
    assert 1 <= int(found.group(1)) <= 5


def test_submission_sheet_names_the_live_portal_and_not_an_upload():
    sheet = (ROOT / "docs" / "SUBMISSION.md").read_text(encoding="utf-8")
    portal = (ROOT / "article" / "PORTAL.txt").read_text(encoding="utf-8")
    assert PORTAL_URL in sheet
    assert COPYRIGHT_FORM_URL in sheet
    assert TRACK in sheet
    assert TRACK in portal
    assert "Nothing in this repository has been uploaded." in sheet
    assert "EasyChair" not in sheet
