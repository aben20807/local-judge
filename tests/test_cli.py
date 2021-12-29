from pathlib import Path
from typing import Tuple
import pytest
import subprocess


def exec_command(cmd: str) -> Tuple[str, str, int]:
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    return process.stdout, process.stderr, process.returncode


@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test"""
    return Path(__file__).parent.parent


def test_judge_correct(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path / "examples" / "judge" / "correct")
    out, _, returncode = exec_command("judge")
    assert returncode == 0
    assert "100/100" in out


def test_judge_wrong(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path / "examples" / "judge" / "wrong")
    out, _, returncode = exec_command("judge")
    assert returncode != 0
    assert "90/100" in out


def test_ta_judge(base_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(base_path / "examples" / "ta_judge")
    out, _, returncode = exec_command("ta_judge")
    assert returncode == 0
    assert "OU2345678" in out
    assert "F12345678" in out
    assert "Finished" in out
