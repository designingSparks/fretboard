"""Build the player with Nuitka: python build_nuitka.py [--dry-run]."""

import argparse
import importlib.util
from importlib.metadata import version
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "build" / "nuitka"
WEB_FILES = ("fretboard.html", "main.js", "sequence_outlines.js", "chord_labels.js")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print the build command without compiling")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Use Python 3.11 or newer (the app uses tomllib).")

    lessons = sorted(p.stem for p in (ROOT / "lessons").glob("*.py")
                     if not p.name.startswith("_"))
    if "c_maj_triad" not in lessons:
        parser.error("The default lesson lessons/c_maj_triad.py is missing.")
    for resource in WEB_FILES:
        if not (ROOT / resource).is_file():
            parser.error(f"Missing resource: {resource}")
    for folder, pattern in (("clean", "*.wav"), ("icons", "*.svg")):
        if not any((ROOT / folder).glob(pattern)):
            parser.error(f"Missing resources: {folder}/{pattern}")

    manifest = OUTPUT / "bundled_lessons.json"
    command = [
        sys.executable, "-m", "nuitka",
        "--mode=app" if sys.platform == "darwin" else "--mode=standalone",
        "--enable-plugin=pyside6",
        "--include-qt-plugins=multimedia,iconengines",
        f"--output-dir={OUTPUT}",
        "--output-filename=Fretboard",
        f"--report={OUTPUT / 'compilation-report.xml'}",
        "--nofollow-import-to=main_export,tutorials,tutorials.*",
        "--noinclude-data-files=main_export.py",
        "--noinclude-data-files=tutorials/*",
        f"--include-data-files={manifest}=bundled_lessons.json",
        f"--include-data-files={ROOT / 'clean' / '*.wav'}=clean/",
        f"--include-data-files={ROOT / 'icons' / '*.svg'}=icons/",
    ]
    command.extend(f"--include-module=lessons.{name}" for name in lessons)
    command.extend(f"--include-data-files={ROOT / name}={name}" for name in WEB_FILES)
    if sys.platform == "darwin":
        command.append("--macos-app-name=Fretboard")
        icon = ROOT / "icon" / "icon.icns"
        if icon.is_file():
            command.append(f"--macos-app-icon={icon}")
    elif sys.platform == "win32":
        command.append("--windows-console-mode=disable")
    command.append(str(ROOT / "main.py"))

    print(shlex.join(command), flush=True)
    if args.dry_run:
        return 0
    missing = [name for name in ("nuitka", "PySide6", "numpy", "tomli_w")
               if importlib.util.find_spec(name) is None]
    if missing:
        parser.error("Missing " + ", ".join(missing)
                     + "; install requirements-build.txt with this Python interpreter.")
    nuitka_version = version("Nuitka")
    if tuple(int(part) for part in nuitka_version.split(".")[:2]) < (4, 1):
        parser.error(
            f"Nuitka {nuitka_version} is too old. Install requirements-build.txt "
            "with this Python interpreter; Nuitka 4.1 fixes duplicated Qt WebEngine "
            "libraries in macOS bundles."
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(lessons, indent=2) + "\n", encoding="utf-8")
    # Keep compiler caches inside the project, including in restricted environments.
    env = os.environ.copy()
    env.setdefault("NUITKA_CACHE_DIR", str(OUTPUT / "cache"))
    result = subprocess.call(command, cwd=ROOT, env=env)
    if result:
        return result
    if sys.platform == "darwin":
        bundle = OUTPUT / "main.app"
        # Seal the completed bundle and verify all nested code signatures.
        subprocess.check_call(["codesign", "--force", "--sign", "-", str(bundle)])
        subprocess.check_call(["codesign", "--verify", "--deep", "--strict", str(bundle)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
