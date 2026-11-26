"""Run the entry twice and verify its format and determinism locally."""

from contextlib import ExitStack
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile


LINE_SEPARATORS = "\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029"


def verify() -> None:
    repo = Path(__file__).resolve().parent
    scratch = repo / ".verify"
    scratch.mkdir(exist_ok=True)
    results = []

    with ExitStack() as stack:
        for run in (1, 2):
            output_dir = Path(stack.enter_context(tempfile.TemporaryDirectory(
                prefix=f"run-{run}-", dir=scratch
            )))
            env = os.environ.copy()
            env["OUTPUT_DIR"] = str(output_dir)
            subprocess.run(
                [sys.executable, str(repo / "main.py")],
                cwd=repo,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            data = (output_dir / "entry.txt").read_bytes()
            line = data.decode("utf-8", errors="strict")
            if not 1 <= len(line) <= 200:
                raise ValueError(f"Run {run}: expected 1 to 200 characters.")
            if not line.strip():
                raise ValueError(f"Run {run}: entry is blank.")
            if line.endswith(("\n", "\r")):
                raise ValueError(f"Run {run}: trailing newline detected.")
            if any(char in LINE_SEPARATORS for char in line):
                raise ValueError(f"Run {run}: line separator detected.")
            if len(line.splitlines()) != 1:
                raise ValueError(f"Run {run}: expected exactly one line.")
            results.append(data)

    if results[0] != results[1]:
        raise ValueError("Runs produced different bytes.")

    print(f"PASS: UTF-8, {len(results[0].decode('utf-8'))} characters, one non-blank line,")
    print("no trailing newline, and byte-identical output across two fresh runs.")
    for run, data in enumerate(results, start=1):
        print(f"Run {run} SHA-256: {hashlib.sha256(data).hexdigest()}")


def main() -> int:
    try:
        verify()
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
