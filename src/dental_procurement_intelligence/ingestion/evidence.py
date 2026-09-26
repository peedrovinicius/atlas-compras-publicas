import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from dental_procurement_intelligence.pncp.client import PNCPRawResponse


class EvidenceIntegrityError(RuntimeError):
    """Raised when an existing raw object no longer matches its content hash."""


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    source_url: str
    retrieved_at_utc: str
    status_code: int
    content_type: str | None
    sha256: str
    byte_count: int
    object_path: str
    manifest_path: str


class EvidenceStore:
    """Content-addressed store for immutable source responses and retrieval manifests."""

    def __init__(self, root: str | Path = "data/raw") -> None:
        self.root = Path(root)

    @staticmethod
    def _sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def _atomic_write(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temp_path = Path(temporary.name)
        os.replace(temp_path, path)

    def _object_path(self, digest: str) -> Path:
        return self.root / "objects" / "sha256" / digest[:2] / f"{digest}.json"

    def verify_object(self, path: str | Path, expected_sha256: str) -> None:
        object_path = Path(path)
        actual = self._sha256(object_path.read_bytes())
        if actual != expected_sha256:
            raise EvidenceIntegrityError(
                f"Raw evidence hash mismatch: expected {expected_sha256}, got {actual}"
            )

    def capture(
        self,
        response: PNCPRawResponse,
        retrieved_at: datetime | None = None,
    ) -> EvidenceRecord:
        timestamp = retrieved_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware")
        timestamp = timestamp.astimezone(timezone.utc)

        digest = self._sha256(response.content)
        object_path = self._object_path(digest)

        if object_path.exists():
            self.verify_object(object_path, digest)
        else:
            self._atomic_write(object_path, response.content)

        date_path = timestamp.strftime("%Y/%m/%d")
        timestamp_token = timestamp.strftime("%Y%m%dT%H%M%S.%fZ")
        manifest_path = (
            self.root
            / "manifests"
            / date_path
            / f"{timestamp_token}_{digest[:12]}.json"
        )

        record = EvidenceRecord(
            source_url=response.url,
            retrieved_at_utc=timestamp.isoformat().replace("+00:00", "Z"),
            status_code=response.status_code,
            content_type=response.content_type,
            sha256=digest,
            byte_count=len(response.content),
            object_path=object_path.as_posix(),
            manifest_path=manifest_path.as_posix(),
        )
        manifest = json.dumps(asdict(record), ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        self._atomic_write(manifest_path, manifest)
        return record
