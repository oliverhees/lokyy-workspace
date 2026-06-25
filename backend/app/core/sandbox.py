"""Sandboxed execution of shell commands and Python code (M1/T1.5, first stage).

This is **subprocess-based isolation**, not a real security sandbox. It provides
pragmatic, layered limits so the agent's shell/code tools cannot trivially run
forever, flood memory with output, or read inherited secrets:

- **Timeout** — the child is killed (process-group-wide) when it overruns.
- **Output cap** — stdout/stderr are truncated to a byte budget.
- **Isolated workdir** — execution happens in a fresh temp directory that is
  removed afterwards (unless an explicit ``cwd`` is supplied).
- **Scrubbed environment** — only a minimal allow-list of variables is passed
  through; API keys, tokens and other host secrets are never inherited.

What this DELIBERATELY does NOT do yet (planned next stages — odysseus had a gap
here that we close incrementally):

- No container isolation (Docker/Podman/gVisor) — a child can still touch the
  host filesystem outside its workdir and use host binaries.
- No network egress blocking — a child can still reach the network.
- No CPU/memory/PID rlimits on non-POSIX platforms.

Everything is async (``asyncio.create_subprocess_exec`` + ``wait_for``) so it
fits the FastAPI backend's async tool loop.
"""
from __future__ import annotations

import asyncio
import os
import shlex
import signal
import sys
import tempfile
from dataclasses import dataclass

# Default limits — conservative, overridable per call.
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_OUTPUT_BYTES = 64 * 1024

# Minimal environment allow-list. Anything not listed (and not added by the
# caller) is dropped so host secrets are never leaked into the child.
_ENV_ALLOWLIST = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ")


@dataclass
class SandboxResult:
    """Outcome of a sandboxed run."""

    ok: bool
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    truncated: bool


def _clean_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Build a scrubbed environment from the allow-list plus optional extras."""
    env = {k: os.environ[k] for k in _ENV_ALLOWLIST if k in os.environ}
    # Always provide a sane PATH so basic binaries resolve.
    env.setdefault("PATH", "/usr/local/bin:/usr/bin:/bin")
    env.setdefault("LANG", "C.UTF-8")
    if extra:
        env.update(extra)
    return env


def _truncate(data: bytes, limit: int) -> tuple[str, bool]:
    """Decode bytes (best-effort) and report whether they were truncated."""
    truncated = len(data) > limit
    if truncated:
        data = data[:limit]
    return data.decode("utf-8", errors="replace"), truncated


async def _run(
    argv: list[str],
    *,
    timeout: float,
    cwd: str | None,
    max_output_bytes: int,
    env: dict[str, str] | None = None,
) -> SandboxResult:
    """Core runner: spawn ``argv`` in its own process group with all limits applied."""
    owns_workdir = cwd is None
    workdir = cwd or tempfile.mkdtemp(prefix="lokyy-sbx-")

    # New session/process-group so a timeout kills the whole subtree, not just
    # the immediate child (POSIX only; start_new_session is a no-op elsewhere).
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=workdir,
            env=_clean_env(env),
            start_new_session=True,
        )
    except (FileNotFoundError, PermissionError, OSError) as exc:
        if owns_workdir:
            _cleanup_dir(workdir)
        return SandboxResult(
            ok=False,
            exit_code=None,
            stdout="",
            stderr=f"failed to launch: {exc}",
            timed_out=False,
            truncated=False,
        )

    timed_out = False
    try:
        out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        timed_out = True
        _kill_group(proc)
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        except asyncio.TimeoutError:
            out_b, err_b = b"", b""
    finally:
        if owns_workdir:
            _cleanup_dir(workdir)

    stdout, out_trunc = _truncate(out_b or b"", max_output_bytes)
    stderr, err_trunc = _truncate(err_b or b"", max_output_bytes)
    exit_code = proc.returncode
    ok = (not timed_out) and exit_code == 0

    return SandboxResult(
        ok=ok,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        truncated=out_trunc or err_trunc,
    )


def _kill_group(proc: asyncio.subprocess.Process) -> None:
    """Best-effort SIGKILL of the child's whole process group."""
    if proc.returncode is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except ProcessLookupError:
            pass


def _cleanup_dir(path: str) -> None:
    import shutil

    shutil.rmtree(path, ignore_errors=True)


async def run_shell(
    command: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    cwd: str | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    env: dict[str, str] | None = None,
) -> SandboxResult:
    """Run a shell-style ``command`` under subprocess isolation.

    The command is run via ``/bin/sh -c`` so pipes/redirects work as a user would
    expect from a shell tool. All sandbox limits apply.
    """
    if not command or not command.strip():
        return SandboxResult(
            ok=False,
            exit_code=None,
            stdout="",
            stderr="empty command",
            timed_out=False,
            truncated=False,
        )
    shell = "/bin/sh" if os.path.exists("/bin/sh") else "sh"
    argv = [shell, "-c", command]
    return await _run(
        argv,
        timeout=timeout,
        cwd=cwd,
        max_output_bytes=max_output_bytes,
        env=env,
    )


async def run_python(
    code: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    env: dict[str, str] | None = None,
) -> SandboxResult:
    """Run a snippet of ``code`` with the current Python interpreter, sandboxed.

    Uses ``python -I -c`` (isolated mode: ignores env-based site config and
    ``PYTHON*`` vars) inside a fresh temp workdir.
    """
    if code is None:
        return SandboxResult(
            ok=False,
            exit_code=None,
            stdout="",
            stderr="empty code",
            timed_out=False,
            truncated=False,
        )
    argv = [sys.executable, "-I", "-c", code]
    return await _run(
        argv,
        timeout=timeout,
        cwd=None,
        max_output_bytes=max_output_bytes,
        env=env,
    )


def quote_args(args: list[str]) -> str:
    """Helper: safely join args into a shell command string."""
    return " ".join(shlex.quote(a) for a in args)
