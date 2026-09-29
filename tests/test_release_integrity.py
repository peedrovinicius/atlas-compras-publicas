import json
import re
import tomllib
from hashlib import sha1
from pathlib import Path

from dental_procurement_intelligence import __version__

_FROZEN_GIT_BLOBS = {
    "data/evaluation/technical-attributes-v11-baseline.json":
        "dba8020419137bc918efb31ae5f632954fb708d2",
    "data/evaluation/technical-attributes-v12.jsonl":
        "2bf4c4248af59cf834bc6dadd02fdb4e32f7bcee",
    "data/evaluation/technical-attributes-v12-baseline.json":
        "35196174c7b91774eb6a06d5966d726cf30caa37",
    "data/evaluation/medications-v1.jsonl":
        "2428e3d39a11ef11ef35bb1e87619e7c7596c27d",
    "data/evaluation/medications-v1-baseline.json":
        "0279f2e86d0b9901a84d49f9e41f2acdc263f84b",
    "data/evaluation/medications-v2.jsonl":
        "9be1808d58f53c6e09a3ba753ec5fc92ddd84be9",
    "data/evaluation/medications-v2-baseline.json":
        "d66b488a35effa3cedccdfb99292b15b27d99b41",
    "data/evaluation/medications-v3.jsonl":
        "3de9b933654f19e5e782861985c68fddb44ed9e7",
    "data/evaluation/medications-v3-baseline.json":
        "0f95cb10bb69b0509c7c2ed890a017bfe8fa201c",
    "data/evaluation/medications-v4.jsonl":
        "ef7561d060cdf578529690391da184ac55a02143",
    "data/evaluation/medications-v4-baseline.json":
        "9cd0b39675fd3992ebae956b3074ad26b7e0ff98",
}


def _git_blob_sha(path: str) -> str:
    content = Path(path).read_bytes()
    header = f"blob {len(content)}\0".encode()
    return sha1(header + content).hexdigest()


def test_frozen_artifacts_keep_their_git_blob_sha() -> None:
    for path, expected_sha in _FROZEN_GIT_BLOBS.items():
        assert _git_blob_sha(path) == expected_sha, path


def test_release_version_is_consistent() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    web_package = json.loads(
        Path("web/package.json").read_text(encoding="utf-8")
    )

    client = Path(
        "src/dental_procurement_intelligence/pncp/client.py"
    ).read_text(encoding="utf-8")
    match = re.search(r"atlas-compras-publicas/([0-9.]+)", client)

    assert project_version == __version__
    assert web_package["version"] == project_version
    assert match is not None
    assert match.group(1) == ".".join(project_version.split(".")[:2])
    assert Path(f"docs/release-v{project_version}.md").exists()


def test_render_blueprint_keeps_only_canonical_services() -> None:
    blueprint = Path("render.yaml").read_text(encoding="utf-8")

    service_names = re.findall(r"^\s+name:\s+([^\s]+)\s*$", blueprint, re.MULTILINE)

    assert service_names == [
        "atlas-compras-publicas-analytics",
        "atlas-compras-publicas-web",
    ]
    assert blueprint.count("autoDeployTrigger: checksPass") == 2
    assert "atlas-compras-publicas-api" not in blueprint
    assert re.search(r"^\s+name:\s+atlas-compras-publicas\s*$", blueprint, re.MULTILINE) is None
    assert "https://atlas-compras-publicas-analytics.onrender.com" in blueprint
    assert "https://atlas-compras-publicas-web.onrender.com" in blueprint


def test_dashboard_snapshot_matches_frozen_baselines() -> None:
    snapshot = json.loads(
        Path("docs/dashboard-quality-snapshot.json").read_text(
            encoding="utf-8"
        )
    )

    samples = 0
    fields = 0
    correct = 0
    for version in range(1, 13):
        baseline = json.loads(
            Path(
                f"data/evaluation/technical-attributes-v{version}-baseline.json"
            ).read_text(encoding="utf-8")
        )
        samples += baseline["sample_count"]
        fields += baseline["evaluated_attribute_count"]
        correct += baseline["correct_attribute_count"]

        holdout = snapshot["technical"]["holdouts"][f"v{version}"]
        assert holdout["sample_count"] == baseline["sample_count"]
        assert (
            holdout["evaluated_field_count"]
            == baseline["evaluated_attribute_count"]
        )
        assert holdout["micro_accuracy"] == baseline["micro_accuracy"]

    assert snapshot["technical"]["sample_count"] == samples
    assert snapshot["technical"]["evaluated_field_count"] == fields
    assert snapshot["technical"]["correct_field_count"] == correct

    medication_samples = 0
    medication_fields = 0
    medication_correct = 0
    for version in range(1, 5):
        baseline = json.loads(
            Path(f"data/evaluation/medications-v{version}-baseline.json").read_text(
                encoding="utf-8"
            )
        )
        medication_samples += baseline["sample_count"]
        medication_fields += baseline["evaluated_field_count"]
        medication_correct += baseline["correct_field_count"]

        holdout = snapshot["medications"]["holdouts"][f"v{version}"]
        assert holdout["sample_count"] == baseline["sample_count"]
        assert holdout["evaluated_field_count"] == baseline["evaluated_field_count"]
        assert holdout["correct_field_count"] == baseline["correct_field_count"]
        assert holdout["micro_accuracy"] == baseline["micro_accuracy"]

    assert snapshot["medications"]["sample_count"] == medication_samples
    assert snapshot["medications"]["evaluated_field_count"] == medication_fields
    assert snapshot["medications"]["correct_field_count"] == medication_correct
    assert snapshot["medications"]["weighted_micro_accuracy"] == round(
        medication_correct / medication_fields,
        4,
    )