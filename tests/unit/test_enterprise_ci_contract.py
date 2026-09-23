from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTERPRISE_WORKFLOW = ROOT / ".github" / "workflows" / "enterprise-ci.yml"


def _workflow_text() -> str:
    return ENTERPRISE_WORKFLOW.read_text(encoding="utf-8")


def test_black_diagnostics_preserve_fail_closed_formatter_gate():
    workflow = _workflow_text()

    assert (
        "black --check --diff --no-color . 2>&1 | tee .ci/black/black.txt" in workflow
    )
    assert "status=${PIPESTATUS[0]}" in workflow
    assert "printf '%s\\n' \"$status\" > .ci/black/exit-code.txt" in workflow
    assert 'status="$(cat .ci/black/exit-code.txt)"' in workflow
    assert 'exit "$status"' in workflow
    assert "continue-on-error" not in workflow


def test_black_diagnostics_are_uploaded_before_enforcement():
    workflow = _workflow_text()

    capture = workflow.index("Run Black formatter check and capture diagnostics")
    upload = workflow.index("Upload Black diagnostics")
    enforce = workflow.index("Enforce Black formatter check")
    flake8 = workflow.index("Run Flake8 linting")

    assert capture < upload < enforce < flake8
    assert "if: always()" in workflow[upload:enforce]
    assert "name: black-diagnostics" in workflow[upload:enforce]
    assert "if-no-files-found: error" in workflow[upload:enforce]
