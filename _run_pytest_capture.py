import pathlib
import subprocess

result = subprocess.run(
    ["pytest", "-q", "tests/"],
    capture_output=True,
    text=True,
)

log_text = (result.stdout or "") + "\n" + (result.stderr or "")
pathlib.Path(".pytest_full.log").write_text(log_text, encoding="utf-8")

print(f"EXIT={result.returncode}")
print(f"STDOUT_LINES={len((result.stdout or '').splitlines())}")
print(f"STDERR_LINES={len((result.stderr or '').splitlines())}")
