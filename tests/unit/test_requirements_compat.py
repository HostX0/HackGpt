from pathlib import Path

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[2]


def _requirements():
    return [
        Requirement(line.strip())
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_tensorflow_is_kept_where_supported_but_does_not_block_python_314():
    tensorflow = [item for item in _requirements() if item.name.lower() == "tensorflow"]
    assert len(tensorflow) == 1
    requirement = tensorflow[0]
    assert requirement.marker is not None
    assert requirement.marker.evaluate({"python_version": "3.13"})
    assert not requirement.marker.evaluate({"python_version": "3.14"})
