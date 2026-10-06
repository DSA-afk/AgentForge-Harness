"""Regression tests for damaged transcripts and uncertain tool outcomes."""

import json
import tempfile
import unittest
from pathlib import Path

from agentforge_harness.transcript import load_messages


class TranscriptRecoveryTests(unittest.TestCase):
    def read_entries(self, entries, tail=""):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text(
                "".join(json.dumps(entry) + "\n" for entry in entries) + tail,
                encoding="utf-8",
            )
            return load_messages(path)

    def test_invalid_record_shapes_do_not_hide_later_messages(self):
        messages = self.read_entries([
            None, 42, "unexpected", [],
            {"type": "user", "message": "invalid body"},
            {"type": "assistant", "message": ["invalid body"]},
            {"type": "user", "message": {"content": "still recoverable"}},
        ], tail='{"type":')
        self.assertEqual([message.text() for message in messages], ["still recoverable"])

    def test_missing_result_does_not_claim_a_side_effect_never_happened(self):
        messages = self.read_entries([
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "write-1", "name": "Write",
                 "input": {"file_path": "report.txt", "content": "done"}}
            ]}}
        ])
        result = messages[1].blocks()[0]
        self.assertEqual(result["tool_use_id"], "write-1")
        self.assertTrue(result["is_error"])
        self.assertIn("execution outcome is unknown", result["content"])
        self.assertIn("Verify", result["content"])
        self.assertNotIn("before this tool ran", result["content"])

    def test_recorded_results_are_preserved(self):
        result = {"type": "tool_result", "tool_use_id": "read-1", "content": "known"}
        messages = self.read_entries([
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "read-1", "name": "Read", "input": {}}
            ]}},
            {"type": "user", "message": {"content": [result]}},
        ])
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[1].blocks(), [result])

    def test_compaction_discards_only_earlier_history(self):
        messages = self.read_entries([
            {"type": "user", "message": {"content": "old"}},
            {"type": "user", "message": {"content": "summary"}, "isCompactSummary": True},
            {"type": "assistant", "message": {"content": "continued"}},
        ])
        self.assertEqual([message.text() for message in messages], ["summary", "continued"])


if __name__ == "__main__":
    unittest.main()
