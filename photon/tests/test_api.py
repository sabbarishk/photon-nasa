import os
from fastapi.testclient import TestClient

import app.main as main


def setup_module(module):
    # Ensure auth skip during tests
    os.environ["PHOTON_SKIP_AUTH"] = "1"


def test_root_and_health():
    client = TestClient(main.app)
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()

    r2 = client.get("/health")
    assert r2.status_code == 200
    assert r2.json().get("status") == "ok"


def test_workflow_generate_endpoint_exists():
    client = TestClient(main.app)
    # Call generate without body -- expect 422 or 400 depending on validation
    r = client.post("/workflow/generate", json={})
    assert r.status_code in (400, 422)
