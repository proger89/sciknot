from __future__ import annotations

import argparse
import subprocess
import sys


def run(command: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return completed.returncode, (completed.stdout + completed.stderr)[-1200:]
    except Exception as exc:
        return 1, f"{exc.__class__.__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefer", default="docker")
    parser.add_argument("--fallback", default="streamlit")
    parser.add_argument("--url", default="http://localhost:8501")
    args = parser.parse_args()

    selected = "not_started"
    if args.prefer == "docker":
        code, output = run(["docker", "compose", "config"], timeout=30)
        if code == 0:
            selected = "docker_config_ok"
            print("smoke_launch_paths: docker compose config ok")
            return 0
        print(f"smoke_launch_paths: docker unavailable, fallback allowed. tail={output}")

    code, output = run([sys.executable, "scripts/smoke_streamlit.py"], timeout=30)
    selected = "local_streamlit_static_smoke" if code == 0 else "failed"
    print(f"smoke_launch_paths: selected={selected} url={args.url}")
    if output:
        print(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

