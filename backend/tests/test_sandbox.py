"""T1.5: subprocess sandbox — success, timeout kill, output cap, python, errors."""
import os

from app.core.sandbox import SandboxResult, run_python, run_shell


async def test_shell_success_echo():
    res = await run_shell("echo hello-sandbox")
    assert isinstance(res, SandboxResult)
    assert res.ok is True
    assert res.exit_code == 0
    assert res.timed_out is False
    assert res.stdout.strip() == "hello-sandbox"


async def test_shell_timeout_is_killed():
    res = await run_shell("sleep 5", timeout=0.3)
    assert res.timed_out is True
    assert res.ok is False


async def test_output_cap_truncates():
    # Emit far more than the cap; result must be truncated and bounded.
    res = await run_shell("yes x | head -c 100000", max_output_bytes=1024, timeout=10)
    assert res.truncated is True
    assert len(res.stdout.encode("utf-8")) <= 1024


async def test_python_code_runs():
    res = await run_python("print(2 + 2)")
    assert res.ok is True
    assert res.exit_code == 0
    assert res.stdout.strip() == "4"


async def test_failing_command_reports_error():
    res = await run_shell("exit 3")
    assert res.ok is False
    assert res.exit_code == 3


async def test_unknown_command_does_not_crash():
    res = await run_shell("this-binary-does-not-exist-xyz")
    assert res.ok is False
    assert res.exit_code != 0


async def test_env_is_scrubbed():
    # A host secret in the parent env must not leak into the child.
    os.environ["LOKYY_SECRET_TEST"] = "top-secret"
    try:
        res = await run_shell('echo "[${LOKYY_SECRET_TEST}]"')
    finally:
        os.environ.pop("LOKYY_SECRET_TEST", None)
    assert res.ok is True
    assert "top-secret" not in res.stdout
    assert res.stdout.strip() == "[]"


async def test_python_isolated_from_pythonpath():
    # python -I ignores PYTHONPATH; passing it as extra env must have no effect.
    res = await run_python(
        "import sys; print('inj' in ''.join(sys.path))",
        env={"PYTHONPATH": "/tmp/inj"},
    )
    assert res.ok is True
    assert res.stdout.strip() == "False"


async def test_empty_command_rejected():
    res = await run_shell("   ")
    assert res.ok is False
    assert "empty" in res.stderr
