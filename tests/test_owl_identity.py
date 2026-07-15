import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_IDS = {
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "7e3c1a8f-2b94-4d6e-9a51-2095099012ab",
}


def test_owl_hubitat_identities_are_isolated_from_upstream():
    server = (ROOT / "hubitat-mcp-server.groovy").read_text(encoding="utf-8")
    child = (ROOT / "hubitat-mcp-rule.groovy").read_text(encoding="utf-8")

    assert 'name: "MCP Rule Server Owl"' in server
    assert 'namespace: "mcpowl"' in server
    assert "#include mcp." not in server
    assert 'name: "MCP Rule Owl"' in child
    assert 'parent: "mcpowl:MCP Rule Server Owl"' in child

    for library in (ROOT / "libraries").glob("*.groovy"):
        declaration = library.read_text(encoding="utf-8").splitlines()[0]
        assert 'namespace: "mcpowl"' in declaration, library.name


def test_owl_hpm_delivery_has_unique_ids_names_and_urls():
    manifest = json.loads((ROOT / "packageManifest.json").read_text(encoding="utf-8"))
    entries = manifest["apps"] + manifest["bundles"]

    assert manifest["packageName"] == "MCP Rule Server Owl"
    assert {entry["id"] for entry in entries}.isdisjoint(ORIGINAL_IDS)
    assert all(entry["namespace"] == "mcpowl" for entry in entries)
    assert all("hansenjacobs/Hubitat-local-MCP-server" in entry["location"] for entry in entries)
    assert manifest["bundles"][0]["location"].endswith("/mcp-libraries-owl.zip")

    builder = (ROOT / "tools" / "build-bundle.py").read_text(encoding="utf-8")
    assert 'NAMESPACE = "mcpowl"' in builder
    assert 'BUNDLE_NAME = "mcp_libraries_owl"' in builder
    assert 'OUTPUT_ZIP = OUTPUT_DIR / "mcp-libraries-owl.zip"' in builder
