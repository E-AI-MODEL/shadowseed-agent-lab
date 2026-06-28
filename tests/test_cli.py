from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
import unittest

from shadowseed_agent_lab.cli import main, run_fixture_loop


class CliTests(unittest.TestCase):
    def test_fixture_loop_is_safe_and_promotes_some_seeds(self) -> None:
        result = run_fixture_loop()

        self.assertTrue(result.safe)
        self.assertTrue(result.audit.ok)
        self.assertTrue(result.promoted_seed_ids)
        # Every promoted session must carry a probe suggestion; no weightless one may.
        for session in result.sessions:
            if session.gate_event.promoted:
                self.assertIsNotNone(session.probe_suggestion)
            else:
                self.assertIsNone(session.probe_suggestion)

    def test_main_text_mode_exits_zero(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main([])

        self.assertEqual(code, 0)
        self.assertIn("safe=True", buffer.getvalue())

    def test_main_json_mode_is_parseable(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--json"])

        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(payload["safe"])
        self.assertTrue(payload["audit_ok"])
        self.assertIn("decisions", payload)


if __name__ == "__main__":
    unittest.main()
