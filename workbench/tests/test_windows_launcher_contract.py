"""Static contracts for the dependency-free Windows Workbench launcher."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "workbench" / "start.cmd"


class WindowsLauncherContractTests(unittest.TestCase):
    def setUp(self):
        self.source = LAUNCHER.read_text(encoding="utf-8")
        self.lines = [line.strip() for line in self.source.splitlines()]

    def test_automatic_runtime_install_is_disabled_before_launch_probes(self):
        guard = self.lines.index('set "PYTHON_MANAGER_AUTOMATIC_INSTALL=0"')
        python_probe = self.lines.index("where python >nul 2>nul")
        launcher_probe = self.lines.index("where py >nul 2>nul")
        self.assertLess(guard, python_probe)
        self.assertLess(guard, launcher_probe)
        self.assertNotIn('set "PYTHON_MANAGER_AUTOMATIC_INSTALL=1"', self.lines)

    def test_path_selected_python_precedes_launcher_fallback(self):
        python_probe = self.lines.index("where python >nul 2>nul")
        python_jump = self.lines.index("if not errorlevel 1 goto use_python")
        launcher_probe = self.lines.index("where py >nul 2>nul")
        launcher_jump = self.lines.index("if not errorlevel 1 goto use_py")
        self.assertLess(python_probe, python_jump)
        self.assertLess(python_jump, launcher_probe)
        self.assertLess(launcher_probe, launcher_jump)

    def test_both_routes_execute_the_same_reviewed_entrypoint(self):
        self.assertIn('python "%~dp0start.py" %*', self.lines)
        self.assertIn('python "%~dp0start.py" --open-browser', self.lines)
        self.assertIn('py -3 "%~dp0start.py" %*', self.lines)
        self.assertIn('py -3 "%~dp0start.py" --open-browser', self.lines)

    def test_launcher_never_installs_or_downloads_runtime_content(self):
        lowered = self.source.lower()
        for forbidden in (
            "pip install",
            "py install",
            "pymanager install",
            "powershell -command",
            "curl ",
            "wget ",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
