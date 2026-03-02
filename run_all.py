"""
One-command local development runner.

Starts:
- Backend FastAPI server on port 8000
- Frontend Vite dev server on port 3000
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000
FRONTEND_HOST = "0.0.0.0"
FRONTEND_PORT = 3000


def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _wait_for_url(url: str, timeout_sec: int = 60) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:  # nosec B310
                if 200 <= resp.status < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(1)
    return False


def _start_process(
    cmd: list[str],
    env: Optional[dict[str, str]] = None,
    cwd: Optional[Path] = None,
) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        env=env,
        cwd=str(cwd) if cwd else None,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def _stop_process(proc: Optional[subprocess.Popen], name: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=10)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
    print(f"[stopped] {name}")


def _resolve_npm() -> str:
    npm = shutil.which("npm")
    if npm:
        return npm
    raise RuntimeError("npm was not found in PATH. Install Node.js (includes npm).")


def main() -> int:
    project_root = Path(__file__).resolve().parent
    frontend_dir = project_root / "frontend"

    if not frontend_dir.exists():
        print("[error] frontend directory not found.")
        return 1

    if _is_port_in_use(BACKEND_PORT):
        print(f"[error] Port {BACKEND_PORT} is already in use.")
        return 1
    if _is_port_in_use(FRONTEND_PORT):
        print(f"[error] Port {FRONTEND_PORT} is already in use.")
        return 1

    npm_bin = _resolve_npm()

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
    ]

    frontend_env = os.environ.copy()
    frontend_env.setdefault("VITE_API_BASE_URL", f"http://localhost:{BACKEND_PORT}")
    frontend_cmd = [
        npm_bin,
        "run",
        "dev",
        "--",
        "--host",
        FRONTEND_HOST,
        "--port",
        str(FRONTEND_PORT),
    ]

    backend_proc: Optional[subprocess.Popen] = None
    frontend_proc: Optional[subprocess.Popen] = None
    try:
        print(f"[starting] Backend: {' '.join(backend_cmd)}")
        backend_proc = _start_process(backend_cmd, cwd=project_root)

        if not _wait_for_url(f"http://localhost:{BACKEND_PORT}/health", timeout_sec=60):
            raise RuntimeError("Backend did not become ready at /health within 60 seconds.")

        print(f"[starting] Frontend: {' '.join(frontend_cmd)}")
        frontend_proc = _start_process(frontend_cmd, env=frontend_env, cwd=frontend_dir)

        print("")
        print("Local dev stack is running:")
        print(f"- Backend health: http://localhost:{BACKEND_PORT}/health")
        print(f"- Backend models: http://localhost:{BACKEND_PORT}/api/v1/models")
        print(f"- Frontend: http://localhost:{FRONTEND_PORT}")
        print("")
        print("Frontend config:")
        print(f"- VITE_API_BASE_URL={frontend_env['VITE_API_BASE_URL']}")
        print("")
        print("Press Ctrl+C to stop both services.")

        while True:
            if backend_proc.poll() is not None:
                raise RuntimeError(f"Backend exited unexpectedly with code {backend_proc.returncode}.")
            if frontend_proc.poll() is not None:
                raise RuntimeError(f"Frontend exited unexpectedly with code {frontend_proc.returncode}.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[signal] Ctrl+C received. Shutting down...")
    except Exception as exc:
        print(f"[error] {exc}")
        return 1
    finally:
        _stop_process(frontend_proc, "frontend")
        _stop_process(backend_proc, "backend")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

