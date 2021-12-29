import os
from pathlib import Path
import pytest


@pytest.fixture
def base_path() -> Path:
    """Get the current folder of the test"""
    return Path(__file__).parent.parent


def test_correct(base_path: Path, monkeypatch: pytest.MonkeyPatch, capfd):
    monkeypatch.chdir(base_path / "examples" / "judge" / "correct")
    returncode = os.system("judge")
    out, _ = capfd.readouterr()
    assert returncode == 0
    assert "100/100" in out


def test_wrong(base_path: Path, monkeypatch: pytest.MonkeyPatch, capfd):
    monkeypatch.chdir(base_path / "examples" / "judge" / "wrong")
    returncode = os.system("judge")
    out, _ = capfd.readouterr()
    assert returncode != 0
    assert "90/100" in out
