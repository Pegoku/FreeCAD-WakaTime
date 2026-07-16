import os
import tempfile
import unittest
from pathlib import Path

from freecad.Wakatime.scripts.logWaka import resolve_wakatime_cli


class ResolveWakatimeCliTests(unittest.TestCase):
    def test_configured_path_has_priority(self):
        cli = resolve_wakatime_cli(
            configured_path="/custom/bin/wakatime",
            system="Linux",
            home="/home/test",
            path_lookup=lambda _name: "/usr/bin/wakatime",
        )

        self.assertEqual(cli, "/custom/bin/wakatime")

    def test_finds_user_local_linux_install(self):
        with tempfile.TemporaryDirectory() as home:
            cli = Path(home, ".local", "bin", "wakatime")
            cli.parent.mkdir(parents=True)
            cli.touch()

            resolved = resolve_wakatime_cli(
                system="Linux", home=home, path_lookup=lambda _name: None
            )

        self.assertEqual(resolved, os.fspath(cli))

    def test_finds_cli_on_path(self):
        def lookup(name):
            return "/usr/bin/wakatime" if name == "wakatime" else None

        cli = resolve_wakatime_cli(
            system="Linux", home="/home/test", path_lookup=lookup
        )

        self.assertEqual(cli, "/usr/bin/wakatime")

    def test_uses_legacy_path_as_install_fallback(self):
        cli = resolve_wakatime_cli(
            system="Linux", home="/home/test", path_lookup=lambda _name: None
        )

        self.assertEqual(cli, "/home/test/wakatime/wakatime")


if __name__ == "__main__":
    unittest.main()
