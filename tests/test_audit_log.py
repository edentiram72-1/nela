from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import replace
import tempfile
import unittest

from permissions import AuditLog, AuditRecord, PermissionDecision, PermissionTier
from permissions.audit import AuditWriteError


def make_record(**overrides: object) -> AuditRecord:
    values = {
        "agent": "desktop",
        "action": "launch",
        "capability": "desktop.application.launch",
        "tier": PermissionTier.T1,
        "decision": PermissionDecision.GRANTED,
        "reason": "allowed",
        "granted": True,
        "user_id": "local-owner",
        "target": "Spotify",
        "result_success": True,
        "metadata": {},
    }
    values.update(overrides)
    return AuditRecord(**values)


class AuditLogTests(unittest.TestCase):
    def test_append_behavior_and_json_output(self) -> None:
        log = AuditLog()
        record = log.append(make_record())

        self.assertEqual(log.records(), (record,))
        self.assertIn('"capability": "desktop.application.launch"', record.to_json())
        self.assertIn('"permission_tier": "T1"', record.to_json())
        self.assertTrue(record.entry_hash)
        self.assertTrue(log.verify_chain())

    def test_redacts_sensitive_values(self) -> None:
        log = AuditLog()
        record = log.append(
            make_record(
                target="github_pat-secretsecretsecret",
                metadata={"password": "super-secret", "nested": {"api_token": "ghp-secretsecretsecret"}},
            )
        )

        serialized = record.to_json()
        self.assertIn("[REDACTED]", serialized)
        self.assertNotIn("super-secret", serialized)
        self.assertNotIn("github_pat-secretsecretsecret", serialized)
        self.assertNotIn("ghp-secretsecretsecret", serialized)

    def test_records_are_immutable_from_callers(self) -> None:
        log = AuditLog()
        record = log.append(make_record(metadata={"safe": "value"}))

        with self.assertRaises(TypeError):
            record.metadata["safe"] = "changed"  # type: ignore[index]
        with self.assertRaises(AttributeError):
            record.agent = "changed"  # type: ignore[misc]

    def test_failed_sink_raises_audit_write_error(self) -> None:
        def broken_sink(_line: str) -> None:
            raise OSError("disk full")

        log = AuditLog(sink=broken_sink)

        with self.assertRaises(AuditWriteError):
            log.append(make_record())
        self.assertEqual(log.records(), ())

    def test_file_sink_is_flushed_and_durable(self) -> None:
        with tempfile.TemporaryFile("w+", encoding="utf-8") as sink:
            log = AuditLog(sink=sink)

            log.append(make_record())
            sink.seek(0)

            self.assertIn('"entry_hash":', sink.read())

    def test_filtering_by_time_capability_agent_result_and_session(self) -> None:
        log = AuditLog()
        now = datetime.now(timezone.utc)
        first = log.append(make_record(created_at=now - timedelta(minutes=1), session_id="s1"))
        log.append(
            make_record(
                agent="voice",
                action="speak",
                capability="voice.speak",
                result_success=False,
                session_id="s2",
            )
        )

        self.assertEqual(log.query(agent="desktop"), (first,))
        self.assertEqual(log.query(capability="desktop.application.launch"), (first,))
        self.assertEqual(log.query(result=True), (first,))
        self.assertEqual(log.query(session_id="s1"), (first,))
        self.assertEqual(log.query(start=now - timedelta(minutes=2), end=now), (first,))

    def test_hash_chain_detects_modification_deletion_and_reordering(self) -> None:
        log = AuditLog()
        first = log.append(make_record(action="first", capability="first"))
        second = log.append(make_record(action="second", capability="second"))
        self.assertTrue(log.verify_chain())

        log._records[0] = replace(first, reason="tampered")  # type: ignore[attr-defined]
        self.assertFalse(log.verify_chain())

        log = AuditLog()
        first = log.append(make_record(action="first", capability="first"))
        second = log.append(make_record(action="second", capability="second"))
        log._records = [second]  # type: ignore[attr-defined]
        self.assertFalse(log.verify_chain())

        log = AuditLog()
        first = log.append(make_record(action="first", capability="first"))
        second = log.append(make_record(action="second", capability="second"))
        log._records = [second, first]  # type: ignore[attr-defined]
        self.assertFalse(log.verify_chain())


if __name__ == "__main__":
    unittest.main()
