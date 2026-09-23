import importlib.util
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[2]
INSTALLATION_MODULE = ROOT / "test_installation.py"


def _requirements(path="requirements.txt"):
    return [
        Requirement(line.strip())
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_tensorflow_is_kept_where_supported_but_does_not_block_python_314():
    tensorflow = [item for item in _requirements() if item.name.lower() == "tensorflow"]
    assert len(tensorflow) == 1
    requirement = tensorflow[0]
    assert requirement.marker is not None
    assert requirement.marker.evaluate({"python_version": "3.13"})
    assert not requirement.marker.evaluate({"python_version": "3.14"})


def test_python38_ci_profile_covers_declared_legacy_core_imports():
    spec = importlib.util.spec_from_file_location(
        "installation_contract", INSTALLATION_MODULE
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    profile = {
        canonicalize_name(item.name)
        for item in _requirements("requirements-ci-py38.txt")
    }
    distribution_aliases = {"psycopg2": "psycopg2-binary"}
    expected = {
        canonicalize_name(distribution_aliases.get(name, name))
        for name in module.CORE_IMPORTS
    }
    assert expected <= profile
    assert canonicalize_name("jinja2") in profile


def test_python38_ci_profile_excludes_redundant_heavy_optional_ml_stack():
    profile = {
        canonicalize_name(item.name)
        for item in _requirements("requirements-ci-py38.txt")
    }
    assert canonicalize_name("tensorflow") not in profile
    assert canonicalize_name("torch") not in profile
    assert canonicalize_name("transformers") not in profile
