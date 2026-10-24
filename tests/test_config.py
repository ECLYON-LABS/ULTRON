import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from eclipse.config import get_env
from eclipse.api.server import main, make_server
from eclipse.brain.model import CheckpointNotConfigured, LocalTransformersBackend
from eclipse.tools.sandbox import SandboxClient


SETTINGS = (
    "API_TOKEN", "MODEL_PATH", "HOST", "PORT", "MEMORY_DB_PATH",
    "EMBEDDING_MODEL_PATH", "MEMORY_SCOPE_ID", "ENABLE_WEB_RESEARCH",
    "ENABLE_SANDBOX_EXECUTION", "SANDBOX_URL", "SANDBOX_TOKEN",
    "READONLY_DATABASE_URL",
)


class ConfigTests(unittest.TestCase):
    def test_each_setting_supports_ultron_and_legacy_names(self):
        for suffix in SETTINGS:
            for prefix in ("ULTRON_", "PLUTO_", "ECLIPSE_"):
                with self.subTest(suffix=suffix, prefix=prefix):
                    with patch.dict(os.environ, {prefix + suffix: "test-value"}, clear=True):
                        self.assertEqual(get_env("PLUTO_" + suffix), "test-value")

    def test_pluto_wins_and_empty_values_do_not_restore_legacy_values(self):
        for suffix in SETTINGS:
            for value in ("pluto-value", "", "0"):
                with self.subTest(suffix=suffix, value=value):
                    with patch.dict(os.environ, {
                        "PLUTO_" + suffix: value,
                        "ECLIPSE_" + suffix: "legacy-value",
                    }, clear=True):
                        self.assertEqual(get_env("PLUTO_" + suffix, "default"), value)

    def test_ultron_wins_even_when_empty_for_all_supported_lookup_names(self):
        for suffix in SETTINGS:
            for value in ("ultron-value", "", "0"):
                for lookup_prefix in ("ULTRON_", "PLUTO_", "ECLIPSE_"):
                    with self.subTest(suffix=suffix, value=value, lookup=lookup_prefix):
                        with patch.dict(os.environ, {
                            "ULTRON_" + suffix: value,
                            "PLUTO_" + suffix: "pluto-value",
                            "ECLIPSE_" + suffix: "legacy-value",
                        }, clear=True):
                            self.assertEqual(get_env(lookup_prefix + suffix, "default"), value)

    def test_empty_ultron_token_does_not_restore_old_credentials(self):
        with patch.dict(os.environ, {
            "ULTRON_API_TOKEN": "",
            "PLUTO_API_TOKEN": "old-test-only-token-at-least-16",
            "ECLIPSE_API_TOKEN": "legacy-test-only-token-at-least-16",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "ULTRON_API_TOKEN"):
                make_server("127.0.0.1", 0, Mock(), get_env("ULTRON_API_TOKEN"))

    def test_unconfigured_defaults_and_canonical_name_requirement(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(get_env("PLUTO_API_TOKEN"))
            self.assertEqual(get_env("PLUTO_PORT", "8765"), "8765")
            with self.assertRaises(ValueError):
                get_env("UNRELATED_SETTING")

    def test_api_startup_reads_all_configuration_formats(self):
        for prefix in ("ULTRON_", "PLUTO_", "ECLIPSE_"):
            with self.subTest(prefix=prefix):
                settings = {prefix + "API_TOKEN": "test-only-token-at-least-16",
                            prefix + "HOST": "127.0.0.1", prefix + "PORT": "9876",
                            prefix + "ENABLE_WEB_RESEARCH": "0",
                            prefix + "ENABLE_SANDBOX_EXECUTION": "1"}
                backend, server = Mock(), Mock()
                server.server_port = 9876
                with patch.dict(os.environ, settings, clear=True), \
                        patch("eclipse.api.server.LocalTransformersBackend", return_value=backend), \
                        patch("eclipse.api.server.make_server", return_value=server) as factory, \
                        patch("builtins.print"):
                    main()
                factory.assert_called_once_with("127.0.0.1", 9876, backend,
                    "test-only-token-at-least-16", enable_web_research=False,
                    enable_sandbox_execution=True)
                server.serve_forever.assert_called_once()
                server.server_close.assert_called_once()

    def test_explicit_empty_new_api_token_fails_closed(self):
        with patch.dict(os.environ, {
            "PLUTO_API_TOKEN": "", "ECLIPSE_API_TOKEN": "legacy-test-token-at-least-16",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "ULTRON_API_TOKEN"):
                make_server("127.0.0.1", 0, Mock(), get_env("PLUTO_API_TOKEN"))

    def test_backend_uses_new_checkpoint_path_before_legacy_path(self):
        with tempfile.TemporaryDirectory() as directory:
            new_path = str(Path(directory) / "pluto-missing")
            with patch.dict(os.environ, {
                "PLUTO_MODEL_PATH": new_path,
                "ECLIPSE_MODEL_PATH": str(Path(directory) / "legacy-missing"),
            }, clear=True):
                with self.assertRaisesRegex(CheckpointNotConfigured, "pluto-missing"):
                    LocalTransformersBackend()

    def test_sandbox_reads_all_configuration_formats_without_a_request(self):
        for prefix in ("ULTRON_", "PLUTO_", "ECLIPSE_"):
            with self.subTest(prefix=prefix):
                with patch.dict(os.environ, {
                    prefix + "SANDBOX_URL": "https://sandbox.example",
                    prefix + "SANDBOX_TOKEN": "test-only-sandbox-token",
                }, clear=True):
                    client = SandboxClient()
                    self.assertEqual(client.endpoint, "https://sandbox.example")
                    self.assertEqual(client.token, "test-only-sandbox-token")


if __name__ == "__main__":
    unittest.main()
