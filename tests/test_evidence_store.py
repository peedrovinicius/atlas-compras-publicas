import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from dental_procurement_intelligence.ingestion import EvidenceIntegrityError, EvidenceStore
from dental_procurement_intelligence.pncp import PNCPRawResponse


def test_capture_is_content_addressed_and_writes_manifest(tmp_path: Path) -> None:
    body = b'[{"numeroItem":1,"descricao":"RESINA A2 4G"}]'
    raw = PNCPRawResponse(
        url="https://pncp.gov.br/api/pncp/v1/example",
        status_code=200,
        content_type="application/json",
        content=body,
    )
    retrieved_at = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)

    record = EvidenceStore(tmp_path).capture(raw, retrieved_at=retrieved_at)

    expected_hash = hashlib.sha256(body).hexdigest()
    assert record.sha256 == expected_hash
    assert Path(record.object_path).read_bytes() == body
    assert Path(record.manifest_path).exists()
    assert record.retrieved_at_utc == "2026-09-26T12:00:00Z"


def test_existing_raw_object_is_verified_before_reuse(tmp_path: Path) -> None:
    body = b'{"ok":true}'
    raw = PNCPRawResponse(
        url="https://pncp.gov.br/api/pncp/v1/example",
        status_code=200,
        content_type="application/json",
        content=body,
    )
    store = EvidenceStore(tmp_path)
    record = store.capture(raw)
    Path(record.object_path).write_bytes(b"tampered")

    with pytest.raises(EvidenceIntegrityError):
        store.capture(raw)
