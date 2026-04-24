"""Unit-тесты для BackupCode."""

from datetime import datetime, timezone

import pytest

from app.context.identity.domain.entities.backup_code import BackupCode


@pytest.mark.unit
class TestBackupCode:
    def test_create_backup_code(self) -> None:
        bc = BackupCode(code_hash="hashed_code_1")
        assert bc.code_hash == "hashed_code_1"
        assert not bc.is_used
        assert bc.used_at is None
        assert isinstance(bc.created_at, datetime)

    def test_mark_used(self) -> None:
        bc = BackupCode(code_hash="hashed_code_1")
        bc.mark_used()
        assert bc.is_used
        assert bc.used_at is not None

    def test_mark_used_sets_timestamp(self) -> None:
        bc = BackupCode(code_hash="hashed_code_1")
        before = datetime.now(tz=timezone.utc)
        bc.mark_used()
        after = datetime.now(tz=timezone.utc)
        assert before <= bc.used_at <= after
