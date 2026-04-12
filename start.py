import signal
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def _resolve_executable(name: str) -> str | None:
    candidates = [name]
    if sys.platform == "win32":
        candidates = [name, f"{name}.cmd", f"{name}.exe"]

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _start_process(command: list[str], cwd: Path, name: str) -> subprocess.Popen:
    resolved = _resolve_executable(command[0])
    if not resolved:
        raise RuntimeError(
            f"Failed to start {name}: executable not found: {command[0]!r}. "
            "Please ensure it is installed and available in PATH."
        )
    command = [resolved, *command[1:]]

    try:
        return subprocess.Popen(command, cwd=cwd)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Failed to start {name}: {exc}") from exc


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def _stop_services(frontend: subprocess.Popen | None, backend: subprocess.Popen | None) -> None:
    if frontend is not None:
        _stop_process(frontend)
    if backend is not None:
        _stop_process(backend)


def main() -> int:
    backend = None
    frontend = None
    stop_requested = threading.Event()

    def _handle_sigterm(_signum, _frame):
        stop_requested.set()

    signal.signal(signal.SIGTERM, _handle_sigterm)
    signal.signal(signal.SIGINT, _handle_sigterm)

    try:
        backend = _start_process([sys.executable, "main.py"], BACKEND_DIR, "backend")
        frontend = _start_process(["npm", "run", "dev", "--", "--open"], FRONTEND_DIR, "frontend")

        while True:
            if stop_requested.is_set():
                raise KeyboardInterrupt

            backend_code = backend.poll()
            frontend_code = frontend.poll()

            if backend_code is not None:
                print(f"Backend exited with code {backend_code}. Stopping frontend...")
                _stop_process(frontend)
                return backend_code

            if frontend_code is not None:
                print(f"Frontend exited with code {frontend_code}. Stopping backend...")
                _stop_process(backend)
                return frontend_code

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        _stop_services(frontend, backend)
        return 0
    except RuntimeError as exc:
        print(exc)
        _stop_services(frontend, backend)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
