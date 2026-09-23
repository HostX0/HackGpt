from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTERPRISE_WORKFLOW = ROOT / ".github" / "workflows" / "enterprise-ci.yml"


def _workflow_text() -> str:
    return ENTERPRISE_WORKFLOW.read_text(encoding="utf-8")


def test_black_version_is_pinned_to_published_repair_formatter():
    workflow = _workflow_text()

    assert "BLACK_VERSION: '26.5.1'" in workflow
    assert 'pip install "black==${BLACK_VERSION}" flake8 mypy pylint' in workflow
    assert "black --version" in workflow


def test_quality_lane_uses_black_compatible_python_and_keeps_install_diagnostics():
    workflow = _workflow_text()
    code_quality = workflow[
        workflow.index("  code-quality:") : workflow.index("  test-suite:")
    ]

    assert "QUALITY_PYTHON_VERSION: '3.11'" in workflow
    assert "python-version: ${{ env.QUALITY_PYTHON_VERSION }}" in code_quality
    assert "mkdir -p .ci/black" in code_quality
    assert "python --version 2>&1 | tee .ci/black/python-version.txt" in code_quality
    assert "black --version | tee .ci/black/black-version.txt" in code_quality
    assert "python-version: ${{ env.PYTHON_VERSION }}" not in code_quality


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
