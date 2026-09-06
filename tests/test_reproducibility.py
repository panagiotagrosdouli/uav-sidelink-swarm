from src.reproducibility import build_manifest


def test_manifest_contains_scientific_policy_and_experiments():
    manifest = build_manifest([{"name": "x", "status": "success"}])
    assert manifest["experiments"][0]["name"] == "x"
    assert "SOURCE -> MODEL" in manifest["scientific_policy"]["source_chain"]
    assert "STANDARD" in manifest["scientific_policy"]["allowed_classifications"]
    assert manifest["python_version"]
    assert "package_versions" in manifest
